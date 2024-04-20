import React, { useState, useEffect, useRef, useCallback} from "react";
import axios from "axios";
import { Meteors } from './ui/meteors.tsx'; // Adjust the path as necessary based on your project structure
import clsx from "clsx";


function RecommendationsList({ recommendations, onRecommendations, setIsLoading, query, position, onTogglePosition }) {
  //State variables
  const [visibleEmbeds, setVisibleEmbeds] = useState(5); // State to track the number of visible embeds
  const [loaded, setLoaded] = useState([]);
  const [showMeteors, setShowMeteors] = useState(false);
  const [containerHeight, setContainerHeight] = useState(575); // Set the starting height
  const [clickedLikes, setClickedLikes] = useState([]);

  
  // Constants
  const maxHeight = 3000; // Set the maximum height for recommendations container
  const extendRec = 500
  // Memoized callbakc to handle loading more embeds
  const handleLoadMore = useCallback(() => {
    setVisibleEmbeds((prev) => prev + 5);
    setContainerHeight((prev) => prev + extendRec, maxHeight);
  
   
  }, [maxHeight]);

  // Handler for clicking like
  const handleClickLike = (index) => {
    setClickedLikes((prevClickedLikes) => {
      if (prevClickedLikes.includes(index)) {
        return prevClickedLikes.filter((likeIndex) => likeIndex !== index);
      } else {
        return [...prevClickedLikes, index];
      }
    });
  };

  // Check if recommendations is a playlist
  const isPlaylist = recommendations && recommendations.hasOwnProperty("playlist"); // Check if recommendations is a playlist
  
  // Set the initial number of visible embeds
  useEffect(() => {
    if (recommendations) {
      const initialVisibleEmbeds = isPlaylist ? 5 : 5; // Set initial number of visible embeds based on whether it's a playlist or not
      setVisibleEmbeds(initialVisibleEmbeds);
    }
  }, [recommendations]);

  // Get the array of recommended ids
  const recommendationsArray = recommendations.recommended_ids || []; // Get the array of recommended ids
  console.log(recommendationsArray);

  // Load meteors when recommendations are received
  useEffect(() => {
    if (recommendationsArray.length > 0 && Object.keys(loaded).length >= 5) {
      setTimeout(() => {
        setShowMeteors(true);
      }, 2000);
    }
  }, [loaded, recommendationsArray]);


  // Define loading based on whether search was initiated and recommendations are not yet received
  if (!recommendations || recommendations.length === 0) {
    return null; // If no recommendations or empty array, return null
  }

  // Handler for loading embeds
  const handleLoad = (index) => {
    const embedElements = document.querySelectorAll(".embed");
    if (embedElements[index]) {
      embedElements[index].classList.add("active");
    }
  
    // Set a timeout to mark the embed as loaded after 1 second
    setTimeout(() => {
      setLoaded((prev) => [...prev, index]);
    }, 100); // For animation timing
  };


  

  // Handler for shuffling recommendations
  const handleShuffle = async () => {
    setIsLoading(true);
    
    try {
      const response = await axios.get(`/recommend?link=${query}`);
      onRecommendations(response.data || []);
    
      
    } catch (error) {
      console.error("Error fetching search results", error);
      onRecommendations([]);
    }

    setIsLoading(false);
  };

  return (
    <div className="relative">
      <div className={`mx-auto p-4 transition-transform duration-500 ${position === "left" ? "-translate-x-full" : ""}`}>
        {isPlaylist && recommendations.top_genres && recommendations.playlist ? (
          <h2 className="text-xl font-semibold text-gray-400 mb-4 text-center">
            <span className="text-gray-400 font-bold ">{recommendations.top_genres.join(", ")}</span> recommendations for{" "}
            <span className="text-yellow-600 font-bold italic">{recommendations.playlist}</span>
          </h2>
        ) : (
          <h2 className="text-xl font-semibold text-gray-400 mb-4 text-center">
            Here are some recommendations for <span className="text-yellow-600 font-bold italic">{recommendations.track}</span> by{" "}
            <span className="text-gray-400 font-bold italic">{recommendations.artist}</span>, released in {""}
            <span className="text-gray-400 font-semibold">{recommendations.release_date}</span>
          </h2>
        )}
        {/* <div className="recommendations-container p-4 bg-gradient-to-r from-gray-800 to-gray-600 shadow-2xl rounded-2xl transform overflow"> */}
        <div className="recommendations-container p-5 w-full bg-gradient-to-tr from-gray-900 via-gray-800 to-blue-900 shadow-2xl rounded-2xl relative overflow-hidden container-transition" style={{ '--container-height': `${containerHeight}px` }}>
        {showMeteors && (
          <Meteors
            number={25}
            className="absolute inset-0 -translate-y-[4px]"
            style={{ zIndex: -1 }}
          />
        )}
          <ul className="meteor space-y-5 z-10 relative">
            {recommendationsArray.slice(0, visibleEmbeds).map((id, index) => (
              <li
                key={index}
                className="w-full bg-transparent overflow-visible relative flex group"
              >
                {loaded.includes(index) && (
                  <button
                    className={clsx(
                      "absolute left-0 pr-1 top-1/2 transform -translate-x-[8px] -translate-y-1/2 text-gray-200 hover:text-yellow-400 hover:scale-110 transition-transform-opacity duration-300 group-hover:translate-x-[-16px] ",    
                      {
                        "group-hover:opacity-100 opacity-0": !clickedLikes.includes(index),
                        "absolute left-0 pr-1 top-1/2 transform translate-x-[-16px] opacity-100 text-yellow-400": clickedLikes.includes(index),
                      }
                    )}
                    onClick={() => handleClickLike(index)}
                  >
                    <svg width="13" height="13" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M7.22303 0.665992C7.32551 0.419604 7.67454 0.419604 7.77702 0.665992L9.41343 4.60039C9.45663 4.70426 9.55432 4.77523 9.66645 4.78422L13.914 5.12475C14.18 5.14607 14.2878 5.47802 14.0852 5.65162L10.849 8.42374C10.7636 8.49692 10.7263 8.61176 10.7524 8.72118L11.7411 12.866C11.803 13.1256 11.5206 13.3308 11.2929 13.1917L7.6564 10.9705C7.5604 10.9119 7.43965 10.9119 7.34365 10.9705L3.70718 13.1917C3.47945 13.3308 3.19708 13.1256 3.25899 12.866L4.24769 8.72118C4.2738 8.61176 4.23648 8.49692 4.15105 8.42374L0.914889 5.65162C0.712228 5.47802 0.820086 5.14607 1.08608 5.12475L5.3336 4.78422C5.44573 4.77523 5.54342 4.70426 5.58662 4.60039L7.22303 0.665992Z" 
                    fill="currentColor"></path></svg>
                  </button>
                )}
                <div className="embed-container w-full h-20 ">
                  
                  <div className={`embed ${loaded.includes(index) ? "active" : ""}`}>
                    <iframe
                      onLoad={() => handleLoad(index)}
                      src={`https://open.spotify.com/embed/track/${id}?utm_source=generator`}
                      style={{border: "none"}}
                      width="100%"
                      height="132"
                      allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
                      loading="eager"
                    ></iframe>
                  </div>
                </div>
              </li>
            ))}
          </ul>
          <div className="flex justify-between mt-4 px-1 py-1 ">
            {visibleEmbeds < recommendationsArray.length && (
              <button
                className="z-50 px-4 py-2 bg-custom-brown text-gray-200 shadow-xl font-bold rounded-full hover:bg-yellow-700 duration-300 hover:scale-105 transition-transform"
                onClick={handleLoadMore}
              >
                <img src="/plus.png" alt="Arrow" width={20} height={20}/>
              </button>
            )}
              <button
              className="z-50 px-4 py-2 bg-custom-brown text-gray-200 shadow-xl font-bold rounded-full hover:bg-yellow-700 duration-300 hover:scale-105 transition-transform"
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
