import './App.css';
import { useEffect, useState } from 'react';
import Home from './components/Home';
import {BrowserRouter, Routes, Route} from 'react-router-dom';

function App() {
  


  return (
    <div >
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
        </Routes>
      </BrowserRouter>
    </div>
  )
  
 
}

export default App;
