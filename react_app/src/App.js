import React, { useState, useEffect } from 'react';
import Login from './components/Login'
import SearchBar from './components/SearchBar';
import './App.css';

function App() {

  const [token, setToken] = useState('');

  useEffect(() => {

    async function getToken() {
      const response = await fetch('/auth/token');
      const json = await response.json();
      setToken(json.access_token);
    }

    getToken();

  }, []);

  return (
    <div className="App-content">
        { (token === '') ? <Login/> : <SearchBar /> }
    </div>
  );
}

export default App;