"use client";


import {useState} from "react";
import {Message} from "../types/chat";
import {sendChatMessage} from "../services/api";


export default function useChat(
    religion?:string,
    book?:string
){


const [messages,setMessages]
=
useState<Message[]>([
    {
        role:"assistant",
        content:
        "Welcome to MythVerse 🙏 Ask anything about scriptures."
    }
]);


const [loading,setLoading]
=
useState(false);
const [sessionId] = useState(
    () => crypto.randomUUID()
);


async function sendMessage(
    text:string
){


    const userMessage:Message =
    {
        role:"user",
        content:text
    };


    setMessages(prev=>[
        ...prev,
        userMessage
    ]);



    setLoading(true);



    try{


        const data =
await sendChatMessage({

    message:text,

    session_id:sessionId,

    religion,

    holy_book: book,

    history: messages.slice(-2)

});



        setMessages(prev=>[

            ...prev,

            {
                role:"assistant",
                content:data.reply
            }

        ]);



    }
    catch(error){


        setMessages(prev=>[

            ...prev,

            {
                role:"assistant",
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