import ProgressBar from "https://deno.land/x/progress@v1.2.8/mod.ts";
import { writeCSVObjects } from "https://deno.land/x/csv/mod.ts";
import * as fs from "https://deno.land/std@0.149.0/fs/mod.ts";

import { IFiled } from "./lib/interfaces.ts";
import { fetcher } from "./lib/fetcher.ts"
import { scrapeListing, scrapeListings } from "./lib/scrapers.ts";
import { scrapeListingPagesCount } from "./lib/scrapers.ts";
import { listingExtractors } from "./lib/extractors.ts";

// UTILS
const escapeCSV = (str: string): string => {
    let o = str;
    while (o.indexOf('"') !== -1) {
        o = o.replace("\"", "'");
    }
    return o;
}


// Setup env
fs.ensureDirSync("./out")


// GLOBAL STATE / CONFIG
let query = "software";
const pageTemplateURL = "https://www.wlw.de/de/suche/page/{pageIndex}?q={query}";
const pageStartIndex = 1;

let OUT_CSV_NAME = `./out/${Date.now()}.csv`;
let ISSUE_PAGES: { url: string }[] = [] // Issue pages (Some pages dont answer and need to be rescanned at the end!)
let TASK_COMPLETED = 0;
let LISTING_FIELDS = []


// Handle pagination
let paginationDoc = await fetcher("https://www.wlw.de/de/suche?q=software");
let pageEndIndex = await scrapeListingPagesCount(paginationDoc);
let listingsCount = parseInt(paginationDoc.querySelector("a.search-tabs-supplier-link").innerText.split(" ")[0]);

// Setup progressbar
const PROGRESS = new ProgressBar({
  title: "Scraping...",
  total: listingsCount//pageEndIndex
});
const progress = () => PROGRESS.render(TASK_COMPLETED++);
const log = (...args) => PROGRESS.console(...args);
log("\nStarting script...");


const handleListing = async (url: string): Promise<IField[]> => {
    log(`-> Fetching listing @ ${url}`);
    let listingDoc = await fetcher(url);
    listingDoc.location = { href: url};
    let fields = await scrapeListing(listingDoc, listingExtractors);
    log(`\t Scraped ${fields.length} values from listing @ ${url}`);
    for (let iixa in fields) {  // TODO: DEBUG out only
        log(`\t${fields[iixa].name} : ${fields[iixa].value}`);
    }
    progress();
    return fields;
}

const handlePage = async (url: string): Promise<{ listingCnt: number, listingFields: { url: string, fields: IField[] } }> => {
    log(`-> Fetching page @ ${url}`);
    let pageDoc = await fetcher(url);
    pageDoc.location = { href: url};
    let listingURLs = await scrapeListings(pageDoc);
    log(`\t Found ${listingURLs.length} Listings @ ${url}`);

    let listingFields: { url: string, fields: IField[] }[] = []
    // Iterate listings
    for (let i in listingURLs) {
        let url = listingURLs[i];
        let fields = await handleListing(url);
        listingFields.push({ url, fields });
    }

    LISTING_FIELDS = LISTING_FIELDS.concat(LISTING_FIELDS, listingFields);
    // TODO: impl

    return { listingCnt: listingURLs.length, listingFields };
}

// Iterate all page indices
for (let pageIndex = pageStartIndex; pageIndex <= pageEndIndex; pageIndex++) {
    // Assemble page URL
    const pageURL = pageTemplateURL
                    .replaceAll("{pageIndex}", pageIndex)
                    .replaceAll("{query}", query);
    let { listingsCnt, listingFields } = await handlePage(pageURL);
    if (listingsCnt <= 0) {
        ISSUE_PAGES.push({ url: pageURL })
    }
    else {
        // Write csv
        const f = await Deno.open(OUT_CSV_NAME, {
            write: true,
            create: true,
            truncate: true,
        });
        
        //f.writeSync(new Uint8Array(["\xEF", "\xBB", "\xBF"]));
        f.writeSync(new Uint8Array([0xEF, 0xBB, 0xBF]));
        f.writeSync(new TextEncoder().encode("sep=,\n", "utf-16"));
        
        // Collect all fields
        let fieldNames = [];
        LISTING_FIELDS.forEach(e => {
            e.fields.forEach(f => {
                if (fieldNames.indexOf(f.name) === -1) fieldNames.push(f.name);
            });
        });
        const header = ["url", ...fieldNames];
        let CSV_MAPPED_LISTINGS = LISTING_FIELDS.map(e => {
            let o = {};
            o["url"] = `${escapeCSV(encodeURI(e.url))}`;
            e.fields.forEach(f => {
                let s = `${f.value}`
                o[f.name] = f.value ? new TextEncoder().encode(escapeCSV(s), "utf-16") : "undefined"//`${escapeCSV(s)}` : "undefined";
            });
            return o;
        });

        await writeCSVObjects(f, CSV_MAPPED_LISTINGS, { columnSeparator: ",", forceQuotes: true, header });
        f.close();
    }
}

log(`\n ! ${ISSUE_PAGES.length} Issue pages! Rescanning them ...`)

// Iterate over issue pages
while (ISSUE_PAGES.length > 0) {
    let { listingsCnt, listingFields } = await handlePage(ISSUE_PAGES[ISSUE_PAGES.length - 1].url);
    if (listingsCnt > 0) {
        ISSUE_PAGES.pop()
    }
    // TODO: impl
}


