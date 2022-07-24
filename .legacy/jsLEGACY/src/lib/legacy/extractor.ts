
/**
 * Returns the queried element or undefined.
 * @param selector The selector to use.
 */
export async function querySelector(doc: Document, selector: string): Promise<Element> {
    return doc.querySelector(selector);
}

/**
 * Returns a list of queried element.
 * @param selector The selector to use.
 */
export async function querySelectorAll(doc: Document, selector: string): Promise<NodeListOf<Element>> {
    return doc.querySelectorAll(selector);
}

/**
 * Extracts the text content of a DOM Element.
 * @param el The element.
 * @returns The text or undefined if element does not exist.
 */
export async function text(el: Element|undefined): Promise<string> {
    return el?.textContent;
}

export async function attr(el: Element|undefined, attrName: string): Promise<string> {
    if (!el) return undefined;
    return el[attrName];
}