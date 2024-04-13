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
      <div className="App-content flex-col justify-center items-center min-h-screen">
          { (token === '') ? (
          <Login/> 
          ) : (
          <div className="main-container max-w-2xl w-full mx-auto p-4">
            <div className="flex justify-end mb-4">
              <Logout setToken={setToken} setRecommendations={setRecommendations} />
            </div>
            <div className="search-container mb-8">
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