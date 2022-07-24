import { stripOuterWhitespace, toInt } from "./transformer.ts"
import { querySelector, querySelectorAll, text, attr } from "./legacy/extractor.ts"

export function* runn(doc: Document, operations: any[]): any {
    for (let ic = 0; ic <= operations.length; ic++) {
        let currOp = operations[ic].operation;
        if (currOp === "querySelector") {
            let selector = operations[ic].options?.selector;
            yield doc.querySelector(selector);
        }
    }
}

export async function run(doc: Document, operations: any[]): any {
    let val = undefined
    for (let ic = 0; ic < operations.length; ic++) {
        
        let currOp = operations[ic].operation;
        if (currOp === "querySelector") {
            let selector = operations[ic].options?.selector;
            val = await querySelector(doc, selector);
        }
        else if (currOp === "querySelectorAll") {
            let selector = operations[ic].options?.selector;
            val = Array.from(await querySelectorAll(doc, selector));
        }
        else if (currOp === "text") {
            val = await text(val);
        }
        else if (currOp === "attr") {
            let attribute = operations[ic].options?.attribute;
            val = await attr(val, attribute);
        }
        else if (currOp === "stripOuterWhitespace") {
            val = await stripOuterWhitespace(val);
        }
        else if (currOp === "toInt") {
            val = await toInt(val);
        }
        else if (currOp === "index") {
            let index = operations[ic].options?.index;
            val = val[index];
        }
        else if (currOp === "map") {
            
            /*for (let e in val) {
                //console.log(e[2]);
                for (let ii = 0; ii < e.length; ii++) {
                    console.log(e[ii]);
                    
                }
                return
                
            }
            //console.log("out: ", Array.from(val).map(e => e.nodeName))*/
            
            let mapOperations = operations[ic].options?.mapOperations;

            val = await val.map(async e => await run(null, mapOperations))
        }
    }
    return val;
}