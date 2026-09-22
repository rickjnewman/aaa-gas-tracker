import csv
import datetime
import requests
from bs4 import BeautifulSoup

URL = "https://gasprices.aaa.com/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

def fetch_aaa():
    try:
        response = requests.get(URL, headers=HEADERS, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"HTTP Error: {e}")
        return None, "", ""
    
    soup = BeautifulSoup(response.text, "html.parser")
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

    today = datetime.date.today().strftime("%Y-%m-%d")
    return today, regular, diesel

if __name__ == "__main__":
    date_str, reg_price, diesel_price = fetch_aaa()
    
    if reg_price and diesel_price:
        with open("aaa_fuel_prices.csv", mode="a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([date_str, reg_price, diesel_price])
        print(f"Logged: {date_str} -> Regular: ${reg_price}, Diesel: ${diesel_price}")
    else:
        raise ValueError("Unable to parse price table from AAA website.")
