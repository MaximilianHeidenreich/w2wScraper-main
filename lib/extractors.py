import re, os, atexit
from typing import Callable, Tuple
from bs4 import BeautifulSoup, ResultSet
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from lib.transformers import *

EMPTY_EXTRACT = ""
MULTILINE_DELIMITER = "\r\n"

# UTIL
def rSetToList(rSet: ResultSet) -> list:
    o = []
    for e in rSet:
        o.append(e)
    return o

# Contains a function for every unique value (collection) to extract.
# An extractor function can contain setup code and should return the following tuple:
#   Tuple[fieldName: str, Callable[[url: str, soup: BeautifulSoup], Tuple[str, str]]]
# The callable ALWAYS returns a tuple value (EMPTY_EXTRACT if not found in soup):
#   Tuple[fieldName: str, value: str]

def extractBusinessName() -> Tuple[str, Callable[[str, BeautifulSoup], Tuple[str, str]]]:
    """
    Extracts the business name from the soup.
    """
    fieldName = "Business Name"
    def f(url: str, soup: BeautifulSoup) -> Tuple[str, str]:
        el = soup.select_one(".business-card__title")
        if not el:
            return fieldName, EMPTY_EXTRACT
        return fieldName, stripOuterWhitespace(el.text)
    return fieldName, lambda url, soup : f(url, soup)

def extractBusinessAddress() -> Tuple[str, Callable[[str, BeautifulSoup], Tuple[str, str]]]:
    """
    Extracts the business address from the soup.
    """
    fieldName = "Business Address"
    def f(url: str, soup: BeautifulSoup) -> Tuple[str, str]:
        el = soup.select_one(".business-card__address")
        if not el:
            return fieldName, EMPTY_EXTRACT
        addr = stripOuterWhitespace(el.text)
        addr = re.sub(r"\n\s*\n", "\r\n", addr)
        return fieldName, addr
    return fieldName, lambda url, soup : f(url, soup)

def extractBusinessPhone() -> Tuple[str, Callable[[str, BeautifulSoup], Tuple[str, str]]]:
    """
    Extracts the business phone from the soup.
    """
    fieldName = "Business Phone"
    def f(url: str, soup: BeautifulSoup) -> Tuple[str, str]:
        el = soup.select_one("[data-test=\"phone__number\"] > span")
        if not el:
            return fieldName, EMPTY_EXTRACT
        return fieldName, stripOuterWhitespace(el.text)
    return fieldName, lambda url, soup : f(url, soup)

def extractBusinessWebsite() -> Tuple[str, Callable[[str, BeautifulSoup], Tuple[str, str]]]:
    """
    Extracts the business website from the soup.
    """
    fieldName = "Business Website"
    def f(url: str, soup: BeautifulSoup) -> Tuple[str, str]:
        el = soup.select_one("#location-and-contact__website")
        if not el:
            return fieldName, EMPTY_EXTRACT
        return fieldName, stripOuterWhitespace(el.get("href"))
    return fieldName, lambda url, soup : f(url, soup)

def extractBusinessDescription(browser_driver_name: str) -> Tuple[str, Callable[[str, BeautifulSoup], Tuple[str, str]]]:
    """
    Extracts the business description from the soup.
    :param browser_driver_name: driver binary name inside ./bin/
    ! Need selenium, because the description is dynamically loaded into the page !
    """
    print("WARNING: 'extractBusinessDescription' active. Be sure to have the latest chromedriver inside bin/ dir & Chrome installed on your system!")
    fieldName = "Business Description"

    PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
    DRIVER_BIN = os.path.join(PROJECT_ROOT, "bin/{}".format(browser_driver_name))
    BROWSER = webdriver.Chrome(executable_path = DRIVER_BIN)
    atexit.register(lambda : BROWSER.quit())

    def f(url: str, soup: BeautifulSoup) -> Tuple[str, str]:
        BROWSER.get(url)
        elem = WebDriverWait(BROWSER, 15).until(
            EC.presence_of_element_located((By.ID, "company-media-about-us")) 
        )
        pageSoup = BeautifulSoup(BROWSER.page_source, "html.parser")
        el = pageSoup.select_one("#company-media-about-us")
        if not el:
            return fieldName, EMPTY_EXTRACT
        dsc = ""
        try:
            dsc = el.attrs["description"]
        except:
            dsc = EMPTY_EXTRACT
        return fieldName, stripOuterWhitespace(dsc)
    return fieldName, lambda url, soup : f(url, soup)

def extractEstablished() -> Tuple[str, Callable[[str, BeautifulSoup], Tuple[str, str]]]:
    """
    Extracts the established date from the soup.
    """
    fieldName = "Established"
    def f(url: str, soup: BeautifulSoup) -> Tuple[str, str]:
        boxes = rSetToList(soup.select(".facts-and-figures > .facts-and-figures__box"))
        result = EMPTY_EXTRACT
        for box in boxes:
            if box.select_one(".facts-and-figures__title").text == "Gründungsjahr":
                result = box.select_one(".facts-and-figures__value").text
                break
        return fieldName, stripOuterWhitespace(result)
    return fieldName, lambda url, soup : f(url, soup)

def extractEmployeeCount() -> Tuple[str, Callable[[str, BeautifulSoup], Tuple[str, str]]]:
    """
    Extracts the employee count from the soup.
    """
    fieldName = "Employee Count"
    def f(url: str, soup: BeautifulSoup) -> Tuple[str, str]:
        boxes = rSetToList(soup.select(".facts-and-figures > .facts-and-figures__box"))
        result = EMPTY_EXTRACT
        for box in boxes:
            if box.select_one(".facts-and-figures__title").text == "Mitarbeiteranzahl":
                result = box.select_one(".facts-and-figures__value").text
                break
        # Optional mapping
        reMap = True
        mapping = {
            "1 – 4": 1,
            "5 – 9": 5,
            "10 – 19": 10,
            "20 – 49": 20,
            "50 – 99": 50,
            "100 – 199": 100,
            "200 – 499": 200,
            "500 – 999": 500,
            "1,000+": 1000
        }
        if reMap and result in mapping:
            result = mapping[result]
        return fieldName, stripOuterWhitespace(result)
    return fieldName, lambda url, soup : f(url, soup)

def extractLocation() -> Tuple[str, Callable[[str, BeautifulSoup], Tuple[str, str]]]:
    """
    Extracts the location from the soup.
    """
    fieldName = "Location"
    def f(url: str, soup: BeautifulSoup) -> Tuple[str, str]:
        el = soup.select_one(".location-and-contact address")
        if not el:
            return fieldName, EMPTY_EXTRACT
        addr = stripOuterWhitespace(el.get_text(MULTILINE_DELIMITER))
        addr = re.sub(r"\n\s*\n", "", addr)
        return fieldName, addr
    return fieldName, lambda url, soup : f(url, soup)

# TODO? extractKeyFigures

def extractContactDetails() -> Tuple[str, Callable[[str, BeautifulSoup], Tuple[str, str]]]:
    """
    Extracts the unique contact details from the soup.
    """
    fieldName = "Contact Details"
    def f(url: str, soup: BeautifulSoup) -> Tuple[str, str]:
        el = soup.select_one(".categories .categories__container")
        if not el:
            return fieldName, EMPTY_EXTRACT
        cards = el.select(".category__card")
        if not cards:
            return fieldName, EMPTY_EXTRACT
        
        displayRole = True
        # name -> { phone, roles }
        people = {}

        for card in cards:
            role = stripOuterWhitespace(card.select_one(".chip__title").text)
            name = stripOuterWhitespace(card.select_one(".direct-contact__person").text)

            # extract phone
            phoneEl = card.select_one(".vis-phone a")
            if not phoneEl: 
                continue
            phone = stripOuterWhitespace(phoneEl.text)
            if name not in people:
                people[name] = {
                    "phone": [phone],
                    "roles": [role]
                }
            else:
                if phone not in people[name]["phone"]:
                    people[name]["phone"].append(phone)
                if role not in people[name]["roles"]:
                    people[name]["roles"].append(role)
        
        result = ""
        for name in people:
            if displayRole:
                result = "{}{}\nRoles: {}\nPhones: \n{}\n\n=======\n".format(result, name, ", ".join(people[name]["roles"]), "\n".join(people[name]["phone"]))
            else:
                result = "{}{}\nPhones: \n{}\n\n=======\n".format(result, name, "\n".join(people[name]["phone"]))

        return fieldName, result
    return fieldName, lambda url, soup : f(url, soup)