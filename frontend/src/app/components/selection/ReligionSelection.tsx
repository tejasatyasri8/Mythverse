"use client";


import Card from "../common/card";
import {RELIGIONS} from "../../utils/constants";
import PageHeader from "../common/pageheader";


interface Props{

onSelect:(religion:any)=>void;
onBack?:()=>void;

}



export default function ReligionSelection({
onSelect,
onBack
}:Props){




return(

<div className="space-y-5">


<PageHeader

title="Select Religion"

onBack={onBack}

/>



{
RELIGIONS.map((religion)=>(


<Card

key={religion.id}

onClick={()=>
onSelect(religion)
}

>


<h2 className="
text-xl
font-semibold
text-gray-900
">

{religion.name}

</h2>


</Card>


))

}



</div>

)


}