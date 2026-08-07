"use client";


import Card from "../common/card";
import {BOOKS} from "../../utils/constants";
import PageHeader from "../common/pageheader";


interface Props{

religion:any;

onSelect:(book:any)=>void;
onBack?:()=>void;

}



export default function BookSelection({

religion,

onSelect,

onBack

}:Props){



const books =
BOOKS[
religion.id as keyof typeof BOOKS
];




return(

<div className="space-y-5">


<PageHeader

title="Select Book"

onBack={onBack}

/>




{
books.map((book)=>(


<Card

key={book.id}

onClick={()=>onSelect(book)}

>


<h2 className="
text-xl
font-semibold
">

{book.name}

</h2>


</Card>


))

}



</div>


)


}