"use client";

import {useState} from "react";


export default function useSelection(){
    console.log(goBack);

    const [step,setStep] = useState(1);

    const [mode,setMode] = useState<string>("");

    const [firstScripture,setFirstScripture] = useState<any>(null);

    const [secondScripture,setSecondScripture] = useState<any>(null);



    function selectMode(value:string){

        setMode(value);

        setStep(2);

    }



    function selectReligion(value:any){

        setStep(3);

    }



    function selectFirst(value:any){

        setFirstScripture(value);

        if(mode==="compare"){
            setStep(3);
        }
        else{
            setStep(4);
        }

    }



    function selectSecond(value:any){

        setSecondScripture(value);

        setStep(4);

    }

    function goBack(){

    if(step > 1){

        setStep(step - 1);

    }

}

    function reset(){

        setStep(1);
        setMode("");
        setFirstScripture(null);
        setSecondScripture(null);

    }



    return {

        step,
        mode,

        firstScripture,
        secondScripture,

        selectMode,
        selectReligion,
        selectFirst,
        selectSecond,

        goBack,

        reset

    };

}