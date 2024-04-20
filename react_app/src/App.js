import React, { useState, useEffect, useRef, useCallback } from "react";
import Login from "./components/Login";
import SearchBar from "./components/SearchBar";
import RecommendationsList from "./components/RecommendationList";
import Logout from "./components/Logout";
import Navbar from "./components/Navbar";
import GradientBackground from "./components/GradientBackground";
import Footer from "./components/Footer";
import PlaylistDropdown from "./components/PlaylistDropdown";

import "./App.css";


function App() {
  // State variables
  const [token, setToken] = useState("");
  const [recommendations, setRecommendations] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [query, setQuery] = useState("");
  const [recommendationPosition, setRecommendationPosition] = useState("center");
  const [showInfoContainer, setShowInfoContainer] = useState(false);

  // Ref variables
  const prevPositionRef = useRef(recommendationPosition);

  // Fetch the token
  useEffect(() => {
    async function getToken() {
      const response = await fetch("/auth/token");
      const json = await response.json();
      setToken(json.access_token);
    }

    getToken();
  }, []);

  // Update Query State for Search and Shuffle
  const handleQueryChange = (newQuery) => {
    setQuery(newQuery);
  };
  
  // Update Recommendations State
  const handleRecommendations = (data) => {
    setRecommendations(data);
  };
  
  // Toggle recommendation position and show/hide info container 
  const handleTogglePosition = useCallback(() => {
    setRecommendationPosition((prevPosition) => (prevPosition === "center" ? "left" : "center"));
  }, []);

  // Check if recommendation position has changed
  useEffect(() => {
    if (prevPositionRef.current !== recommendationPosition) {
      console.log(`Recommendation position changed from ${prevPositionRef.current} to ${recommendationPosition}`);
      // Toggle the visibility of the info container
      setShowInfoContainer(show => !show);
      prevPositionRef.current = recommendationPosition;
    }
  }, [recommendationPosition]); // Dependency on recommendationPosition
  
  // Scroll to top when loading
  useEffect(() => {
    if (isLoading) {
      window.scrollTo({
        top: 0,
        behavior: "smooth"
      });
    }
  }, [isLoading]);  // Dependency on isLoading


  return (
    <div className="App z-1 bg-gradient-to-br from-custom_dark to-gray-900 flex flex-col min-h-screen">
      
      <div className="App-content z-1 flex-grow justify-center items-center min-h-screen relative over">
      <GradientBackground className='z-[0]'/>
        {token === "" ? (
          <Login />
        ) : (
          <>
          <div>
            <Navbar LogoutComponent={<Logout setToken={setToken} setRecommendations={setRecommendations} />} />
          </div>
          <div className="main-container flex flex-col max-w-2xl w-full mx-auto p-4">
            <div className="flex flex-col items-center">
              <div className="search-container mt-16 mb-1 w-full max-w-lg">
                <SearchBar onRecommendations={handleRecommendations} setIsLoading={setIsLoading} onQueryChange={handleQueryChange} />
              </div>
              <div className="recommendations-container w-full max-w-2xlflex justify-center items-center z-10">
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
                  <div className="relative">
                    <RecommendationsList
                      recommendations={recommendations}
                      onRecommendations={handleRecommendations}
                      setIsLoading={setIsLoading}
                      query={query}
                      position={recommendationPosition}
                      onTogglePosition={handleTogglePosition}
                    />
                    {showInfoContainer && (
                      <div
                        className="additional-container absolute right-0 top-1/2 transform -translate-y-1/2 w-1/4 bg-white p-4 shadow-lg"
                        style={{
                          transform: `translateX(${
                            recommendationPosition === "left" ? "100%" : "0"
                          })`,
                        }}
                      >
                        <p>Recommendation info Coming</p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        </>
        )}

      </div>
        <Footer />
      {/* <footer className="z-[1] bg-custom_dark bg-opacity-60 py-4 border-b border-gray-700 backdrop-filter backdrop-blur-md font-semibold p-4 pb-6 text-center text-gray-400">
        <p>&copy; {new Date().getFullYear()} trading fours, by stanley wang</p>
      </footer> */}
    </div>
  );
}

export default App;
