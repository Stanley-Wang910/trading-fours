import React, { useState, useEffect } from 'react';
import Login from './components/Login'
import SearchBar from './components/SearchBar';
import RecommendationsList from './components/RecommendationList';
import Logout from './components/Logout';
import './App.css';

function App() {

  const [token, setToken] = useState('');
  const [recommendations, setRecommendations] = useState([]);

  useEffect(() => {

    async function getToken() {
      const response = await fetch('/auth/token');
      const json = await response.json();
      setToken(json.access_token);
    }

    getToken();

  }, []);

  const handleRecommendations = (data) => {
    setRecommendations(data);
  }

  return (
  <div className="App">
      <div className="App-content">
          { (token === '') ? (
          <Login/> 
          ) : (
          <div className="main-container">
            <Logout setToken={setToken} setRecommendations={setRecommendations} />
            <div className="search_container">
              <SearchBar onRecommendations={handleRecommendations}/> 
            </div>
            <div className="recommendations-container">
              <RecommendationsList recommendations={recommendations}/>
            </div>
          </div>
          )}
      </div>
  </div>
  );
}

export default App;