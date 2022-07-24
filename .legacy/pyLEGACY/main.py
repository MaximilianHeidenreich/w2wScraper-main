import os
from scraper import scrape_all_listings

if __name__ == "__main__":
    # Setup env
    if not os.path.exists("./out"):
        os.makedirs("./out")
    
    # Setup configuration
    BASE_URL = "https://www.wlw.de/"
    scrape_all_listings