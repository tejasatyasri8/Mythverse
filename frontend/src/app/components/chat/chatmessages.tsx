"use client";


import MessageBubble from "./MessageBubble";


interface Props{

messages:any[];

}



export default function ChatMessages({

messages

}:Props){



return(

<div

className="
flex-1
overflow-y-auto
p-5
"

>


{

messages.map((message,index)=>(


<MessageBubble

key={index}

role={message.role}

content={message.content}

/>


))


}



</div>

)


}