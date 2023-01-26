export enum Author {
    AGENT,
    USER,
}

export interface ChatResponse {
    content: string,
    author: Author,
    sources?: string[]
}