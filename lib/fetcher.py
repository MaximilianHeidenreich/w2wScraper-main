from bs4 import BeautifulSoup
import requests

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

def fetcher(url: str) -> BeautifulSoup:
    """
    Fetches the html of a given url and returns it as a soup.
    """
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    return soup