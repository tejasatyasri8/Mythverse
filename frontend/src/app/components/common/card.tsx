interface Props{

children:React.ReactNode;

onClick?:()=>void;

}


export default function Card({
children,
onClick
}:Props){


return(

<div

onClick={onClick}

className="
w-full
p-6
rounded-2xl
bg-white
border
border-purple-200
shadow-md
cursor-pointer
text-gray-900
hover:bg-purple-50
hover:border-purple-400
transition
"

>

{children}

</div>

)

}