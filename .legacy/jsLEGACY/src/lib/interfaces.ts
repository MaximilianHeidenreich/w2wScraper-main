export interface IField {
    name: string
    value: string|undefined
}
export interface IFieldExtractor {
    (doc: Document): IField
}