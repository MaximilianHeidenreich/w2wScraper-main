import { DOMParser } from "https://deno.land/x/deno_dom/deno-dom-wasm.ts";

/**
 * Fetches a page from URL and parses the HTML contents.
 * @param url The url to fetch
 * @returns Promise, resolving to parsed DOM Document for further queries.
 */
export async function fetcher(url: string): Promise<Document> {
    const HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }
    const res = await fetch(url, {
        headers: HEADERS
    });
    const html = await res.text();
    const doc: Document  = new DOMParser().parseFromString(html, "text/html");
    return doc;
}

/**
 * Fetches pages from start to end index.
 * Specify in urlTemplate: {pageIndex} -> current index
 * e.g. https://www.xyz.com/page/{pageIndex}?query=YourSearch
 * @param urlTemplate The url to fetch (use {pageIndex} variable inside it)
 * @param start The starting page index
 * @param end The end page index
 * @returns Generator of fetcher Promises resolving to Documents.
 */
export async function* paginatedFetcher(urlTemplate: string, start: number, end: number): IterableIterator<Promise<Document>> {
    for (let i = start; i <= end; i++) {
        const url = urlTemplate.replaceAll("{pageIndex}", i);
        yield fetcher(url);
    }
}