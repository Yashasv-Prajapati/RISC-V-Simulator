const express = require('express')
const fs = require('fs')
const app = express()
const cors = require('cors')
const { spawn, exec } = require('child_process');

let RunData;
try{
    RunData = require('./data_out.json');
}catch(err){
    RunData = [];
}
// middleware
app.use(cors())
app.use(express.json())


// An api endpoint that returns a short list of items
app.post('/api/load', (req, res) => {
    
    const textData = req.body.textData;

    // write to file named test.mem
    fs.writeFile('test.mem', textData, function (err) {
        if (err){
            throw err;
        };

        console.log('Saved!');

        let success = true;
        // spawn new child process to run the executable
        try{
            const child = spawn('myRISCVSim', ['./test.mem']);


            const resultData = "Data Loaded";
            // listen for errors
            child.stderr.on('data', (data) => {
                console.error(`stderr: ${data}`);
                // resultData = data;
                success = false;
            });

            child.stderr.on('error', (data) => {
                console.log(`stderr: ${data}`);
                // resultData = data;
                success = false;
            });

            // listen for the process to exit
            child.on('close', (code) => {
                console.log(`child process exited with code ${code}`);
                const DataToSend = {
                    resultData: resultData,
                    success:success
                }
            
                res.status(201).json(DataToSend)
            });
            
        }
        catch(err){
            console.log(err);
            success = false;
            const resultData = "Error";

            const DataToSend = {
                resultData: resultData,
                success:success
            }

            res.status(500).json(DataToSend)
        }
        });
})

app.get('/api/run', (req, res) => {

    let success = true;
    // spawn new child process to run the executable
    try{
        const totalObjects = RunData.length;
        const resultData = RunData[totalObjects-1];
    
        const DataToSend = {
            resultData: resultData,
            success:success
        }
    
        res.status(201).json(DataToSend)
    }
    catch(err){
        console.log(err);
        success = false;
        const resultData = "Error";

        const DataToSend = {
            resultData: resultData,
            success:success
        }

        res.status(500).json(DataToSend)
    }
    
    

})


app.post('/api/step', (req, res)=>{
    const stepNum = parseInt(req.body.stepNum);

    try{
        const resultData = RunData[stepNum];
        const success = true;
        const DataToSend = {
            resultData: resultData,
            success:success
        }
        res.status(201).json(DataToSend)

    }catch(err){
        const resultData = "Error";
        const success = false;
        const DataToSend = {
            resultData: resultData,
            success:success
        }
        res.status(500).json(DataToSend)

    }


})

app.post('/api/prev', (req, res)=>{
    const prevNum = parseInt(req.body.prevNum);

    try{
        const resultData = RunData[prevNum];
        const success = true;
        const DataToSend = {
            resultData: resultData,
            success:success
        }
        res.status(201).json(DataToSend)

    }catch(err){
        const resultData = "Error";
        const success = false;
        const DataToSend = {
            resultData: resultData,
            success:success
        }
        res.status(500).json(DataToSend)

    }
})


// api endpoint that returns memory of that location
app.post('/api/memory', (req,res)=>{
    const step = parseInt(req.body.stepNum)
    const MemoryLocation = parseInt(req.body.MemoryLocation)
    // console.log(step, MemoryLocation, RunData[RunData.length-1][`DataMem[${MemoryLocation}]`],)

    // accessing data-memory from that step
    if(!Number.isInteger(MemoryLocation)){
        return res.status(404).json({
            resultData:-1,
            success:false
        })
    }

    try{

        if(step==-100){
            // send last step data memory
            return res.status(201).json({
                resultData:RunData[RunData.length-1][`DataMem[${MemoryLocation}]`],
                success:true
            })
        }
        // console.log("HEY")
        // console.log(Number.isInteger(RunData[step][`DataMem[${MemoryLocation}]`]))

        if(Number.isInteger(RunData[step][`DataMem[${MemoryLocation}]`])){
            // console.log("INSIDER HERE")
            return res.status(201).json({
                resultData:RunData[step][`DataMem[${MemoryLocation}]`],
                success:true
            })
        }else{
            return res.status(201).json({
                resultData:0,
                success:true
            })
        }
    }catch(err){
        return res.status(500).json({
            resultData:-1,
            success:false
        })
    }


})

app.listen(process.env.PORT || 5000, () => {
  console.log(`Server listening on port ${process.env.PORT || 5000}`)
})
