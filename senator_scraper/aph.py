# app/scrapers/aph_senators_csv.py
import argparse
import csv
import random
import re
import time
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlencode
import urllib.robotparser as robotparser

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE = "https://www.aph.gov.au"
SEARCH_URL = f"{BASE}/Senators_and_Members/Parliamentarian_Search_Results"  # ?sen=1&sta=WA
ROBOTS_URL = f"{BASE}/robots.txt"
UA = "CITS5206-Group6/1.0 (+contact: your-email@example.com)"

# ---------- HTTP session with retries ----------
def make_session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": UA})
    retries = Retry(
        total=3, backoff_factor=0.6,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    s.mount("https://", HTTPAdapter(max_retries=retries))
    return s

# ---------- robots.txt ----------
def allowed_by_robots(url: str, user_agent: str = UA) -> bool:
    rp = robotparser.RobotFileParser()
    try:
        rp.set_url(ROBOTS_URL)
        rp.read()
        return rp.can_fetch(user_agent, url)
    except Exception:
        # If robots can't be read, fail safe: only allow Senators_and_Members subtree
        return url.startswith(f"{BASE}/Senators_and_Members/")

# ---------- dataclass ----------
@dataclass
class SenatorRow:
    name: str
    profile_url: str
    party: Optional[str] = None
    state: Optional[str] = None
    phones: Optional[str] = None
    emails: Optional[str] = None
    postal_address: Optional[str] = None
    source_url: Optional[str] = None

# ---------- util ----------
def polite_sleep(a: float = 0.6, b: float = 2.0):
    time.sleep(random.uniform(a, b))

def extract_text_after_heading(soup: BeautifulSoup, labels: List[str]) -> Optional[str]:
    """Find text that follows a labeled heading/term on the page."""
    for tag in soup.find_all(["h2", "h3", "strong", "dt"]):
        label = tag.get_text(" ", strip=True).lower()
        for wanted in labels:
            if wanted.lower() in label:
                sib = tag.find_next_sibling()
                if sib and hasattr(sib, "get_text"):
                    val = sib.get_text(" ", strip=True)
                    if val:
                        return val
    return None

# ---------- parsing ----------
def parse_search_results(html: str) -> List[Dict[str, str]]:
    """
    Extract (name, profile link) pairs from the search results page.
    We look for anchors that link to /Parliamentarian?MPID=...
    """
    soup = BeautifulSoup(html, "lxml")
    out = []
    for a in soup.select("a[href*='Parliamentarian?MPID=']"):
        name = a.get_text(" ", strip=True)
        href = a.get("href") or ""
        if not name or not href:
            continue
        full = urljoin(BASE, href)
        out.append({"name": name, "href": full})
    # De-duplicate by href
    seen, uniq = set(), []
    for r in out:
        if r["href"] not in seen:
            uniq.append(r)
            seen.add(r["href"])
    return uniq

def parse_profile(html: str) -> Dict[str, Optional[str]]:
    soup = BeautifulSoup(html, "lxml")
    text = soup.get_text("\n", strip=True)

    # party & state/territory
    party = extract_text_after_heading(soup, ["Party"])
    st = extract_text_after_heading(soup, ["State/Territory", "State and Territory"])

    # phones from tel: links (preferred), fallback to regex
    phones = set()
    for tel in soup.select("a[href^='tel:']"):
        num = (tel.get("href") or "").replace("tel:", "").strip()
        if num:
            phones.add(num)
    if not phones:
        # very simple AU-ish phone pattern fallback
        for m in re.findall(r"\(?\d{1,4}\)?[\s-]?\d{3,4}[\s-]?\d{3,4}", text):
            phones.add(m)
    phones_str = "; ".join(sorted(phones)) if phones else None

    # emails via mailto: links (if present)
    emails = set()
    for em in soup.select("a[href^='mailto:']"):
        addr = (em.get("href") or "").replace("mailto:", "").strip()
        if addr and "@" in addr:
            emails.add(addr)
    emails_str = "; ".join(sorted(emails)) if emails else None

    # postal address: try several labels
    postal = extract_text_after_heading(
        soup,
        ["Postal address", "Parliament House address", "Office address", "Electorate Office"]
    )

    return {"party": party, "state": st, "phones": phones_str, "emails": emails_str, "postal_address": postal}

# ---------- core scrape ----------
def fetch_senators(state: Optional[str] = None, limit: Optional[int] = 50) -> List[SenatorRow]:
    """
    Scrape senators from APH search results (optionally filter by state),
    then follow each profile to extract details.
    """
    session = make_session()

    # Build search query
    params = {"sen": 1}
    if state:
        params["sta"] = state.upper()

    url = SEARCH_URL + "?" + urlencode(params)
    if not allowed_by_robots(url):
        raise PermissionError(f"Blocked by robots.txt: {url}")

    polite_sleep()
    r = session.get(url, timeout=20)
    r.raise_for_status()

    pairs = parse_search_results(r.text)
    if limit is not None and len(pairs) > limit:
        pairs = pairs[:limit]

    rows: List[SenatorRow] = []
    for p in pairs:
        profile_url = p["href"]
        if not allowed_by_robots(profile_url):
            # Skip disallowed (shouldn't happen for Senators_and_Members, but be safe)
            continue

        polite_sleep()
        pr = session.get(profile_url, timeout=20)
        pr.raise_for_status()

        details = parse_profile(pr.text)
        rows.append(SenatorRow(
            name=p["name"],
            profile_url=profile_url,
            party=details.get("party"),
            state=details.get("state"),
            phones=details.get("phones"),
            emails=details.get("emails"),
            postal_address=details.get("postal_address"),
            source_url=profile_url
        ))
    return rows

def export_csv(rows: List[SenatorRow], path: str) -> str:
    fieldnames = ["name", "party", "state", "phones", "emails", "postal_address", "profile_url", "source_url"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow(asdict(row))
    return path

# ---------- CLI ----------
def main():
    ap = argparse.ArgumentParser(description="Scrape Australian Senators into CSV")
    ap.add_argument("--state", help="State code (e.g., WA, NSW, VIC). If omitted, fetch all (first 50 by default).")
    ap.add_argument("--out", default="senators.csv", help="Output CSV path")
    ap.add_argument("--limit", type=int, default=50, help="Max records to fetch (protective cap)")
    args = ap.parse_args()

    rows = fetch_senators(state=args.state, limit=args.limit)
    p = export_csv(rows, args.out)
    print(f"Saved {len(rows)} rows → {p}")

if __name__ == "__main__":
    main()
