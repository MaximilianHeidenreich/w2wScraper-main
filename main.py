from sys import exit
import os
import time
import urllib.parse
from datetime import datetime
import csv
from typing import Tuple
from tqdm import tqdm

from fetcher import fetcher
from transformers import stripOuterWhitespace
from scrapers import scrapeListing, scrapeListings
from extractors import *

# UTILS
def sPrint(str: str):
    tqdm.write(str)
def csvEscape(str: str) -> str:
    """
    Escapes a string for CSV.
    """
    return str.replace("\"", "'")
def getQueryString() -> str:
    """
    Returns the query string.
    """
    if not QUERY["q"]:
        print("ERR: No query string provided!")
        exit(1)
    return urllib.parse.urlencode(QUERY)

# Setup env
if not os.path.exists(os.path.join(os.getcwd(), "out")):
    os.makedirs(os.path.join(os.getcwd(), "out"))


# Global CONFIG
DEBUG_OUT                   = True  # Print addition extraction info

QUERY                       = {
    "q": "software",
    #"supplierTypes": "Großhändler",
    #"employeeCounts": "200+",          # Special chars are escaped automatically!
}

CSV_OUT_NAME                = "./out/wlw_{}_{}.csv".format(getQueryString(), datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
CSV_DELIMITER               = ","
CSV_EXCEL_HEADER            = False # !! Might break special characters when used ! Adds "SEP={delimiter}" to the out file -> Excel can display it with correct formatting
ERROR_OUT_NAME                = "./out/wlw_{}_{}.error.txt".format(getQueryString(), datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))

PAGINATION_URL_TEMPLATE     = "https://www.wlw.de/de/suche?{query}"
PAGE_TEMPLATE_URL           = "https://www.wlw.de/de/suche/page/{pageIndex}?{query}"
PAGE_START_INDEX            = 1
PAGE_SCRAPE_DELAY           = 0   # Delay for scraping pages (SECONDS) -> Could increase scraping success

# The extractor functions -> Fields to extract from listing pages
EXTRACTOR_FUNCTIONS = [
    extractBusinessName,
    extractBusinessAddress,
    extractBusinessPhone,
    extractBusinessWebsite,
    #extractBusinessDescription,
    extractEstablished,
    extractEmployeeCount,
    extractLocation,
    #extractKeyFigures,
    extractContactDetails
]

# Gloabl STATE
CWD             = os.getcwd()
ISSUE_PAGES     = []    # Some pages cannot be scraped on first try -> Try rescraping them at the end
LISTING_FIELDS  = []

# Setup error file
ERR_FILE = open(os.path.join(CWD, ERROR_OUT_NAME), "w+", buffering=1, encoding="UTF-8")

# Handle pagination & listingsCnt
sPrint("> Fetching pagination...")
print(PAGINATION_URL_TEMPLATE.format(query=getQueryString()))
paginationSoup = fetcher(PAGINATION_URL_TEMPLATE.format(query=getQueryString()))
paginationEls = paginationSoup.select(".pagination > :nth-last-child(2)")
if paginationEls.__sizeof__() <= 0:
    sPrint("ERR: Pagination could not be extracted!")
    exit(1)

try:
    pageEndIndex = int(stripOuterWhitespace(paginationEls[0].text))
    #pageEndIndex = 23    # TODO!: REMOVE DEBUG ONLY
except ValueError:
    sPrint("ERR: Pagination value is not Integer: {}".format(paginationEls[0].text))
    exit(1)

listingsCntEls = paginationSoup.select("a.search-tabs-supplier-link")
if listingsCntEls.__sizeof__() <= 0:
    sPrint("ERR: Listings count could not be extracted!")
    exit(1)

try:
    listingsCnt = int(stripOuterWhitespace(listingsCntEls[0].text.split(" ")[0]))
except ValueError:
    sPrint("ERR: Listings count value is not Integer: {}".format(listingsCntEls[0].text))
    exit(1)

sPrint("=> Pagination: {} - {} / {} listings".format(PAGE_START_INDEX, pageEndIndex, listingsCnt))

PAGES_PROGRESS = tqdm(desc="Pages", total=pageEndIndex)
LISTINGS_PROGRESS = tqdm(desc="Listings", total=listingsCnt)

def handleListing(url: str) -> list:
    """
    Handles a single listing.
    """
    global LISTINGS_PROGRESS
    # Fetch page
    sPrint("> Fetching listing page {} ...".format(url))
    pageSoup = fetcher(url)
    listingFields = scrapeListing(url, pageSoup, EXTRACTOR_FUNCTIONS)
    sPrint("> Scraped {} fields from listing page {}".format(len(listingFields), url))

    if DEBUG_OUT:
        for key in listingFields:
            sPrint("{}: {}".format(key, listingFields[key]))

    LISTINGS_PROGRESS.update(1)
    return listingFields


def handlePage(url: str) -> Tuple[int, list]:
    """
    Handles a single page.
    """
    global LISTINGS_PROGRESS

    # Fetch page
    sPrint("> Fetching page {} ...".format(url))
    pageSoup = fetcher(url)
    listingUrls = scrapeListings(url, pageSoup)
    if len(listingUrls) <= 0:
        return 0, []
    
    sPrint("> Found {} listings on page {}".format(len(listingUrls), url))

    extractedFields = []

    for listingUrl in listingUrls:
        listingFields = handleListing(listingUrl)
        extractedFields.append({ "url": listingUrl, "fields": listingFields })
    return len(listingUrls), extractedFields

def handlePageUrl(url: str):
    global LISTING_FIELDS
    global PAGES_PROGRESS
    global ISSUE_PAGES
    global PAGE_SCRAPE_DELAY
    global ERR_FILE

    try:
        listingsCnt, listingFields = handlePage(url)
        if listingsCnt <= 0:
            sPrint("WARN: No listings found on page {} -> Rescraping later".format(url))
            ISSUE_PAGES.append(url)
            return None
        
        PAGES_PROGRESS.update(1)
        if PAGE_SCRAPE_DELAY > 0:
            time.sleep(PAGE_SCRAPE_DELAY)
        return listingFields
    except Exception as e:
        sPrint("ERR: Exception while handling page {}: {}".format(url, e))
        ERR_FILE.write("\r\nErr @ {}: {}\r\n\r\n".format(url, e))
        return None

def scrapeGenerator():
    try:
        # Iterate over page indices
        for pageIndex in range(PAGE_START_INDEX, pageEndIndex):
            pageUrl = PAGE_TEMPLATE_URL.format(pageIndex=pageIndex, query=getQueryString())
            yield handlePageUrl(pageUrl)

        # Handle ISSUE_PAGES
        sPrint("> Rescraping {} issue pages...".format(len(ISSUE_PAGES)))
        while len(ISSUE_PAGES) > 0:
            pageUrl = ISSUE_PAGES[len(ISSUE_PAGES) - 1]
            success = handlePageUrl(pageUrl)
            if success:
                ISSUE_PAGES.pop()
                yield success
    except KeyboardInterrupt:
        pass

sPrint("\r\n> Opening CSV file...")
# Write to csv
with open(os.path.join(CWD, CSV_OUT_NAME), "w+", buffering=1, encoding="UTF-8") as csvFile: 
    
    # Extract field names
    fieldNames = ["url"]
    for f in EXTRACTOR_FUNCTIONS:
        fName, empty = f("", None)
        if fName not in fieldNames:
            fieldNames.append(fName)

    if CSV_EXCEL_HEADER:
        csvFile.write("SEP={}\r\n".format(CSV_DELIMITER))

    csvWriter = csv.DictWriter(csvFile, fieldnames=fieldNames, delimiter=CSV_DELIMITER, quotechar='"', quoting=csv.QUOTE_ALL, dialect="excel")
    csvWriter.writeheader()
    sPrint("> Starting scraping pages...")

    for pageListings in scrapeGenerator():
        if pageListings:
            for listing in pageListings:
                #if listingFields:
                listingObj = { "url": listing["url"] }
                for fName in listing["fields"]:
                    listingObj[fName] = listing["fields"][fName]
                csvWriter.writerow(listingObj)
    
# Cleanup & Exit
PAGES_PROGRESS.close()
LISTINGS_PROGRESS.close()
ERR_FILE.close()
exit(0)
