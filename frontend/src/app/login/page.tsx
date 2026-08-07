"use client";

import GoogleLogin from "../components/auth/GoogleLogin";

export default function LoginPage(){

return(

<main
className="
min-h-screen
bg-gradient-to-br
from-purple-100
to-blue-100
flex
items-center
justify-center
"
>

<div
className="
bg-white
rounded-3xl
shadow-xl
p-10
text-center
"
>

<h1
className="
text-3xl
font-bold
text-black
mb-6
"
>
Welcome to MythVerse
</h1>


<p className="mb-6 text-gray-600">
Sign in to explore scriptures with AI
</p>


<GoogleLogin />


</div>

</main>

)

}