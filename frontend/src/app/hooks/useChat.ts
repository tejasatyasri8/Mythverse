"use client";

import { useState } from "react";
import { Message } from "../types/chat";
import { sendChatMessage } from "../services/api";

interface Scripture {
    religion?: {
        name?: string;
    } | string;

    book?: {
        name?: string;
    } | string;
}

function getName(value: any): string | undefined {
    if (!value) return undefined;

    if (typeof value === "string") {
        return value;
    }

    return value.name;
}

export default function useChat(
    mode?: string,
    religion?: any,
    book?: any,
    firstScripture?: Scripture | null,
    secondScripture?: Scripture | null
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

    function resetChat() {
        setMessages([
            {
                role: "assistant",
                content:
                    "Welcome to MythVerse 🙏 Ask anything about scriptures."
            }
        ]);

        setSessionId(crypto.randomUUID());
        setLoading(false);
    }

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
            let requestData: any = {
                message: text,
                session_id: sessionId,
                mode: mode || "single",
                history: messages.slice(-6)
            };

            // -----------------------------
            // SINGLE MODE
            // -----------------------------

            if (mode === "single") {
                requestData.religion = getName(religion);
                requestData.holy_book = getName(book);
            }

            // -----------------------------
            // COMPARE MODE
            // -----------------------------

            if (mode === "compare") {
                requestData.first_religion =
                    getName(firstScripture?.religion);

                requestData.first_book =
                    getName(firstScripture?.book);

                requestData.second_religion =
                    getName(secondScripture?.religion);

                requestData.second_book =
                    getName(secondScripture?.book);
            }

            console.log(
                "Sending chat request:",
                requestData
            );

            const data = await sendChatMessage(requestData);

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
                    content:
                        "Error: " + String(error)
                }
            ]);

        } finally {
            setLoading(false);
        }
    }

    return {
        messages,
        loading,
        sendMessage,
        resetChat
    };
}