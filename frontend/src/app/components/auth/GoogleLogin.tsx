"use client";

import { signIn } from "next-auth/react";

export default function GoogleLogin() {
  return (
    <button
      onClick={() =>
        signIn("google", {
            callbackUrl: "/",
        })
    }
      className="bg-blue-600 text-white px-5 py-2 rounded-xl"
    >
      Sign in with Google
    </button>
  );
}