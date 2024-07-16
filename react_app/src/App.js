import React, { useState, useEffect, useRef, useCallback } from "react";
import SearchBar from "./components/SearchBar";
import RecommendationsList from "./components/RecommendationList";
import AuthButton from "./components/AuthButton";
import Navbar from "./components/Navbar";
import GradientBackground from "./components/GradientBackground";
import Footer from "./components/Footer";
import Greeting from "./components/Greeting";
import HomePage from "./components/HomePage";
import LoadingBars from "./components/LoadingBars";

import axios from "axios";

import "./App.css";

function App() {
  // State variables
  const [token, setToken] = useState("");
  const [recommendations, setRecommendations] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isShuffling, setIsShuffling] = useState(false);
  const [lastActionShuffle, setLastActionShuffle] = useState(false);

  const [isLocalLoading, setIsLocalLoading] = useState(false);
  const [query, setQuery] = useState("");
  const [recommendationPosition, setRecommendationPosition] =
    useState("center");
  const [showInfoContainer, setShowInfoContainer] = useState(false);
  const [animateOut, setAnimateOut] = useState(false); // For animating out the recommendation containter

  const [favoritedTracks, setFavoritedTracks] = useState([]);

  // Ref variables
  const prevPositionRef = useRef(recommendationPosition);

  // Fetch the token
  useEffect(() => {
    async function getToken() {
      try {
        console.log("Fetching token...");
        const response = await axios.get(
          `${process.env.REACT_APP_BACKEND_URL}/auth/token`,
          { withCredentials: true }
        );
        if (response.status === 200) {
          console.log("Fetched token:", response.data.access_token);
          setToken(response.data.access_token);
        } else {
          console.error("Failed to fetch token:", response.data);
        }
      } catch (error) {
        console.error("Error fetching token:", error);
      }
    }

    getToken();
  }, []);

  // Update Query State for Search and Shuffle
  const handleQueryChange = (newQuery) => {
    setQuery(newQuery);
  };

  // Update Recommendations State
  const handleRecommendations = (data) => {
    console.log("Setting recommendations", data);
    setRecommendations(data);
  };

  // Toggle recommendation position and show/hide info container
  const handleTogglePosition = useCallback(() => {
    setRecommendationPosition((prevPosition) =>
      prevPosition === "center" ? "left" : "center"
    );
  }, []);

  // Check if recommendation position has changed
  useEffect(() => {
    if (prevPositionRef.current !== recommendationPosition) {
      console.log(
        `Recommendation position changed from ${prevPositionRef.current} to ${recommendationPosition}`
      );
      // Toggle the visibility of the info container
      setShowInfoContainer((show) => !show);
      prevPositionRef.current = recommendationPosition;
    }
  }, [recommendationPosition]); // Dependency on recommendationPosition

  // Scroll to top when loading
  useEffect(() => {
    if (isLoading) {
      window.scrollTo({
        top: 250, // Adjust as needed to meet Search Bar
        behavior: "smooth",
      });
    }
  }, [isLoading]); // Dependency on isLoading

  const sendFavoritedTracks = async () => {
    try {
      console.log("Sending favorited tracks to backend:", favoritedTracks);
      // console.log(recommendations.id)
      const response = await axios.post("/favorited", {
        favoritedTracks,
        recommendationID: recommendations.id,
      });
      console.log(response);

      setFavoritedTracks([]);
    } catch (error) {
      console.error("Error sending favorited tracks to backend:", error);
    }
  };

  useEffect(() => {
    if (isLoading && favoritedTracks.length > 0) {
      sendFavoritedTracks();
    }
  }, [isLoading, favoritedTracks]);

  return (
    <div className="App z-1 bg-gray-900 flex flex-col min-h-screen">
      <GradientBackground
        className={`z-[0] ${token !== "" ? "fade-in-gradient" : "opacity-0"}`}
      />
      <Navbar
        AuthButton={
          <AuthButton
            token={token}
            setToken={setToken}
            setRecommendations={setRecommendations}
          />
        }
      />

      <div className="App-content z-1 flex-grow justify-center items-center min-h-screen relative over">
        {token === "" ? (
          <HomePage />
        ) : (
          <>
            <Greeting />
            <div className="main-container flex flex-col w-full mx-auto p-4 px-10">
              <div className="flex flex-col items-center">
                <div className="search-container mt-16 mb-4 w-full max-w-lg z-20">
                  <SearchBar
                    onRecommendations={handleRecommendations}
                    isLocalLoading={isLocalLoading}
                    setIsLocalLoading={setIsLocalLoading}
                    setIsLoading={setIsLoading}
                    onQueryChange={handleQueryChange}
                    setAnimateOut={setAnimateOut}
                    setLastActionShuffle={setLastActionShuffle}
                  />
                </div>
                <div className="recommendations-container w-full justify-center items-center z-10">
                  {isLoading && !isShuffling ? ( // Change setTimeout before this is true for animations
                    <LoadingBars className="mt-[30vh] top-[60%] left-[50%]  -translate-y-1/2 -translate-x-1/2" />
                  ) : (
                    <div className="relative">
                      <RecommendationsList
                        recommendations={recommendations}
                        onRecommendations={handleRecommendations}
                        // isLoading={isLoading}
                        setIsLoading={setIsLoading}
                        setIsLocalLoading={setIsLocalLoading}
                        query={query}
                        onQueryChange={handleQueryChange}
                        position={recommendationPosition}
                        onTogglePosition={handleTogglePosition}
                        setFavoritedTracks={setFavoritedTracks}
                        animateOut={animateOut}
                        setAnimateOut={setAnimateOut}
                        isShuffling={isShuffling}
                        setIsShuffling={setIsShuffling}
                        lastActionShuffle={lastActionShuffle}
                        setLastActionShuffle={setLastActionShuffle}
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
      <div className={`${token ? "mt-[22vh]" : "mt-[12vh]"} `}>
        <Footer />
      </div>
    </div>
  );
}

export default App;
