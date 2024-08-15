import React, { useState, useEffect } from "react";
import SearchBar from "./components/SearchBar";
import RecommendationsList from "./components/RecommendationList";
import Navbar from "./components/Navbar";
import GradientBackground from "./components/GradientBackground";
import Footer from "./components/Footer";
import Greeting from "./components/Greeting";
import HomePage from "./components/HomePage";
import LoadingBars from "./components/LoadingBars";

import axios from "axios";

import "./App.css";

const useMediaQuery = (query) => {
  const [matches, setMatches] = useState(false);

  useEffect(() => {
    const media = window.matchMedia(query);
    if (media.matches !== matches) {
      setMatches(media.matches);
    }
    const listener = () => setMatches(media.matches);
    window.addEventListener("resize", listener);
    return () => window.removeEventListener("resize", listener);
  }, [matches, query]);

  return matches;
};

function App() {
  const isMobile = useMediaQuery("(max-width: 768px)");
  const noop = () => {};

  // State variables
  const [token, setToken] = useState("");
  const [recommendations, setRecommendations] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isShuffling, setIsShuffling] = useState(false);
  const [lastActionShuffle, setLastActionShuffle] = useState(false);
  const [userPlaylistIds, setUserPlaylistIds] = useState([]); // Holds list of playlists, send to children

  const [isLocalLoading, setIsLocalLoading] = useState(false);
  const [query, setQuery] = useState("");

  const [animateOut, setAnimateOut] = useState(false); // For animating out the recommendation containter

  // Fetch the token
  useEffect(() => {
    if (token === "") {
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
    }
  }, [token]);

  // Update Query State for Search and Shuffle
  const handleQueryChange = (newQuery) => {
    setQuery(newQuery);
  };

  // Update Recommendations State
  const handleRecommendations = (data) => {
    console.log("Setting recommendations", data);
    setRecommendations(data);
  };

  // Scroll to top when loading
  useEffect(() => {
    if (isLoading) {
      window.scrollTo({
        top: 250, // Adjust as needed to meet Search Bar
        behavior: "smooth",
      });
    }
  }, [isLoading]); // Dependency on isLoading

  if (isMobile) {
    return (
      <div className="App z-1 bg-gray-900 flex flex-col min-h-screen">
        <Navbar
          token={noop}
          setToken={noop}
          setRecommendations={noop}
          isMobile={true}
        />
        <div className="phone-message">
          <h1 className="text-xl text-tbold  text-amber-500">
            Trading Fours is optimized for desktop and tablet.
          </h1>
          <br />
          <p className="text-md  text-gray-300">
            Please come back on a larger screen to enjoy the full experience.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="App z-1 bg-gray-900 flex flex-col min-h-screen">
      <GradientBackground
        className={`z-[0] ${token !== "" ? "fade-in-gradient" : "opacity-0"}`}
      />
      <Navbar
        token={token}
        setToken={setToken}
        setRecommendations={setRecommendations}
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
                    userPlaylistIds={userPlaylistIds}
                    setUserPlaylistIds={setUserPlaylistIds}
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
                        animateOut={animateOut}
                        setAnimateOut={setAnimateOut}
                        isShuffling={isShuffling}
                        setIsShuffling={setIsShuffling}
                        lastActionShuffle={lastActionShuffle}
                        setLastActionShuffle={setLastActionShuffle}
                        userPlaylistIds={userPlaylistIds}
                      />
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
