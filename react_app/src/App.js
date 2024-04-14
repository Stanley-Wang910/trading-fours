import React, { useState, useEffect } from "react";
import Login from "./components/Login";
import SearchBar from "./components/SearchBar";
import RecommendationsList from "./components/RecommendationList";
import Logout from "./components/Logout";
import "./App.css";

function App() {
  const [token, setToken] = useState("");
  const [recommendations, setRecommendations] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    async function getToken() {
      const response = await fetch("/auth/token");
      const json = await response.json();
      setToken(json.access_token);
    }

    getToken();
  }, []);

  const handleRecommendations = (data) => {
    setRecommendations(data);
  };

  return (
    <div className="App bg-custom_dark">
      <div className="App-content flex-col justify-center items-center min-h-screen relative">
        {token === "" ? (
          <Login />
        ) : (
          <div className="main-container max-w-2xl w-full mx-auto p-4">
            <Logout
                setToken={setToken}
                setRecommendations={setRecommendations}
            />
            <div className="search-container mb-2">
              <SearchBar onRecommendations={handleRecommendations}setIsLoading={setIsLoading} />
            </div>
              <div className="recommendations-container">
                {isLoading ? (
                  <div className="loader">
                    <div className="bar1"></div>
                    <div className="bar2"></div>
                    <div className="bar3"></div>
                    <div className="bar4"></div>
                    <div className="bar5"></div>
                    <div className="bar6"></div>
                  </div>
                ) : (
                  <RecommendationsList recommendations={recommendations} />
                )}
              </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
