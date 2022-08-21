from lib.extractors import *
from datetime import datetime
import urllib.parse

# Global CONFIG
DEBUG_OUT                   = True  # Print addition extraction info

QUERY                       = {
    "q": "software",
    #"supplierTypes": "Großhändler",
    #"employeeCounts": "200+",          # Special chars are escaped automatically!
}

CSV_OUT_NAME                = "./out/wlw_{}_{}.csv".format(urllib.parse.urlencode(QUERY), datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
CSV_DELIMITER               = ","
ERROR_OUT_NAME              = "./out/wlw_{}_{}.error.txt".format(urllib.parse.urlencode(QUERY), datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))

PAGINATION_URL_TEMPLATE     = "https://www.wlw.de/de/suche?{query}"
PAGE_TEMPLATE_URL           = "https://www.wlw.de/de/suche/page/{pageIndex}?{query}"
PAGE_START_INDEX            = 1     # For debug, manually set start page
PAGE_STOP_INDEX             = None  # For debug, manually set end page
LISTING_SCRAPE_DELAY        = 0   # Delay for scraping listings (SECONDS) -> Could increase scraping success

BROWSER_DRIVER_BIN = "chromedriverOSX_m1"

# The extractor functions -> Fields to extract from listing pages
# Format: Tuple[fieldName: str, fn: function]
EXTRACTORS = [
    extractBusinessName(),
    extractBusinessAddress(),
    extractBusinessPhone(),
    extractBusinessWebsite(),
    extractBusinessDescription(BROWSER_DRIVER_BIN),
    extractEstablished(),
    extractEmployeeCount(),
    extractLocation(),
    extractContactDetails()
]