"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";
import { v4 as uuidv4 } from "uuid";

const religions = {
  Hinduism: [
    "Bhagavad Gita",
    "Ramayana",
    "Mahabharata",
    "Vedas",
    "Upanishads",
  ],
  Christianity: [
    "Bible",
  ],
  Islam: [
    "Quran",
  ],
  Buddhism: [
    "Tripitaka",
  ],
  Sikhism: [
    "Guru Granth Sahib",
  ],
};

export default function Home() {

  const [message, setMessage] = useState("");

  const [messages, setMessages] = useState<
    {
      role: string;
      content: string;
    }[]
  >([]);

  const [isLoading, setIsLoading] = useState(false);

  const [sessionId] = useState(() => uuidv4());

  const [selectedReligion, setSelectedReligion] = useState("");

  const [selectedBook, setSelectedBook] = useState("");

  const [chatStarted, setChatStarted] = useState(false);


  async function sendMessage() {

    if (message.trim() === "" || isLoading) return;


    const userMessage = {
      role: "user",
      content: message,
    };


    setMessages((prev) => [
      ...prev,
      userMessage
    ]);


    setMessage("");

    setIsLoading(true);


    try {

      const response = await fetch(
        "http://127.0.0.1:8000/chat/",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({

            session_id: sessionId,

            religion: selectedReligion,

            holy_book: selectedBook,

            message: message,

          }),
        }
      );


      const data = await response.json();


      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.reply,
        },
      ]);


    } catch(error) {


      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "Sorry, something went wrong. Please try again.",
        },
      ]);


    } finally {

      setIsLoading(false);

    }

  }



  // Religion + Book Selection Screen

  if (!chatStarted) {

    return (

      <main className="flex min-h-screen items-center justify-center bg-gray-100">

        <div className="flex w-[500px] flex-col gap-5 rounded-xl bg-white p-8 shadow-xl">


          <h1 className="text-center text-3xl font-bold text-black">
            MythVerse
          </h1>



          {!selectedReligion ? (

            <>

              <h2 className="text-center text-lg text-black">
                Select Your Religion
              </h2>


              {Object.keys(religions).map((religion) => (

                <button

                  key={religion}

                  onClick={() => {

                    setSelectedReligion(religion);

                    setSelectedBook("");

                  }}

                  className="rounded-lg border p-3 bg-white text-black"

                >

                  {religion}

                </button>

              ))}


            </>


          ) : (

            <>

              <h2 className="text-center text-lg text-black">
                Select Holy Book
              </h2>


              <p className="text-center text-black">
                {selectedReligion}
              </p>



              {(religions[selectedReligion as keyof typeof religions]).map(
                (book) => (

                <button

                  key={book}

                  onClick={() => setSelectedBook(book)}

                  className={`rounded-lg border p-3 ${
                    selectedBook === book
                      ? "bg-green-600 text-white"
                      : "bg-white text-black"
                  }`}

                >

                  {book}

                </button>

              ))}



              {selectedBook && (

                <button

                  onClick={() => setChatStarted(true)}

                  className="rounded-lg bg-blue-600 p-3 text-white"

                >

                  Start Chat

                </button>

              )}



              <button

                onClick={() => setSelectedReligion("")}

                className="text-blue-600"

              >

                Back

              </button>


            </>

          )}


        </div>

      </main>

    );

  }



  // Chat Screen

  return (

    <main className="flex min-h-screen items-center justify-center bg-gray-100">


      <div className="flex h-[700px] w-[900px] flex-col rounded-xl bg-white shadow-xl">


        <div className="border-b p-5">

  <div className="flex justify-between items-center">

    <div>
      <h1 className="text-3xl font-bold text-black">
        MythVerse
      </h1>

      <p className="text-black">
        {selectedReligion} - {selectedBook}
      </p>
    </div>


    <button
      onClick={() => {
        setChatStarted(false);
        setMessages([]);
      }}
      className="rounded bg-gray-200 px-4 py-2 text-black"
    >
      Change Book
    </button>

  </div>

</div>




        <div className="flex-1 overflow-y-auto p-6">


          {messages.map((msg,index)=>(

            <div

              key={index}

              className={`mb-5 rounded-xl p-4 break-words text-black ${
                msg.role === "user"
                ? "bg-blue-100 ml-auto max-w-[75%]"
                : "bg-gray-200 mr-auto max-w-[75%]"
              }`}

            >

              <strong>

                {msg.role==="user"
                ? "You"
                : "MythVerse"}:

              </strong>{" "}


              <ReactMarkdown>

                {msg.content}

              </ReactMarkdown>


            </div>

          ))}



          {isLoading && (

            <div className="mb-5 rounded-xl bg-gray-200 p-4 text-black mr-auto max-w-[75%]">

              <strong>
                MythVerse:
              </strong>{" "}
              typing...

            </div>

          )}


        </div>




        <div className="flex gap-3 border-t p-5">


          <input

            className="flex-1 rounded border p-3 text-black"

            placeholder="Ask about mythology..."

            value={message}

            onChange={(e)=>setMessage(e.target.value)}

            onKeyDown={(e)=>{

              if(e.key==="Enter"){

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