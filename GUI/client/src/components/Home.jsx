import React from 'react'
import { useEffect, useState } from 'react';
import Hazards from './Hazards';
import Simulator from './Simulator';

function Home() {

    const [isRegister, setIsRegister] = useState(true)
    const [isEditor, setIsEditor] = useState(true)
    const [textData, setTextData] = useState(''); // text area data
    const [stepNum, setStepNum] = useState(0); // step number
    const [instructions, setInstructions] = useState([]); // instructions
    const[instructionString, setInstructionString] = useState(''); // instruction string
    const [registerData, setRegisterData] = useState([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]); // register data
    const [MemoryLocation, setMemoryLocation] = useState('');
    const [MemoryDataToShow, setMemoryDataToShow]= useState(0);
    const [checkRun, setCheckRun]= useState(false);

    const sampleInput = "Sample Input \n0x0 0x00900093 \n0x4 0x00908113 \n0x8 0x002081b3 \n0xc 0x00218233 \n0x10 0x05a08293 \n0x14 0x05508313 \n0x18 0x05b08393 \n0x1c 0x00820613 \n0x20 0x04108a13 \n0x24 0x007a0c93 \n0x2c 0xfffffffb";


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

      function TextAreaChanges(e){
        setTextData(e.target.value)
        setInstructionString(e.target.value);
        setInstructions(e.target.value.split('\n'));
      }
    
      function getStepMemoryData(){
        if(MemoryLocation==undefined || MemoryLocation=="" || MemoryLocation==null){
          window.alert("Enter valid memory location")
          return;
        }
    
        fetch('http://localhost:5000/api/memory',{
          method:'post',
          headers:{
            'Content-Type':'application/json'
          },
          body:JSON.stringify({stepNum,MemoryLocation})
        }).then(response=>{
          response.json().then((data)=>{
            if(data.success){
              setMemoryDataToShow(data.resultData)
            }else{
              setMemoryDataToShow(-1);
            }
          })
        })
      }
    
      function getRunMemoryData(){
        if(MemoryLocation==undefined || MemoryLocation=="" || MemoryLocation==null){
          window.alert("Enter valid memory location")
          return;
        }
    
        fetch('http://localhost:5000/api/memory',{
          method:'post',
          headers:{
            'Content-Type':'application/json'
          },
          body:JSON.stringify({stepNum:-100,MemoryLocation})
        }).then(response=>{
          response.json().then((data)=>{
            if(data.success){
              setMemoryDataToShow(data.resultData)
            }else{
              setMemoryDataToShow(-1);
            }
          })
        })
      }
    
      function getMemoryData(){
        if(checkRun){
          console.log("RUNNIGN THIS")
          getRunMemoryData();
        }else{
          getStepMemoryData();
        }
      }
      useEffect(()=>{
    
      }, [registerData])


    return (
    <div className='flex flex-row items-center' >
        {/* left */}
        <div className='w-4/5 m-2' >
        <div className='flex justify-center'>
            <button className='p-2 m-4 rounded bg-blue-300 hover:bg-blue-400 active:bg-blue-300 shadow' onClick={()=>{setIsEditor(true)}}>Editor</button>
            <button className='p-2 m-4 rounded bg-blue-300 hover:bg-blue-400 active:bg-blue-300 shadow' onClick={LoadData}>Simulator</button>
        </div>
        {
        isEditor?
        
            <div>
            <div>
                <textarea onChange={TextAreaChanges} placeholder={sampleInput} value={instructionString} className='w-full h-96 p-4 border-2 border-gray-300 rounded shadow'></textarea>
            </div>
            </div>
        
        :

        <Simulator 
          instructions={instructions} 
          setInstructionString={setInstructionString}
          setInstructions={setInstructions} 
          setRegisterData={setRegisterData} 
          setIsEditor={setIsEditor} 
          stepNum={stepNum} 
          setStepNum={setStepNum} 
          setCheckRun={setCheckRun} 
          textData={textData}
        />
        
        }
        </div>

        {/* right */}
        <div className='w-1/5 h-screen overflow-hidden border-8 border-black'>

            <div className='flex justify-center'>
                <button className='p-2 m-4 rounded bg-blue-300 hover:bg-blue-400 active:bg-blue-300 shadow' onClick={()=>{setIsRegister(true)}}>Register</button>
                <button className='p-2 m-4 rounded bg-blue-300 hover:bg-blue-400 active:bg-blue-300 shadow' onClick={()=>{setIsRegister(false)}}>Memory</button>
            </div>
        {
            isRegister?
            <div className='overflow-y-auto max-h-full' style={{ maxHeight: 'calc(100% - 100px)' }}>
            {
                registerData.map((item, index)=>{
                return (
                    <p className='p-1 bg-gray-400 m-1 shadow'>
                    X{index}:  {item}
                    </p>
                )  
                
                }
                )
            } 
            </div>
            :
            <div className='flex justify-center flex-col p-2'>
            <div>
                <label>Enter the location which you want to access</label>
                <input onChange={(e)=>{setMemoryLocation(e.target.value)}} type='text' className='border border-black '/>
                <button onClick={getMemoryData} className='p-2 m-4 rounded bg-blue-300 hover:bg-blue-400 active:bg-blue-300 shadow' > Submit </button>
            </div>
            
            <div>
                {MemoryDataToShow}
            </div>
            </div>
        }
        </div>
    </div>
    );
}

export default Home