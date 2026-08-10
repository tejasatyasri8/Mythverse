import { ChatRequest, ChatResponse } from "../types/chat";


const API_URL = process.env.NEXT_PUBLIC_API_URL;


export async function sendChatMessage(
    data: ChatRequest
): Promise<ChatResponse>{


    const response = await fetch(
        `${API_URL}/chat/`,
        {
            method:"POST",

            headers:{
                "Content-Type":"application/json"
            },

            body:JSON.stringify(data)
        }
    );


    if (!response.ok) {

        const errorText = await response.text();

        console.error(
            "Backend error:",
            response.status,
            errorText
        );

        throw new Error(
            `Backend returned ${response.status}: ${errorText}`
        );
    }

    return response.json();
}