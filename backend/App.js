// File: src/App.js
// Last Modified: 2026-03-29
import React from 'react';
import MyInterface from './components/MyInterface';
import './App.css';
import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';

function App() {
    return (
        <Container maxWidth="md">
            <div className="App">
                <MyInterface />
            </div>
        </Container>
    );
}

export default App;