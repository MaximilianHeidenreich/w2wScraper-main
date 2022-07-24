
# Installation
- python3 -m pip install bs4
- python3 -m pip install requests
- python3 -m pip install tqdm 


# Configuration
`DEBUG_OUT` (main.py): True/False -> Prints extracted fields for every listing while the script is running.

`QUERY` (main.py): dict<string, string> -> Query parameters for search results. Each entry is a unique search parameter. No escaping is necessary! "q" is the searchterm and MUST always be present.


`CSV_OUT_NAME` (main.py): string -> The name of the generated CSV file.

`CSV_DELIMITER` (main.py): string -> The delimiter which separates columns inside the CSV.

`CSV_EXCEL_HEADER` (main.py): bool -> Whether to add a header to the output file. This will allow Excel to open the file directly, but will break Special Chars (Ä,Ö,Ü...).

`ERROR_OUT_NAME` (main.py): string -> The name of the generated error file.

`PAGINATION_URL_TEMPLATE` (main.py): string -> The template for the pagination page. This will be used to calculate search results & scrape individual listings.

`PAGE_TEMPLATE_URL` (main.py): string -> The template to use for specific page indices.

`PAGE_START_INDEX` (main.py): int -> The index to start iterating pages at.

`PAGE_SCRAPE_DELAY` (main.py): int -> Optional delay (SECONDS) between page scrapes. Might be useful if rate-limited.

`EMPTY_EXTRACT` (extractors.py): string -> Content to put in CSV when value cannot be extracted (e.g. "" for empty column).

`MULTILINE_DELIMITER` (extractors.py): string -> How to represent multiple lines while extracting text from DOM elements. (e.g. "\r\n" will keep the newline / " - " will represent multi-line strings in a single line delimited by " - ").

# Usage
1. Install python3
2. Install packages listed above
3. Configre options listed above
4. Run `python3 main.py`
5. Result CSV will be generated in ./out folder!

# Architecture

## Fetcher
Input: URL
Fetches a given webpage and returns DOM representaton as BeautifulSoup

## Transformer
### Operations
#### stripOuterWhitespace
Strips any outher whitespace of a given string

## Extractor
Single functions which take in the page URL and BeautifulSoup and return a "Field".
A Field is a tuple containing the field name and it string value.
Fields will be collected and written to the csv file.
A single extractor function should only extract a single field.

## Scrapers
Utility functions for scraping a single listing or scrape all listings from a search page.