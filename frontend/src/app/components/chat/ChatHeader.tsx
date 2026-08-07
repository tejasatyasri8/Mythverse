interface Props{

title?:string;

onBack?:()=>void;

}


export default function ChatHeader({

title="MythVerse",

onBack

}:Props){


return(

<div

className="
border-b
p-4
flex
justify-between
items-center
"

>

<div>

<h1

className="
text-2xl
text-black
font-bold
"

>

{title}

</h1>


<p

className="
text-gray-500
"

>

AI Knowledge Assistant

</p>

</div>


{

onBack &&

<button

onClick={onBack}

className="
bg-gray-200
hover:bg-gray-300
text-black
font-medium
px-4
py-2
rounded-xl
transition-colors
duration-200
"

>

← Back

</button>

}


</div>

)


}