from sys import exit
import os, csv, urllib.parse
from config import *
from tqdm import tqdm
from datetime import datetime

from lib.fetcher import fetcher
from lib.transformers import stripOuterWhitespace
from lib.scrapers import *

# UTILS
def sPrint(strr: str):
    tqdm.write(str(strr))
def sErr(strr: str):
    sPrint("ERR: {}".format(strr))
    ERR_FILE.write("======== [ Err @ {} ] ========\nErr: {}\n\n".format(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"), strr))
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
        print("ERR: No query 'q' string provided inside config.py!")
        exit(1)
    return urllib.parse.urlencode(QUERY)

# Setup env
if not os.path.exists(os.path.join(os.getcwd(), "out")):
    os.makedirs(os.path.join(os.getcwd(), "out"))

# Setup script state
CWD = os.getcwd()
ERR_FILE = open(os.path.join(CWD, ERROR_OUT_NAME), "w+", buffering=1, encoding="UTF-8")
OUT_FILE = open(os.path.join(CWD, CSV_OUT_NAME), "w+", buffering=1, encoding="UTF-8")
ISSUE_PAGES = []

# Setting up CSV_WRITER
csv_headers = ["url"]
for e in EXTRACTORS:
    csv_headers.append(e[0])
CSV_WRITER = csv.DictWriter(OUT_FILE, fieldnames=csv_headers, delimiter=CSV_DELIMITER, quotechar='"', quoting=csv.QUOTE_ALL, dialect="excel")
CSV_WRITER.writeheader()

sPrint("> Fetching pagination from {}".format(PAGINATION_URL_TEMPLATE.format(query=getQueryString())))
paginationSoup = fetcher(PAGINATION_URL_TEMPLATE.format(query=getQueryString()))
paginationEls = paginationSoup.select(".pagination > :nth-last-child(2)")
if paginationEls.__sizeof__() <= 0:
    sErr("Pagination could not be extracted!")
    exit(1)
try:
    pageEndIndex = int(stripOuterWhitespace(paginationEls[0].text))
    if PAGE_STOP_INDEX != None:
        pageEndIndex = PAGE_STOP_INDEX
except ValueError:
    sErr("Pagination value is not Integer: {}".format(paginationEls[0].text))
    exit(1)

listingsCntEls = paginationSoup.select("a.search-tabs-supplier-link")
if listingsCntEls.__sizeof__() <= 0:
    sErr("Listings count could not be extracted!")
    exit(1)
try:
    listingsCnt = int(stripOuterWhitespace(listingsCntEls[0].text.split(" ")[0]))
except ValueError:
    sErr("Listings count value is not Integer: {}".format(listingsCntEls[0].text))
    exit(1)

sPrint("=> Pagination: {} - {} / {} listings".format(PAGE_START_INDEX, pageEndIndex, listingsCnt))

PAGES_PROGRESS = tqdm(desc="Pages", total=pageEndIndex)
LISTINGS_PROGRESS = tqdm(desc="Listings", total=listingsCnt)

sPrint("> Starting scraping pages...")

try:
    def rescrapeLater(url: str):
        ISSUE_PAGES.appen(url)

    #iterate over page indices
    for pageIndex in range(PAGE_START_INDEX, pageEndIndex):
        pageUrl = PAGE_TEMPLATE_URL.format(pageIndex=pageIndex, query=getQueryString())
        scrapeSearchResultPage(pageUrl, EXTRACTORS, LISTING_SCRAPE_DELAY, CSV_WRITER, sErr, rescrapeLater, PAGES_PROGRESS, LISTINGS_PROGRESS)
    
    # Rescrape issue pages
    while len(ISSUE_PAGES) > 0:
        sPrint("> Rescraping 1 of {} issue pages...".format(len(ISSUE_PAGES)))
        pageUrl = ISSUE_PAGES[len(ISSUE_PAGES) - 1]
        ISSUE_PAGES.pop()
        scrapeSearchResultPage(pageUrl, EXTRACTORS, LISTING_SCRAPE_DELAY, CSV_WRITER, sErr, rescrapeLater, PAGES_PROGRESS, LISTINGS_PROGRESS)
except KeyboardInterrupt:
    pass
except Exception as e:
    sErr(e)

PAGES_PROGRESS.close()
LISTINGS_PROGRESS.close()
ERR_FILE.close()
OUT_FILE.close()
exit(0)

