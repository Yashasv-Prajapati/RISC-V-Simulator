import React from 'react'
import Hazards from './Hazards'
import { useState } from 'react';

function Simulator({instructions, setCheckRun, setRegisterData, setIsEditor, textData, stepNum,setStepNum, setInstructionString, setInstructions }) {


    const [pipeline, setPipeline] = useState(false);
    const [dataForwarding, setDataForwarding] = useState(false);
    const [runbtnClicked, setRunbtnClicked] = useState(false); // run button clicked
    const [prevNum, setPrevNum] = useState(0); // previous number

    function Run(){

        setRunbtnClicked(true);
        setCheckRun(true);
        fetch("http://localhost:5000/api/run", {
            method: 'GET',
            headers: {
            'Content-Type': 'application/json'
            }
        })
        .then(res => 
            res.json().then(data => {
            if(data.success){
                console.log(data);
                const regArray = [];
                for(let i=0;i<32;i++){
                regArray.push(parseInt(data.resultData[`X[${i}]`]));
                }
                setRegisterData(regArray);
            }

            }
            ).catch(err=>console.log(err))
        ).catch(err=>{
            console.log(err)
        })

    }

    function LoadData(){
        if(textData===null || textData===undefined || textData===''){
        return;
        }

        setIsEditor(false);
        fetch("http://localhost:5000/api/load", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({textData})
        })
        .then(res => 
        res.json().then(data => {
            if(data.success){

            console.log(data);
            // const regArray = [];
            // for(let i=0;i<32;i++){
            //   regArray.push(parseInt(data.resultData[`X[${i}]`]));
            // }
            // setRegisterData(regArray);
            }

        }
        ).catch(err=>console.log(err))
        ).catch(err=>{
        console.log(err)
        })
    }

    function Step(){
        if(stepNum===null || stepNum===undefined){
        console.log("UNDEFINED OR NULL\n");
        return;
        }
        // set run button clicked to false because we want to show step by step instructions
        setCheckRun(false);

        console.log("StepNum is", stepNum);
        setRunbtnClicked(true);

        fetch("http://localhost:5000/api/step", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({stepNum})
        })
        .then(res => 
        res.json().then(data => {
            if(data.success){
            console.log("YESSSS")
            console.log(data);
            const regArray = [];
            for(let i=0;i<32;i++){
                regArray.push(parseInt(data.resultData[`X[${i}]`]));
            }
            setRegisterData(regArray);
            setStepNum(stepNum+1);
            setPrevNum(stepNum);
            }

        }
        ).catch(err=>console.log(err))
        ).catch(err=>{
        console.log(err)
        })

    }

    function Previous(){
        if(prevNum===null || prevNum===undefined){
        return;
        }

        // set run button clicked to false because we want to show step by step instructions
        setCheckRun(false);

        setRunbtnClicked(true);
        console.log("Prev is ", prevNum);

        const prev = prevNum-1<=0 ? 0:prevNum-1; // check for negative values
        fetch("http://localhost:5000/api/prev", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({'prevNum':`${prevNum-1<=0 ? 0: prevNum-1}`})
        })
        .then(res =>
        res.json().then(data => {
            if(data.success){

            console.log(data);
            const regArray = [];
            for(let i=0;i<32;i++){
                regArray.push(parseInt(data.resultData[`X[${i}]`]));
            }
            setRegisterData(regArray);
            setPrevNum(prevNum-1);
            setStepNum(prevNum)
            }

        })
        .catch(err=>console.log(err))
        )
        .catch(err=>{
            console.log(err)
        }
        )
    }

    function Reset(){
        setRunbtnClicked(false);
        setStepNum(0);
        setPrevNum(0);
        setRegisterData([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]);
        setInstructionString("");
        setInstructions([]);
    }





  return (
    <div >
        <div className='flex justify-center'>
            {/* Run */}
            <button onClick={Run} className='p-2 m-4 rounded bg-orange-300 hover:bg-orange-400 active:bg-orange-300 shadow'>Run</button>
            
            {/* Step */}
            <button onClick={Step} className='p-2 m-4 rounded bg-orange-300 hover:bg-orange-400 active:bg-orange-300 shadow'>Step</button>

            {/* Previous */}
            <button onClick={Previous} className='p-2 m-4 rounded bg-orange-300 hover:bg-orange-400 active:bg-orange-300 shadow'>Previous</button>

            {/* Reset */}
            <button onClick={Reset} disabled={runbtnClicked?false:true} className='p-2 m-4 rounded bg-orange-300 hover:bg-orange-400 active:bg-orange-300 shadow'>Reset</button>
            
            {/* Pipeline */}
            <div className='flex justify-center items-center border-4 m-2 p-2 border-orange-300 rounded '>
                <label htmlFor="pipelineLabel" className='p-2'>Pipeline</label>
                <input type="checkbox" name="pipeline" onChange={(e)=>{setPipeline(e.target.checked)}} className='' id="pipeline" />
            </div>
            
            {/* DataForwarding */}
            <div className='flex justify-center items-center border-4 m-2 p-2 border-orange-300 rounded '>
                <label htmlFor="pipelineLabel" >Data-Forwarding</label>
                <input type="checkbox" name="dataForwarding" onChange={(e)=>{setDataForwarding(e.target.checked)}} className='' id="dataForwarding" />
            </div>
        </div>

        <div className='w-full h-screen flex flex-row border-8 border-black'>
            <div className='overflow-y-auto max-h-full w-1/4' style={{ maxHeight: 'calc(100% - 100px)' }}>

                {
                    instructions.map((item, index)=>{
                        return (
                            <p className='p-1 bg-gray-400 m-1 shadow rounded'>
                            {item}
                        </p>
                        )
                    })
                }
            </div>
            <div className='w-1/4 flex border-2 border-blue-300 rounded'>
                <Hazards/>
            </div>
        </div>

    </div>
  )
}

export default Simulator