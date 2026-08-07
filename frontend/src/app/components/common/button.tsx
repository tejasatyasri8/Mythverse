interface Props{

children:React.ReactNode;

onClick?:()=>void;

}


export default function Button({
children,
onClick
}:Props){


return(

<button

onClick={onClick}

className="
px-6
py-3
rounded-xl
bg-black
text-white
hover:opacity-80
transition
"

>

{children}

</button>

)

}