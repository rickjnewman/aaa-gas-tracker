import csv
import datetime
import re
from curl_cffi import requests
from bs4 import BeautifulSoup

def parse_prices_from_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    regular, diesel = "", ""
    table = soup.find("table")
    if table:
        for row in table.find_all("tr"):
            cols = [td.text.strip().replace("$", "") for td in row.find_all(["td", "th"])]
            if len(cols) >= 2:
                label = cols[0].lower()
                if "regular" in label and not regular:
                    regular = cols[1]
                elif "diesel" in label and not diesel:
                    diesel = cols[1]
    return regular, diesel

def parse_prices_from_text(text_content):
    reg_match = re.search(r"Regular.*?\$\s*([0-9]+\.[0-9]{2,4})", text_content, re.IGNORECASE)
    diesel_match = re.search(r"Diesel.*?\$\s*([0-9]+\.[0-9]{2,4})", text_content, re.IGNORECASE)
    regular = reg_match.group(1) if reg_match else ""
    diesel = diesel_match.group(1) if diesel_match else ""
    return regular, diesel

def fetch_aaa():
    # 1. Direct fetch attempt
    for url in ["https://gasprices.aaa.com/", "https://gasprices.aaa.com/?state=US"]:
        try:
            resp = requests.get(url, impersonate="chrome120", timeout=15)
            if resp.status_code == 200:
                reg, dies = parse_prices_from_html(resp.text)
                if reg and dies:
                    return reg, dies
        except Exception as e:
            print(f"Direct fetch failed: {e}")

    # 2. Proxy fallback for Cloudflare datacenter IP blocks
    try:
        print("Direct fetch blocked; attempting proxy fallback...")
        proxy_url = "https://r.jina.ai/https://gasprices.aaa.com/"
        resp = requests.get(proxy_url, impersonate="chrome120", timeout=20)
        if resp.status_code == 200:
            reg, dies = parse_prices_from_text(resp.text)
            if not (reg and dies):
                reg, dies = parse_prices_from_html(resp.text)
            if reg and dies:
                return reg, dies
    except Exception as e:
        print(f"Proxy fetch failed: {e}")

    return "", ""

if __name__ == "__main__":
    today = datetime.date.today().strftime("%Y-%m-%d")
    reg_price, diesel_price = fetch_aaa()
    
    if reg_price and diesel_price:
        with open("aaa_fuel_prices.csv", mode="a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([today, reg_price, diesel_price])
        print(f"Successfully logged: {today} -> Regular: ${reg_price}, Diesel: ${diesel_price}")
    else:
        print("Warning: Unable to fetch AAA prices today. Skipping entry to avoid corrupting CSV.")
