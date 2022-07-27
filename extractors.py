import re
from typing import Tuple
from bs4 import BeautifulSoup, ResultSet
from transformers import stripOuterWhitespace

EMPTY_EXTRACT = "none"
MULTILINE_DELIMITER = "\r\n"

# UTIL
def rSetToList(rSet: ResultSet) -> list:
    o = []
    for e in rSet:
        o.append(e)
    return o


def extractBusinessName(url: str, soup: BeautifulSoup) -> Tuple[str, str]:
    """
    Extracts the business name from the soup.
    """
    FIELD_NAME = "Business Name"
    if not soup: return FIELD_NAME, EMPTY_EXTRACT

    el = soup.select_one(".business-card__title")
    if not el:
        return FIELD_NAME, EMPTY_EXTRACT
    return FIELD_NAME, stripOuterWhitespace(el.text)


def extractBusinessAddress(url: str, soup: BeautifulSoup) -> Tuple[str, str]:
    """
    Extracts the business address from the soup.
    """
    FIELD_NAME = "Business Address"
    if not soup: return FIELD_NAME, EMPTY_EXTRACT

    el = soup.select_one(".business-card__address")
    if not el:
        return FIELD_NAME, EMPTY_EXTRACT
    return FIELD_NAME, stripOuterWhitespace(el.text)


def extractBusinessPhone(url: str, soup: BeautifulSoup) -> Tuple[str, str]:
    """
    Extracts the business phone from the soup.
    """
    FIELD_NAME = "Business Phone"
    if not soup: return FIELD_NAME, EMPTY_EXTRACT

    el = soup.select_one("[data-test=\"phone__number\"] > span")
    if not el:
        return FIELD_NAME, EMPTY_EXTRACT
    return FIELD_NAME, stripOuterWhitespace(el.text)


def extractBusinessWebsite(url: str, soup: BeautifulSoup) -> Tuple[str, str]:
    """
    Extracts the business website from the soup.
    """
    FIELD_NAME = "Business Website"
    if not soup: return FIELD_NAME, EMPTY_EXTRACT

    el = soup.select_one("#location-and-contact__website")#"a.website-button__button")
    if not el:
        return FIELD_NAME, EMPTY_EXTRACT
    return FIELD_NAME, stripOuterWhitespace(el.get("href"))


def extractBusinessDescription(url: str, soup: BeautifulSoup) -> Tuple[str, str]:
    """
    Extracts the business description from the soup.
    """
    FIELD_NAME = "Business Description"
    if not soup: return FIELD_NAME, EMPTY_EXTRACT

    # TODO!: Impls
    el = soup.select_one("p.company-summary__text")
    #el = soup.select_one("div#company-media-about-us div.description__content")
    if not el:
        return FIELD_NAME, EMPTY_EXTRACT
    return FIELD_NAME, stripOuterWhitespace(el.getText(MULTILINE_DELIMITER))


def extractEstablished(url: str, soup: BeautifulSoup) -> Tuple[str, str]:
    """
    Extracts the established date from the soup.
    """
    FIELD_NAME = "Established"
    if not soup: return FIELD_NAME, EMPTY_EXTRACT 

    boxes = rSetToList(soup.select(".facts-and-figures > .facts-and-figures__box"))
    result = EMPTY_EXTRACT
    for box in boxes:
        if box.select_one(".facts-and-figures__title").text == "Gründungsjahr":
            result = box.select_one(".facts-and-figures__value").text
            break
    return FIELD_NAME, stripOuterWhitespace(result)


def extractEmployeeCount(url: str, soup: BeautifulSoup) -> Tuple[str, str]:
    """
    Extracts the employee count from the soup.
    """
    FIELD_NAME = "Employee Count"
    if not soup: return FIELD_NAME, EMPTY_EXTRACT 

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

    return FIELD_NAME, stripOuterWhitespace(result)


def extractLocation(url: str, soup: BeautifulSoup) -> Tuple[str, str]:
    """
    Extracts the location from the soup.
    """
    FIELD_NAME = "Location"
    if not soup: return FIELD_NAME, EMPTY_EXTRACT 

    el = soup.select_one(".location-and-contact address")
    if not el:
        return FIELD_NAME, EMPTY_EXTRACT
    return FIELD_NAME, stripOuterWhitespace(el.get_text(MULTILINE_DELIMITER))

def extractKeyFigures(url: str, soup: BeautifulSoup) -> Tuple[str, str]:
    """
    Extracts the key figures from the soup.
    """
    FIELD_NAME = "Key Figures"
    if not soup: return FIELD_NAME, EMPTY_EXTRACT 

    fig_container = soup.select_one("table")
    print("\n\n\n\n{}\n\n\n\n".format(fig_container))
    if not fig_container:
        return FIELD_NAME, EMPTY_EXTRACT
    
    # Jahr
    year = stripOuterWhitespace(soup.select_one(".balance table thead tr th:last-child").text)
    # Bilanzsumme
    summ = stripOuterWhitespace(soup.select_one(".balance table tbody tr:first-child td:last-child").text)
    # Umsatz
    umsatz = stripOuterWhitespace(soup.select_one(".balance table tbody tr:last-child td:last-child").text)

    o = "Jahr: {}\r\nBilanzsumme: {}\r\nUmsatz: {}\r\n".format(year, summ, umsatz)

    return FIELD_NAME, o

def extractContactDetails(url: str, soup: BeautifulSoup) -> Tuple[str, str]:
    """
    Extracts the contact details for specific persons from the soup.
    Configure this extractor to include only specific search strings in person titles or 
    to include all persons.
    """
    FIELD_NAME = "Contact Details"
    if not soup: return FIELD_NAME, EMPTY_EXTRACT 

    titleFilter = None # e.g. r"\bGeschäftsführer\b" -> Will only extract persons with "Geschäftsführer" in their title

    el = soup.select_one(".categories .categories__container")
    if not el:
        return FIELD_NAME, EMPTY_EXTRACT
    cards = el.select(".category__card")
    if not cards:
        return FIELD_NAME, EMPTY_EXTRACT

    cardDetails = []

    for card in cards:
        title = stripOuterWhitespace(card.select_one(".chip__title").text)
        if not titleFilter or re.match(titleFilter, title):
            name = stripOuterWhitespace(card.select_one(".direct-contact__person").text)
            buttons = card.select(".category__buttons")
            contactStr = ""
            for btn in buttons:
                btnText = btn.getText(MULTILINE_DELIMITER)
                btnText = re.sub("Telefonnummer anzeigen", "", btnText)
                btnText = re.sub("Firma kontaktieren", "", btnText)
                contactStr = contactStr + btnText
                contactStr = re.sub(r"\n\s*\n", "\r\n\r\n", contactStr)
                contactStr = contactStr + "\r\n- NEXT BUTTON -\r\n"
                
            # Extract phone numbers
            #phoneNum = re.compile(r"[^\d\s\n\r+-/().]+").sub("", contactStr)
            #phoneNum = re.sub(r"\n\s*\n", "  -  ", phoneNum)
            
            cardDetails.append({
                "title": title,
                "name": name,
                "contacts": contactStr
            })

    outStr = ""
    for details in cardDetails:
        outStr = outStr + "Title: {}\r\nName: {}\r\nContacts: {}\r\n".format(details["title"], details["name"], details["contacts"])

    return FIELD_NAME, outStr

