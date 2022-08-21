from urllib.parse import urljoin
from tqdm import tqdm
from datetime import datetime
from typing import Callable, Tuple, List
import traceback as tb
from time import sleep

from lib.fetcher import fetcher

# UTILS
def sPrint(strr: str):
    tqdm.write(str(strr))


def scrapeListingPage(url: str, extractors, LISTING_SCRAPE_DELAY, csv_writer, sErr: Callable[[str], None], listingsProgress):
    """
    Scrapes all values configued from a single listing page.
    """
    if LISTING_SCRAPE_DELAY > 0:
        sleep(LISTING_SCRAPE_DELAY)

    try:
        sPrint("> Fetching listing @ {} ...".format(url))
        pageSoup = fetcher(url)
        listingFields = { "url": url }
        for fieldName, eFn in extractors:
            fieldValue = eFn(url, pageSoup)
            listingFields[fieldName] = fieldValue[1]
        
        sPrint("=> Scraped {}/{} fields from listing page @ {}".format(len(listingFields.keys()) - 1, len(extractors), url))
        listingsProgress.update(1)
        csv_writer.writerow(listingFields)
    except Exception as e:
        sErr("@ {}\n {}".format(url, ''.join(tb.format_exception(None, e, e.__traceback__))))
        listingsProgress.update(1)


def scrapeSearchResultPage(url: str, extractors, LISTING_SCRAPE_DELAY, csv_writer, sErr: Callable[[str], None], rescrapeLater: Callable[[str], None], pagesProgress, listingsProgress):
    """
    Scrapes all the listings inside the given search result page.
    """

    try:
        sPrint("> Fetching search results @ {} ...".format(url))
        listingURLS = []
        pageSoup = fetcher(url)
        listings = pageSoup.select("a[href].company-title-link")
        if listings.__sizeof__() <= 0:
            sPrint("WARNING: No listings found on page {} -> Rescraping later".format(url))
            rescrapeLater(url)
            return
        for el in listings:
            path = el.get("href")
            listingUrl = urljoin(url, path)
            listingURLS.append(listingUrl)
        
        sPrint("=> Found {} listings!".format(len(listingURLS)))
        for pUrl in listingURLS:
            scrapeListingPage(pUrl, extractors, LISTING_SCRAPE_DELAY, csv_writer, sErr, listingsProgress)
        pagesProgress.update(1)
        return
    except Exception as e:
        sErr("@ {}\n {}".format(url, ''.join(tb.format_exception(None, e, e.__traceback__))))
        rescrapeLater(url)
