"use client";

import { useState, useEffect } from "react";
import { Message } from "../types/chat";
import { sendChatMessage } from "../services/api";

export default function useChat(
    religion?: string,
    book?: string,
    step?: number
) {
    const [messages, setMessages] = useState<Message[]>([
        {
            role: "assistant",
            content:
                "Welcome to MythVerse 🙏 Ask anything about scriptures."
        }
    ]);

    const [loading, setLoading] = useState(false);

    const [sessionId, setSessionId] = useState(
        () => crypto.randomUUID()
    );

    // Reset chat whenever the user enters the chat screen
    useEffect(() => {
        if (step === 4) {
            setMessages([
                {
                    role: "assistant",
                    content:
                        "Welcome to MythVerse 🙏 Ask anything about scriptures."
                }
            ]);

            // Create a completely new session
            setSessionId(crypto.randomUUID());
        }
    }, [step, religion, book]);

    async function sendMessage(text: string) {
        const userMessage: Message = {
            role: "user",
            content: text
        };

        setMessages(prev => [
            ...prev,
            userMessage
        ]);

        setLoading(true);

        try {
            const data = await sendChatMessage({
                message: text,
                session_id: sessionId,
                religion,
                holy_book: book,
                history: messages.slice(-2)
            });

            setMessages(prev => [
                ...prev,
                {
                    role: "assistant",
                    content: data.reply
                }
            ]);
        } catch (error) {
            setMessages(prev => [
                ...prev,
                {
                    role: "assistant",
                    content: "Error: " + String(error)
                }
            ]);
        }

        setLoading(false);
    }

    return {
        messages,
        loading,
        sendMessage
    };
}