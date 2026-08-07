interface Props{

title:string;

onBack?:()=>void;

}


export default function PageHeader({

title,

onBack

}:Props){


return(

<div

className="
flex
justify-between
items-center
mb-6
"

>

<h1

className="
text-3xl
font-bold
text-black
"

>

{title}

</h1>


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