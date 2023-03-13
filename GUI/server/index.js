const express = require('express')
const fs = require('fs')
const app = express()
const cors = require('cors')
const { spawn } = require('child_process');
const RunData = require('./data_out.json') ? require('./data_out.json') : [];

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
    });

    let success = true;
    // spawn new child process to run the executable
    try{
        const process = spawn('./myRISCVSim', ['./test.mem']);
        
        // listen for output
        // process.stdout.on('data', (data) => {
            //     console.log(`stdout: ${data}`);
            //     resultData = data;
            //     success = true;
            // });
        const resultData = "Data Loaded";
        // // listen for errors
        process.stderr.on('data', (data) => {
            console.error(`stderr: ${data}`);
            resultData = data;
            success = false;
        });
    
        // listen for the process to exit
        process.on('close', (code) => {
            console.log(`child process exited with code ${code}`);
        });

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


app.listen(process.env.PORT || 5000, () => {
  console.log(`Server listening on port ${process.env.PORT || 5000}`)
})
