import { ChatRequest, ChatResponse } from "../types/chat";


const API_URL = "http://127.0.0.1:8000";


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


    if(!response.ok){

        throw new Error(
            "Failed to get response"
        );

    }


    return response.json();

}