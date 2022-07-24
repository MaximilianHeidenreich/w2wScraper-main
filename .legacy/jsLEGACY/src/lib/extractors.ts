import { IField } from "./interfaces.ts";
import { stripOuterWhitespace } from "./transformer.ts";

export const listingExtractors = [
    extractBusinessName,
    extractBusinessAddress,
    extractBusinessPhone,
    extractBusinessWebsite,
    extractBusinessDescription,
    extractEstablished,
    extractEmployeeCount,
    extractLocation,
]

export function extractBusinessName(doc: Document): IField {
    return {
        name: "Business Name",
        value: stripOuterWhitespace(doc.querySelector(".business-card__title")?.textContent)
    }
}

export function extractBusinessAddress(doc: Document): IField {
    return {
        name: "Business Address",
        value: stripOuterWhitespace(doc.querySelector(".business-card__address")?.textContent)
    }
}

export function extractBusinessPhone(doc: Document): IField {
    return {
        name: "Business Phone",
        value: stripOuterWhitespace(doc.querySelector("[data-test=\"phone__number\"] > span")?.textContent)
    }
}

export function extractBusinessWebsite(doc: Document): IField {
    return {
        name: "Business Website",
        value: doc.querySelector(".website-button__button")?.attributes.getNamedItem("href")?.value
    }
}

export function extractBusinessDescription(doc: Document): IField {
    return {
        name: "Business Description",
        value: doc.querySelector(".description__content")?.innerText
    }
}

export function extractEstablished(doc: Document): IField {
    let boxes = Array.from(doc.querySelectorAll(".facts-and-figures > .facts-and-figures__box"));
    let result: string | undefined = undefined;
    for (let i in boxes) {
        let box = boxes[i];
        if (stripOuterWhitespace(box.querySelector(".facts-and-figures__title")?.textContent) === "Gründungsjahr") {
            result = stripOuterWhitespace(box.querySelector(".facts-and-figures__value")?.textContent);
        }
    }
    return {
        name: "Established",
        value: result
    }
}

export function extractEmployeeCount(doc: Document, reMapCount: boolean = true): IField {
    let boxes = Array.from(doc.querySelectorAll(".facts-and-figures > .facts-and-figures__box"));
    let result: string | undefined = undefined;
    for (let i in boxes) {
        let box = boxes[i];
        if (stripOuterWhitespace(box.querySelector(".facts-and-figures__title")?.textContent) === "Mitarbeiteranzahl") {
            result = stripOuterWhitespace(box.querySelector(".facts-and-figures__value")?.textContent);
        }
    }

    // Optional mapping
    const mapping = {
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
    if (reMapCount && mapping[result]) result = mapping[result]


    return {
        name: "Employee Count",
        value: result
    }
}



export function extractLocation(doc: Document): IField {
    let baseEl = doc.querySelector(".location-and-contact address");

    const getChildText = (el: Node) => {
        
        if (!el.hasChildNodes) return el.textContent;
        let childText = Array.from(el.childNodes).map(c => getChildText(c)).join("\n\r");
        return el.textContent + "\n\r" + childText;
    };
    let result = baseEl?.innerText || undefined; // TODO: Fix missing newlines?
    
    return {
        name: "Location",
        value: result
    }
}