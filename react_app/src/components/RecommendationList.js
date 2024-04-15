import React, { useState, useEffect } from "react";
import axios from "axios";
import { Meteors } from './ui/meteors.tsx'; // Adjust the path as necessary based on your project structure
import clsx from "clsx";

function RecommendationsList({ recommendations, onRecommendations, setIsLoading, query, position, onTogglePosition }) {
  const [visibleEmbeds, setVisibleEmbeds] = useState(5); // State to track the number of visible embeds
  const [loaded, setLoaded] = useState({}); // State to track load status of each iframe
  const [showMeteors, setShowMeteors] = useState(false);




  const isPlaylist = recommendations && recommendations.hasOwnProperty("playlist"); // Check if recommendations is a playlist
  
  useEffect(() => {
    if (recommendations) {
      const initialVisibleEmbeds = isPlaylist ? 5 : 5; // Set initial number of visible embeds based on whether it's a playlist or not
      setVisibleEmbeds(initialVisibleEmbeds);
    }
  }, [recommendations]);

  
  const recommendationsArray = recommendations.recommended_ids || []; // Get the array of recommended ids
  console.log(recommendationsArray);

  useEffect(() => {
    if (recommendationsArray.length > 0 && Object.keys(loaded).length >= 5) {
      setShowMeteors(true);
    }
  }, [loaded, recommendationsArray]);

  // Define loading based on whether search was initiated and recommendations are not yet received
  if (!recommendations || recommendations.length === 0) {
    return null; // If no recommendations or empty array, return null
  }


  const handleLoad = (id) => {
    setLoaded((prev) => ({ ...prev, [id]: true })); // Update the loaded state for the specific iframe
  };

  const handleShuffle = async () => {
    setIsLoading(true);
    
    try {
      const response = await axios.get(`/RecEngine/recommend?link=${query}`);
      onRecommendations(response.data || []);
      
    } catch (error) {
      console.error("Error fetching search results", error);
      onRecommendations([]);
    }

    setIsLoading(false);
   
  };

  return (
    <div className="relative">
      <Meteors number={10} className="absolute inset-0 z-[-1]" />
      <div className={`mx-auto p-4 transition-transform duration-500 ${position === "left" ? "-translate-x-full" : ""}`}>
        {isPlaylist && recommendations.top_genres && recommendations.playlist ? (
          <h2 className="text-xl font-semibold text-gray-300 mb-4 text-center">
            <span className="text-gray-400 font-bold ">{recommendations.top_genres.join(", ")}</span> recommendations for{" "}
            <span className="text-yellow-600 font-bold italic">{recommendations.playlist}</span>
          </h2>
        ) : (
          <h2 className="text-xl font-semibold text-gray-300 mb-4 text-center">
            Here are some recommendations for <span className="text-yellow-600 font-bold italic">{recommendations.track}</span> by{" "}
            <span className="text-gray-300 font-bold italic">{recommendations.artist}</span>, released in {""}
            <span className="text-gray-400 font-semibold">{recommendations.release_date}</span>
          </h2>
        )}
        {/* <div className="recommendations-container p-4 bg-gradient-to-r from-gray-800 to-gray-600 shadow-2xl rounded-2xl transform overflow"> */}
        <div className="recommendations-container p-4 w-full bg-gradient-to-tr from-gray-900 via-gray-800 to-blue-900 shadow-2xl rounded-2xl relative  h-auto  overflow-hidden">
        {showMeteors && (
          <Meteors
            number={25}
            className="absolute inset-0 -translate-y-full"
            style={{ zIndex: -1 }}
          />
        )}
          <ul className="meteor space-y-4 z-10 relative">
            {recommendationsArray.slice(0, visibleEmbeds).map((id, index) => (
              <li
                key={index}
                className="w-full bg-gray-600 shadow-xl rounded-xl overflow-hidden"
              >
                <div className="w-full h-20 bg-gray-600 ">
                  <iframe
                    onLoad={() => handleLoad(id)}
                    className={`w-full h-20 rounded-lg ${loaded[id] ? "opacity-100" : "opacity-0"} transition-opacity duration-500 delay-200`}
                    src={`https://open.spotify.com/embed/track/${id}?utm_source=generator`}
                    style={{border: "none"}}
                    width="100%"
                    height="132"
                    allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
                    loading="eager"
                  ></iframe>
                </div>
              </li>
            ))}
          </ul>
          <div className="flex justify-between mt-4 px-2 py-1">
            {visibleEmbeds < recommendationsArray.length && (
              <button
                className="px-4 py-2 bg-custom-brown text-gray-200 shadow-xl font-bold rounded-full hover:bg-yellow-700 duration-300 hover:scale-105 transition-transform"
                onClick={() => setVisibleEmbeds((prev) => prev + 5)}
              >
                <img src="/plus.png" alt="Arrow" width={20} height={20}/>
              </button>
            )}
              <button
              className="px-4 py-2 bg-custom-brown text-gray-200 shadow-xl font-bold rounded-full hover:bg-yellow-700 duration-300 hover:scale-105 transition-transform"
              onClick={handleShuffle}
            >
              <img src="/arrow.png" alt="Arrow" style={{ transform: 'scaleX(0.9)' }} width={20} height={20}/>
            </button>
            
          </div>
        </div>
        <div className="absolute top-1/2 right-[-15px] transform -translate-y-1/2">
        <div className="relative inline-block">
          <div
            className="buttonDiv cursor-pointer text-gray-200 shadow-xl font-bold">
          
            <svg onClick={onTogglePosition} fill="#ffffff" width="28px" height="28px" className="transition-all hover:fill-custom-brown hover:scale-110 hover:rotate-6" viewBox="0 0 22 22" xmlns="http://www.w3.org/2000/svg" id="memory-music-note">
              <path d="M11 2H18V7H13V18H12V19H11V20H7V19H6V18H5V14H6V13H7V12H11V2M11 15H10V14H8V15H7V17H8V18H10V17H11V15Z" />
            </svg>
          
          </div>
          <div className="absolute top-1/2 left-[100%] transform -translate-y-1/2 px-2 py-1 text-custom-brown text-xs font-semi-bold opacity-0 pointer-events-none transition-opacity duration-300 tooltip">
            Unpack Me!
          </div>
        </div>
      </div>
      </div>

      
    </div>
  );
}

export default RecommendationsList;
