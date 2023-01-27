export enum Author {
    AGENT,
    USER,
}

export interface ChatEntryData {
    content: string,
    author: Author,
    context?: string,
    isTransient?: boolean,
    isStop?: boolean
}