from unittest.mock import patch
from bs4 import BeautifulSoup
from requests.compat import urljoin

def scrapeListing(url: str, soup: BeautifulSoup, extractorFns: list) -> object:
    """
    Scrapes a listing.
    """
    listingFields = {}
    for extractorFn in extractorFns:
        fieldName, fieldValue = extractorFn(url, soup)
        listingFields[fieldName] = fieldValue
    return listingFields

def scrapeListings(baseUrl: str, soup: BeautifulSoup) -> list:
    """
    Scrapes all listing urls from page soup.
    """

    els = soup.select("a[href].company-title-link")
    if els.__sizeof__() <= 0:
        return []
    
    out = []
    for el in els:
        path = el.get("href")
        url = urljoin(baseUrl, path)
        out.append(url)
    return out
