"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";

export default function Home() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<
    {
      role: string;
      content: string;
    }[]
  >([]);
  const [isLoading, setIsLoading] = useState(false);


  async function sendMessage() {
    if (message.trim() === "" || isLoading) return;

    const userMessage = {
        role: "user",
        content: message,
    };

    setMessages((prev) => [...prev, userMessage]);

    setMessage("");

    setIsLoading(true);

    try {

    const response = await fetch(
        "http://127.0.0.1:8000/chat/",
        {
            method: "POST",
            headers:{
                "Content-Type":"application/json",
            },
            body: JSON.stringify({
                session_id:"demo-session",
                message:message,
            }),
        }
    );

    const data = await response.json();

    setMessages((prev)=>[
        ...prev,
        {
            role:"assistant",
            content:data.reply,
        }
    ]);

    }
    catch(error){

        setMessages((prev)=>[
            ...prev,
            {
                role:"assistant",
                content:"Sorry, something went wrong. Please try again.",
            }
        ]);

    }

    finally{

        setIsLoading(false);

    }
}

  return (
    <main className="flex min-h-screen items-center justify-center bg-gray-100">

      <div className="flex h-[700px] w-[900px] flex-col rounded-xl bg-white shadow-xl">

        {/* Header */}
        <div className="border-b p-5">
          <h1 className="text-3xl font-bold text-black">
            MythVerse
          </h1>
        </div>

        {/* Chat Area */}
        <div className="flex-1 overflow-y-auto p-6">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`mb-5 rounded-xl p-4 break-words text-black ${
              msg.role === "user"
                ? "bg-blue-100 ml-auto max-w-[75%]"
                : "bg-gray-200 mr-auto max-w-[75%]"
            }`}
          >
            <strong>
              {msg.role === "user" ? "You" : "MythVerse"}:
            </strong>{" "}
            <ReactMarkdown>
            {msg.content}
            </ReactMarkdown>
          </div>
        ))}
        {isLoading && (
          <div className="mb-5 rounded-xl bg-gray-200 p-4 text-black mr-auto max-w-[75%]">
            <strong>MythVerse:</strong> typing...
          </div>
        )}

        </div>
        {/* Input Area */}
        <div className="flex gap-3 border-t p-5">

          <input
            className="flex-1 rounded border p-3 text-black"
            placeholder="Ask about mythology..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
              
            onKeyDown={(e) => {if (e.key === "Enter") {
                sendMessage();
              }
            }}
          />

          <button
            onClick={sendMessage}
            className="rounded bg-blue-600 px-6 text-white"
          >
            Send
          </button>

        </div>

      </div>

    </main>
  );
}