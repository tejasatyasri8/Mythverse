"use client";

import Card from "../common/card";
import PageHeader from "../common/pageheader";
import { RELIGIONS, BOOKS } from "../../utils/constants";

interface Props{

first:any;

onSelect:(scripture:any)=>void;

onBack?:()=>void;

}


export default function CompareSelection({

first,

onSelect,

onBack

}:Props){


return(

<div className="space-y-5">


<PageHeader

title={
first
?
"Select Second Scripture"
:
"Select First Scripture"
}

onBack={onBack}

/>


{
RELIGIONS.map((religion)=>(


<div key={religion.id}>


<h2 className="text-xl font-semibold text-gray-900 mb-3">

{religion.name}

</h2>


{

BOOKS[
religion.id as keyof typeof BOOKS
]
.map((book)=>(


<Card
    key={book.id}
    onClick={() => {

        if (
            first &&
            first.religion?.id === religion.id &&
            first.book?.id === book.id
        ) {
            return;
        }

        onSelect({
            religion,
            book
        });
    }}
>
    {book.name}
</Card>


))


}


</div>


))

}


</div>

)

}