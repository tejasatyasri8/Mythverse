"use client";


import {useState} from "react";


interface Props{

onSend:(text:string)=>void;

}



export default function ChatInput({

onSend

}:Props){



const [text,setText]
=
useState("");



function send(){


if(!text.trim())
return;


onSend(text);


setText("");

}



return(

<div

className="
flex
gap-3
p-4
border-t
"

>



<input


value={text}


onChange={
e=>setText(e.target.value)
}



onKeyDown={
e=>{

if(e.key==="Enter")
send();

}

}


placeholder="
Ask about scriptures...
"


className="
flex-1
border
border-gray-600
rounded-xl
p-3
bg-gray-300
text-black
placeholder-black
"


/>



<button

onClick={send}

className="
bg-black
text-white
px-6
rounded-xl
"

>

Send

</button>



</div>


)


}