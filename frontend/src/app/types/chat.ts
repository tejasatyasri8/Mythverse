export interface Message {
    role: "user" | "assistant";
    content: string;
}


export interface ChatRequest {
    message: string;
    session_id: string;
    religion?: string;
    holy_book?:string;
    history?:Message[];
}


export interface ChatResponse {
    reply: string;
    sources?: any[];
}