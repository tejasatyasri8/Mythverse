export interface Message {
    role: "user" | "assistant";
    content: string;
}

export interface ChatRequest {
    message: string;
    session_id: string;

    mode?: "single" | "compare";

    // Single mode
    religion?: string;
    holy_book?: string;

    // Compare mode
    first_religion?: string;
    first_book?: string;
    second_religion?: string;
    second_book?: string;

    history?: Message[];
}

export interface ChatResponse {
    reply: string;
    sources?: any[];
}