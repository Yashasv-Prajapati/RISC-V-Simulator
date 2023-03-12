const express = require('express')
const fs = require('fs')
// const path = require('path')
const app = express()
const cors = require('cors')
const { exec } = require('child_process');

// Serve static files from the React app
// app.use(express.static(path.join(__dirname, 'client/build')))
app.use(cors())
// An api endpoint that returns a short list of items

app.post('/api/getData', (req, res) => {
    const textData = req.body.textData;

    // write to file named test.mem
    fs.writeFile('test.mem', textData, function (err) {
        if (err) throw err;
        console.log('Saved!');
    });

    // let rawdata = fs.readFileSync('data.json')
    exec('./myRISCVSim test.mem', (err, stdout, stderr) => {
        if(err){
            console.log(`exec error: ${err}`);
            return;
        }else{
            console.log(`stdout: ${stdout}`);
            console.log(`stderr: ${stderr}`);
        }
    
    })
    res.status(201).json(data)
})


app.listen(process.env.PORT || 5000, () => {
  console.log(`Server listening on port ${process.env.PORT || 5000}`)
})
