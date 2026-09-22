import csv
import datetime
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def fetch_aaa_prices():
    with sync_playwright() as p:
        # Launch real headless Chrome browser inside GitHub Action
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        print("Opening AAA Gas Prices in Chrome...")
        page.goto("https://gasprices.aaa.com/", wait_until="domcontentloaded", timeout=60000)
        
        # Wait for table element to render in the DOM
        page.wait_for_selector("table", timeout=20000)
        html = page.content()
        browser.close()
        
    soup = BeautifulSoup(html, "html.parser")
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

if __name__ == "__main__":
    today = datetime.date.today().strftime("%Y-%m-%d")
    reg_price, diesel_price = fetch_aaa_prices()
    print(f"Scraped Data -> Date: {today}, Regular: ${reg_price}, Diesel: ${diesel_price}")
    
    if reg_price and diesel_price:
        with open("aaa_fuel_prices.csv", mode="a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([today, reg_price, diesel_price])
        print("Successfully updated aaa_fuel_prices.csv")
    else:
        raise ValueError("Could not extract gas prices from rendered page.")
