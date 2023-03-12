import './App.css';
import { useState } from 'react';

function App() {
  const [isRegister, setIsRegister] = useState(true)
  const [textData, setTextData] = useState(''); // text area data

  const registers = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31]; // 32 registers
  // console.log(registers)

  function Run(){
    if(textData===null || textData===undefined || textData===''){
      return;
    }
    fetch('http://localhost:5000/api/getData', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
        },
        body: JSON.stringify({textData})
        })
        .then(res => 
          res.json().then(data => {
            console.log(data);
            }
          )
        )



  }


  
  return (
    <div className='flex flex-row items-center'>
      {/* left */}
      <div className='w-2/3 m-2'>
        
        <div className='flex justify-between'>
          <button onClick={Run} className='p-2 m-4 rounded bg-blue-300 hover:bg-blue-400 active:bg-blue-300 shadow'>Run</button>
          <button className='p-2 m-4 rounded bg-blue-300 hover:bg-blue-400 active:bg-blue-300 shadow'>Reset</button>
        </div>

        <div>
          <textarea onChange={(e)=>{setTextData(e.target.value)}} className='w-full h-96 p-4 border-2 border-gray-300 rounded shadow'></textarea>
        </div>

      </div>

      {/* right */}
      <div className='w-1/3 h-screen overflow-hidden border border-gray-400'>

        <div className='flex justify-center'>
          <button className='p-2 m-4 rounded bg-blue-300 hover:bg-blue-400 active:bg-blue-300 shadow' onClick={()=>{setIsRegister(true)}}>Register</button>
          <button className='p-2 m-4 rounded bg-blue-300 hover:bg-blue-400 active:bg-blue-300 shadow' onClick={()=>{setIsRegister(false)}}>Memory</button>
        </div>
        {
          isRegister?
          <div className='overflow-y-auto max-h-full' style={{ maxHeight: 'calc(100% - 100px)' }}>
            {
              registers.map((item, index)=>{
                return (
                  <p className='p-1 bg-gray-400 m-1 shadow'>
                    X{item}
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
              <input type='text' className='border border-black '/>
              <button className='p-2 m-4 rounded bg-blue-300 hover:bg-blue-400 active:bg-blue-300 shadow' > Submit </button>
            </div>
            
            <div>

            </div>
          </div>
        }
      </div>
    </div>
  );
}

export default App;
