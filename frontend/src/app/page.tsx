"use client";


import {useState} from "react";
import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

import ModeSelection from "./components/selection/ModeSelection";
import ReligionSelection from "./components/selection/ReligionSelection";
import BookSelection from "./components/selection/bookselection";
import CompareSelection from "./components/selection/compareselection";

import ChatHeader from "./components/chat/ChatHeader";
import ChatMessages from "./components/chat/chatmessages";
import ChatInput from "./components/chat/ChatInput";
import LoadingBubble from "./components/chat/loadingbubble";

import useSelection from "./hooks/useSelection";
import useChat from "./hooks/useChat";



export default function Home(){


const {

step,

mode,

firstScripture,

secondScripture,

selectMode,

selectReligion,

selectFirst,

selectSecond,

goBack

}=useSelection();



const [religion,setReligion]
=
useState<any>(null);



const [book,setBook]
=
useState<any>(null);




const chat = useChat(
    religion?.name,
    book?.name
);





function handleReligion(value:any){

    setReligion(value);

    selectReligion(value);

}





function handleBook(value:any){

console.log("Religion name:", religion?.name);
console.log("Book name:", value?.name);

setBook(value);

selectFirst({
    ...value,
    religion: religion
});

}





function handleFirstCompare(value:any){

setReligion(value.religion);

setBook(value.book);


selectFirst(value);

}





function handleSecondCompare(value:any){


setReligion(value.religion);


setBook(value.book);


selectSecond(value);


}

const { status } = useSession();
const router = useRouter();

useEffect(() => {
  if (status === "unauthenticated") {
    router.push("/login");
  }
}, [status, router]);

if (status === "loading" || status === "unauthenticated") {
  return (
    <div className="min-h-screen flex items-center justify-center">
      Loading...
    </div>
  );
}




return(

<main


className="
min-h-screen
bg-gradient-to-br
from-purple-100
to-blue-100
flex
justify-center
items-center
p-6
"

>
    


<div

className="
w-full
max-w-4xl
bg-white
rounded-3xl
shadow-xl
p-6
"

>



{

step===1 &&

<ModeSelection

onSelect={selectMode}

/>

}





{

step===2 && mode==="single" &&

<ReligionSelection

onSelect={handleReligion}
onBack={goBack}

/>

}





{

step===2 && mode==="compare" &&

<CompareSelection

first={firstScripture}

onSelect={handleFirstCompare}
onBack={goBack}

/>

}





{

step===3 && mode==="single" && religion &&

<BookSelection

religion={religion}

onSelect={handleBook}
onBack={goBack}

/>

}





{

step===3 && mode==="compare" &&

<CompareSelection

first={firstScripture}

onSelect={handleSecondCompare}
onBack={goBack}

/>

}





{

step===4 &&

<div

className="
h-[650px]
flex
flex-col
"

>


<ChatHeader

title={
book
?
`${book.name}`
:
"MythVerse"
}
onBack={goBack}

/>



<ChatMessages

messages={chat.messages}

/>



{

chat.loading &&

<LoadingBubble/>

}



<ChatInput

onSend={chat.sendMessage}

/>



</div>


}




</div>


</main>


)

}