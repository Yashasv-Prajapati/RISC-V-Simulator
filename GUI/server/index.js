const express = require('express')
const fs = require('fs')
const app = express()
const cors = require('cors')
const { spawn } = require('child_process');

// middleware
app.use(cors())
app.use(express.json())


// An api endpoint that returns a short list of items
app.post('/api/getData', (req, res) => {

    const textData = req.body.textData;

    // write to file named test.mem
    fs.writeFile('test.mem', textData, function (err) {
        if (err) throw err;
        console.log('Saved!');
    });

    const resultData = "";
    const success = true;
    // spawn new child process to run the executable
    const process = spawn('./myRISCVSim', ['./test.mem']);
    
    // listen for output
    process.stdout.on('data', (data) => {
        console.log(`stdout: ${data}`);
        resultData = data;
        success = true;
    });
    
    // listen for errors
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
})


app.listen(process.env.PORT || 5000, () => {
  console.log(`Server listening on port ${process.env.PORT || 5000}`)
})
