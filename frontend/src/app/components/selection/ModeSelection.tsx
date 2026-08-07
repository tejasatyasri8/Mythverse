"use client";


import Card from "../common/card";


interface Props{

onSelect:(mode:string)=>void;

}


export default function ModeSelection({
onSelect
}:Props){


return(

<div className="space-y-5">


<h1 className="
text-3xl
font-bold
text-purple-900
">

Choose Mode

</h1>



<Card
onClick={()=>onSelect("single")}
>

<h2 className="text-xl font-semibold">
Single Scripture
</h2>

<p>
Ask questions from one scripture
</p>

</Card>



<Card

onClick={()=>onSelect("compare")}

>

<h2 className="text-xl font-semibold">
Compare Scriptures
</h2>

<p>
Compare teachings from two scriptures
</p>

</Card>

</div>

)

}