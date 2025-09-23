import requests
from bs4 import BeautifulSoup

def scrape_https_proxies(url="https://free-proxy-list.net/en/"):
    """
    Scrape the proxy list table from free-proxy-list.net and return IPs that support HTTPS.
    Returns:
        List of strings in the format 'ip:port' for proxies with HTTPS support.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
    }
    
    try:
        # Fetch the webpage
        print(f"Fetching {url}...")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an error for bad status codes
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the proxy list table
        table = soup.find('table', class_='table table-striped table-bordered')
        if not table:
            print("Error: Could not find proxy table on the page.")
            return []
        
        # Extract table rows
        rows = table.find_all('tr')[1:]  # Skip header row
        https_proxies = []
        
        # Iterate through rows
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 7:  # Ensure row has enough columns
                ip = cols[0].text.strip()
                port = cols[1].text.strip()
                https = cols[6].text.strip().lower()
                
                # Check if proxy supports HTTPS
                if https == 'yes':
                    proxy = f"{ip}:{port}"
                    https_proxies.append(proxy)
                    print(f"Found HTTPS proxy: {proxy}")
        
        print(f"Total HTTPS proxies found: {len(https_proxies)}")
        return https_proxies
    
    except Exception as e:
        print(f"Error scraping proxy list: {e}")
        return []