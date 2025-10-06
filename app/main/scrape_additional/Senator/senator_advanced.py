import random, re, time, json
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
from urllib.parse import urlencode
import urllib.robotparser as robotparser
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE = "https://www.aph.gov.au"
SEARCH_PATH = "/Senators_and_Members/Parliamentarian_Search_Results"
ROBOTS_URL = f"{BASE}/robots.txt"
UA = "Perth USAsia Centre/1.0 (+contact: lisa.cluett@perthusasia.edu.au)"


def make_session():
    s = requests.Session()
    s.headers.update({"User-Agent": UA})
    retries = Retry(
        total=3, backoff_factor=0.6,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    s.mount("https://", HTTPAdapter(max_retries=retries))
    return s


def allowed_by_robots(url: str, user_agent: str = UA) -> bool:
    rp = robotparser.RobotFileParser()
    try:
        rp.set_url(ROBOTS_URL)
        rp.read()
        return rp.can_fetch(user_agent, url)
    except Exception:
        return url.startswith(f"{BASE}/Senators_and_Members/")


@dataclass
class SenatorRow:
    first_name: str
    last_name: str
    profile_url: str
    sector: str
    party: Optional[str] = None
    state: Optional[str] = None
    phones: Optional[str] = None
    emails: Optional[str] = None
    postal_address: Optional[str] = None
    source_url: Optional[str] = None


def polite_sleep(a: float = 0.3, b: float = 1.0):
    time.sleep(random.uniform(a, b))


def parse_search_results(html: str) -> List[Dict[str, str]]:
    soup = BeautifulSoup(html, "lxml")
    out = []
    for a in soup.select("a[href*='Parliamentarian?MPID=']"):
        name = a.get_text(" ", strip=True)
        href = a.get("href") or ""
        if not name or not href:
            continue
        full = requests.compat.urljoin(BASE, href)
        out.append({"name": name, "href": full})
    seen = set()
    uniq = []
    for r in out:
        if r["href"] not in seen:
            uniq.append(r)
            seen.add(r["href"])
    return uniq


def parse_profile(html: str) -> Dict[str, Optional[str]]:
    soup = BeautifulSoup(html, "lxml")
    text = soup.get_text("\n", strip=True)

    def extract_text_after_heading(labels):
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

    party = extract_text_after_heading(["Party"])
    state = extract_text_after_heading(["State/Territory", "State and Territory"])

    phones = []
    for tel in soup.select("a[href^='tel:']"):
        num = (tel.get("href") or "").replace("tel:", "").strip()
        if num:
            phones.append(num)
    if not phones:
        for m in re.findall(r"\(?\d{1,4}\)?[\s-]?\d{3,4}[\s-]?\d{3,4}", text):
            phones.append(m)
    
    phones_str = phones[0] if phones else None

    emails = set()
    for em in soup.select("a[href^='mailto:']"):
        addr = (em.get("href") or "").replace("mailto:", "").strip()
        if addr and "@" in addr:
            emails.add(addr)
    emails_str = "; ".join(sorted(emails)) if emails else None

    postal = extract_text_after_heading(
        ["Postal address", "Parliament House address", "Office address", "Electorate Office"]
    )

    return {
        "party": party,
        "state": state,
        "phones": phones_str,
        "emails": emails_str,
        "postal_address": postal
    }


def fetch_profile(session, p, sector: str):
    profile_url = p["href"]
    if not allowed_by_robots(profile_url):
        return None

    polite_sleep()
    pr = session.get(profile_url, timeout=20)
    pr.raise_for_status()

    details = parse_profile(pr.text)

    parts = p["name"].split()
    first_name = parts[1] if len(parts) > 1 else ""
    last_name = parts[2] if len(parts) > 2 else ""

    return SenatorRow(
        first_name=first_name,
        last_name=last_name,
        profile_url=profile_url,
        sector=sector,
        party=details.get("party"),
        state=details.get("state"),
        phones=details.get("phones"),
        emails=details.get("emails"),
        postal_address=details.get("postal_address"),
        source_url=profile_url
    )


def fetch_senators_combined(limit: Optional[int] = None, max_workers: int = 8) -> List[Dict]:
    """
    Fetch both House of Representatives (mem=1) and Senators (sen=1)
    """
    session = make_session()
    rows: List[SenatorRow] = []

    for sector_type in [("House of Representatives", {"mem": 1, "par": -1, "gen": 0, "ps": 12}),
                        ("Senator", {"sen": 1, "par": -1, "gen": 0, "ps": 12})]:

        sector_name, base_params = sector_type
        max_pages = 13 if sector_name == "House of Representatives" else 7

        for page in range(1, max_pages + 1):
            params = {"page": page, **base_params}
            url = BASE + SEARCH_PATH + "?" + urlencode(params)
            print(f"Fetching page {page} of {sector_name}: {url}")

            if not allowed_by_robots(url):
                print("Blocked by robots for URL:", url)
                continue

            polite_sleep()
            resp = session.get(url, timeout=20)
            resp.raise_for_status()

            pairs = parse_search_results(resp.text)

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {executor.submit(fetch_profile, session, p, sector_name): p for p in pairs}
                for future in as_completed(futures):
                    try:
                        row = future.result()
                        if row:
                            rows.append(row)
                            if limit and len(rows) >= limit:
                                return [asdict(r) for r in rows]
                    except Exception as e:
                        print("Error fetching profile:", e)

    return [asdict(r) for r in rows]


def main():
    rows_json = fetch_senators_combined(limit=None, max_workers=10)
    print(json.dumps(rows_json, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()