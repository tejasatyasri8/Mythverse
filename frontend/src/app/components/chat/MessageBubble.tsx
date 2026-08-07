"use client";

import Markdown from "react-markdown";


interface Props{

role:string;

content:string;

}



export default function MessageBubble({

role,

content

}:Props){


const isUser = role==="user";


return(

<div

className={

isUser

?

"flex justify-end my-3"

:

"flex justify-start my-3"

}

>


<div

className={

isUser

?

"bg-blue-800 text-white p-4 rounded-2xl max-w-xl"

:

"bg-gray-200 text-gray-100 p-5 rounded-2xl max-w-xl"

}

>


{

isUser

?

content

:

<Markdown

components={{

h2:({children})=>(

<div

className="
text-lg
font-bold
text-yellow-400
mt-4
mb-2
"

>

{children}

</div>

),


p:({children})=>(

<p

className="
text-gray-800
leading-relaxed
mb-3
"

>

{children}

</p>

),


li:({children})=>(

<li

className="
ml-5
list-disc
text-gray-200
"

>

{children}

</li>

)

}}

>

{content}

</Markdown>

}


</div>


</div>


)

}