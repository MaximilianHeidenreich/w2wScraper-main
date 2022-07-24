/*import { DOMParser } from "https://deno.land/x/deno_dom/deno-dom-wasm.ts";

const escape = t => t?.replace(/^\s+|\s+$/g, "");

export async function scrapeListing(url: string) {
    // https://www.wlw.de/de/firma/jung-software-gmbh-971029
    url = "https://www.wlw.de/de/firma/jung-software-gmbh-971029";
    const res = await fetch(url);
    const html = await res.text();
    const doc: Document  = new DOMParser().parseFromString(html, "text/html");

    const lName = escape(doc.querySelector(".business-card__title")?.textContent)
    const lAddr = escape(doc.querySelector(".business-card__address")?.textContent)
    const lPhone = escape(doc.querySelector('[data-test="phone__number"] > span')?.textContent)
    
    const lEstablished = escape(doc.querySelectorAll('.facts-and-figures__box')[1].querySelector(".facts-and-figures__value")?.textContent)
    const lEmployees = escape(doc.querySelectorAll('.facts-and-figures__box')[2].querySelector(".facts-and-figures__value")?.textContent)
    
   

    let listingData = {
        lName,
        lAddr,
        lPhone,

        lEstablished,
        lEmployees
    }
    console.log(listingData);
    
}*/

import { IFieldExtractor, IFiled } from "./interfaces.ts";
import { stripOuterWhitespace } from "./transformer.ts";

export async function scrapeListing(doc: Document, fieldExtractors: IFieldExtractor[]): Promise<IField[]> {
    return fieldExtractors.map(f => f(doc));
}

export async function scrapeListings(doc: Document): Promise<string[]> {
    let listingLinks = Array.from(doc.querySelectorAll("a[href].company-title-link"));
    if (listingLinks.length == 0) return [];

    listingLinks = listingLinks
                        .map(e => e["attributes"].getNamedItem("href").value)
                        .map(e => new URL(e, doc.location.href).href)
    return listingLinks;
}

export async function scrapeListingPagesCount(doc: Document): Promise<number> {
    let maxPagesTxt = doc.querySelector(".pagination > :nth-last-child(2)")?.textContent;
    if (!maxPagesTxt) throw Error(`Could not determine maxPage @ ${doc.location.href}`);
    return parseInt(await stripOuterWhitespace(maxPagesTxt));
}