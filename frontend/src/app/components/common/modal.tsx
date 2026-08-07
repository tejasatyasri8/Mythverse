interface Props{

children:React.ReactNode;

open:boolean;

}


export default function Modal({
children,
open
}:Props){


if(!open)
return null;



return(

<div

className="
fixed
inset-0
flex
items-center
justify-center
bg-black/40
"

>


<div

className="
bg-white
rounded-xl
p-6
"

>

{children}

</div>


</div>

)


}