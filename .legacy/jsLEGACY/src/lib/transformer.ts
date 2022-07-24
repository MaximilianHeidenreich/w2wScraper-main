
/**
 * Strips whitespaces (including tabs & newlines) from the outsides of a string.
 * ! Any whitespace between characters / words will be ignored !
 * @param s The string to process.
 */
export function stripOuterWhitespace(s: string|undefined): string|undefined {
    if (!s) return undefined;
    return s.replace(/^\s+|\s+$/g, "");
}

export async function toInt(e: any): Promise<number> {
    return parseInt(e);
}