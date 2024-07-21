import React, { useState, useEffect, useRef, useCallback } from "react";
import axios from "axios";
import { Meteors } from "./ui/meteors.tsx"; // Adjust the path as necessary based on your project structure
import clsx from "clsx";
import RecommendationDesc from "./RecommendationDesc.js";
import { motion } from "framer-motion";
import LoadingBars from "./LoadingBars.js";

function RecommendationsList({
  recommendations,
  onRecommendations,
  setIsLoading,
  setIsLocalLoading,
  query,
  onQueryChange,
  position,
  onTogglePosition,
  setFavoritedTracks,
  animateOut,
  setAnimateOut,
  isShuffling,
  setIsShuffling,
  lastActionShuffle,
  setLastActionShuffle,
  userPlaylistIds,
  demo = false,
}) {
  //State variables
  const [visibleEmbeds, setVisibleEmbeds] = useState(5); // State to track the number of visible embeds
  const [loaded, setLoaded] = useState([]);
  const [showMeteors, setShowMeteors] = useState(false);
  const [containerHeight, setContainerHeight] = useState(575); // Set the starting height
  const [visibleButtons, setVisibleButtons] = useState({});
  const [animate, setAnimate] = useState(false);
  const [showPlaylistRecs, setShowPlaylistRecs] = useState(false);
  // const [recommendationsArray, setRecommendationsArray] = useState([]);

  const scrollContainerRef = useRef(null);
  const [scrollPosition, setScrollPosition] = useState(0);

  const [hoveredButton, setHoveredButton] = useState(null);
  const [hoveredIFrame, setHoveredIFrame] = useState(null);

  // Constants
  // const maxHeight = 3000; // Set the maximum height for recommendations container
  // const extendRec = 500;
  // Memoized callbakc to handle loading more embeds
  const handleLoadMore = useCallback(() => {
    const incrementCounter = showPlaylistRecs ? 3 : 5;
    const scrollMultiplier = showPlaylistRecs ? 372 : 132;
    const newVisibleEmbeds = visibleEmbeds + incrementCounter;
    setVisibleEmbeds(newVisibleEmbeds);
    // setContainerHeight((prev) => Math.min(prev + extendRec, maxHeight));

    setTimeout(() => {
      const scrollContainer = scrollContainerRef.current;
      if (scrollContainer) {
        const newScrollPosition =
          (newVisibleEmbeds - incrementCounter) * scrollMultiplier;
        scrollContainer.scrollTo({
          top: newScrollPosition,
          behavior: "smooth",
        });
        setScrollPosition(newScrollPosition);
      }
    }, 500);
  }, [visibleEmbeds, showPlaylistRecs]);

  // Handler for loading embeds

  const handleLoad = useCallback((index) => {
    // Mark the embed as active
    const embedElements =
      scrollContainerRef.current?.querySelectorAll(".embed");
    if (embedElements?.[index]) {
      embedElements[index].classList.add("active");
    }

    // Update the loaded state
    setLoaded((prev) => {
      if (!prev.includes(index)) {
        return [...prev, index];
      }
      return prev;
    });
  }, []);

  // Handler for shuffling recommendations
  const handleShuffle = useCallback(async () => {
    setAnimateOut(true);
    setLastActionShuffle(true);
    setTimeout(async () => {
      setIsLoading(true);
      setIsLocalLoading(true);
      setIsShuffling(true);

      try {
        const response = await axios.post(
          `${process.env.REACT_APP_BACKEND_URL}/recommend?link=${query}`,
          { userPlaylistIds },
          { withCredentials: true }
        );
        onRecommendations(response.data || []);
      } catch (error) {
        console.error("Error fetching search results", error);
        onRecommendations([]);
      } finally {
        setIsLoading(false);
        setIsLocalLoading(false);
        setAnimateOut(false);
        setIsShuffling(false);
      }
    }, 500);
  }, [query, setAnimateOut, setIsLoading, onRecommendations, setIsShuffling]);

  // Handler for clicking like
  const handleTrackRecommend = async (index) => {
    setLastActionShuffle(false);
    const trackID = recommendationsArray[index];
    console.log("Clicked like", index, trackID);

    setAnimateOut(true);
    setTimeout(async () => {
      setIsLocalLoading(true);
      setIsLoading(true);
      onQueryChange(trackID);

      try {
        const response = await axios.post(
          `${process.env.REACT_APP_BACKEND_URL}/recommend?link=${trackID}`,
          { userPlaylistIds },
          { withCredentials: true }
        );
        onRecommendations(response.data || []);
      } catch (error) {
        console.error("Error fetching search results", error);
        onRecommendations([]);
      }
      setIsLocalLoading(false);
      setIsLoading(false);
      setAnimateOut(false);
    }, 500);
  };

  useEffect(() => {
    loaded.forEach((index) => {
      if (!visibleButtons[index]) {
        const timer = setTimeout(() => {
          setVisibleButtons((prev) => ({ ...prev, [index]: true }));
        }, 1750); // Animation time for embed-container

        return () => clearTimeout(timer);
      }
    });
  }, [loaded, visibleButtons]);

  // Check if recommendations is a playlist
  const isPlaylist =
    recommendations && recommendations.hasOwnProperty("p_features"); // Check if recommendations is a playlist
  // Set the initial number of visible embeds
  useEffect(() => {
    if (recommendations) {
      setAnimate(true);
      const initialVisibleEmbeds = showPlaylistRecs ? 3 : 5;
      setVisibleEmbeds(initialVisibleEmbeds);
    }
  }, [recommendations, lastActionShuffle, showPlaylistRecs]);

  useEffect(() => {
    // Effect to prevent premature rendering out and in of iframes on shufle
    if (lastActionShuffle && animateOut) {
      setTimeout(() => {
        setLoaded([]);
      }, 500); // Timeout to wait until rec container aniamtes out
    }
  });

  // Get the array of recommended ids
  const recommendationsArray = showPlaylistRecs
    ? recommendations.playlist_rec_ids || []
    : recommendations.recommended_ids || []; // Get the array of recommended ids
  // console.log(recommendationsArray);

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

  const handleShowPlaylistsToggle = () => {
    setAnimateOut(true);
    setLastActionShuffle(true);
    setTimeout(() => {
      setIsLocalLoading(true);
      setIsLoading(true);
      setIsShuffling(true);

      setShowPlaylistRecs(!showPlaylistRecs);

      setTimeout(() => {
        setIsLoading(false);
        setIsLocalLoading(false);
        setAnimateOut(false);
        setIsShuffling(false);
      }, 1500);
    }, 500);
  };

  return (
    <div
      className={`relative ${demo ? "w-[35vw] z-0" : "h-[75vh] mt-10 overflow-hidden "}`}
    >
      <div className="flex justify-center h-full">
        <RecommendationDesc
          recommendations={recommendations}
          animate={animate}
          animateOut={animateOut}
          isShuffling={isShuffling}
          lastActionShuffle={lastActionShuffle}
          demo={demo}
        />
        <div
          className={`${demo ? "w-[35vw] " : "lg:ml-[0vh]  w-3/4 flex flex-col h-full "} `}
        >
          {isShuffling ? (
            <div className="">
              <LoadingBars className="absolute translate-x-[27vw] translate-y-[10vh]  " />
            </div>
          ) : (
            <>
              <motion.div
                ref={scrollContainerRef}
                className={` 
              ${demo ? "overflow-hidden" : "overflow-y-auto flex-grow"} 
              recommendations-container pt-5 ${showPlaylistRecs ? "px-10" : "px-5"} pb-5 bg-gradient-to-tr from-gray-900 via-gray-800 to-blue-900 shadow-2xl rounded-2xl relative  container-transition opacity-0 
              ${animate ? "recs-fade-up opacity-0" : ""} 
                  ${animateOut ? "recs-fade-out opacity-100" : ""}
              `}
                // style={{ "--container-height": `${containerHeight}px` }}
                onScroll={(e) => setScrollPosition(e.target.scrollTop)}
              >
                {showMeteors && !demo && (
                  <Meteors
                    number={25}
                    className="absolute inset-0 -translate-y-[4px]"
                    style={{ zIndex: -1 }}
                  />
                )}
                <ul className="meteor space-y-5 z-10 relative">
                  {recommendationsArray
                    .slice(0, visibleEmbeds)
                    .map((id, index) => (
                      <motion.li
                        key={index}
                        className="w-full bg-transparent overflow-visible relative flex group"
                        onHoverStart={() => setHoveredIFrame(index)}
                        onHoverEnd={() => setHoveredIFrame(null)}
                      >
                        {loaded.includes(index) && visibleButtons[index] && (
                          <motion.button
                            className="absolute left-0 pr-1 top-1/2"
                            onClick={() =>
                              demo ? null : handleTrackRecommend(index)
                            }
                            onMouseEnter={() => setHoveredButton(index)}
                            onMouseLeave={() => setHoveredButton(null)}
                            whileTap={{ scale: 1.05 }}
                            initial={{ opacity: 0, x: "0%", y: "-50%" }}
                            animate={{
                              opacity: hoveredIFrame === index ? 1 : 0,
                              x: hoveredIFrame === index ? "-75%" : "0%",
                              y: hoveredIFrame === index ? "-50%" : "-50%",
                              scale: hoveredButton === index ? 1.1 : 1.0,
                            }}
                            transition={{ duration: 0.2 }}
                          >
                            <svg
                              width="24"
                              height="24"
                              viewBox="0 0 24 24"
                              fill="none"
                              xmlns="http://www.w3.org/2000/svg"
                            >
                              <motion.path
                                fill-rule="evenodd"
                                clip-rule="evenodd"
                                d="M10.1205 19.0028C8.94206 18.9775 8 18.015 8 16.8363C8 15.6576 8.94206 14.6951 10.1205 14.6698C11.2988 14.6951 12.2409 15.6576 12.2409 16.8363C12.2409 18.015 11.2988 18.9775 10.1205 19.0028V19.0028Z"
                                animate={{
                                  stroke:
                                    hoveredButton === index
                                      ? "#fbbf24"
                                      : "#cbd5e1",
                                }}
                                transition={{ duration: 0.3 }}
                                stroke-width="1.5"
                                stroke-linecap="round"
                                stroke-linejoin="round"
                              />
                              <motion.path
                                d="M11.5024 16.8358C11.5024 17.25 11.8382 17.5858 12.2524 17.5858C12.6666 17.5858 13.0024 17.25 13.0024 16.8358H11.5024ZM13.0024 8.50279C13.0024 8.08857 12.6666 7.75279 12.2524 7.75279C11.8382 7.75279 11.5024 8.08857 11.5024 8.50279H13.0024ZM12.2524 8.50279H11.5024C11.5024 8.71537 11.5926 8.91798 11.7506 9.06021C11.9086 9.20244 12.1196 9.27093 12.331 9.24866L12.2524 8.50279ZM12.2524 7.00279H13.0024C13.0024 6.98925 13.0021 6.97573 13.0013 6.96221L12.2524 7.00279ZM12.8061 5.5565L13.3365 6.08683L12.8061 5.5565ZM14.2524 5.00279L14.2118 5.75169C14.2254 5.75242 14.2389 5.75279 14.2524 5.75279V5.00279ZM15.4084 5.00279V5.75279L15.4119 5.75278L15.4084 5.00279ZM16.9927 6.49867L16.2437 6.53814V6.53814L16.9927 6.49867ZM15.5744 8.15279L15.4991 7.40657L15.4958 7.40691L15.5744 8.15279ZM13.0024 16.8358V8.50279H11.5024V16.8358H13.0024ZM13.0024 8.50279V7.00279H11.5024V8.50279H13.0024ZM13.0013 6.96221C12.9837 6.63607 13.1055 6.31779 13.3365 6.08683L12.2758 5.02617C11.7436 5.55838 11.4628 6.2918 11.5035 7.04336L13.0013 6.96221ZM13.3365 6.08683C13.5674 5.85587 13.8857 5.73402 14.2118 5.75169L14.293 4.25388C13.5414 4.21317 12.808 4.49396 12.2758 5.02617L13.3365 6.08683ZM14.2524 5.75279H15.4084V4.25279H14.2524V5.75279ZM15.4119 5.75278C15.8543 5.7507 16.2204 6.09636 16.2437 6.53814L17.7416 6.4592C17.6762 5.21805 16.6478 4.24695 15.4049 4.25279L15.4119 5.75278ZM16.2437 6.53814C16.267 6.97993 15.9393 7.36215 15.4991 7.40658L15.6497 8.89899C16.8863 8.77418 17.807 7.70036 17.7416 6.4592L16.2437 6.53814ZM15.4958 7.40691L12.1738 7.75691L12.331 9.24866L15.653 8.89866L15.4958 7.40691Z"
                                animate={{
                                  fill:
                                    hoveredButton === index
                                      ? "#fbbf24"
                                      : "#cbd5e1",
                                }}
                                transition={{ duration: 0.3 }}
                              />
                            </svg>
                          </motion.button>
                        )}
                        <div className="embed-container w-full">
                          <div
                            className={`${showPlaylistRecs ? "embed-p" : "embed"} ${loaded.includes(index) ? "active" : ""}`}
                          >
                            <iframe
                              onLoad={() => handleLoad(index)}
                              src={`https://open.spotify.com/embed/${
                                showPlaylistRecs ? `playlist` : `track`
                              }/${id}?utm_source=generator`} // [playlist]
                              style={{ border: "none" }}
                              width="100%"
                              height={showPlaylistRecs ? "352" : "83"} // 152
                              allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
                              loading="lazy"
                            ></iframe>
                          </div>
                        </div>
                      </motion.li>
                    ))}
                </ul>
              </motion.div>
              <div className="flex justify-between py-4 px-1 relative z-10 ">
                {visibleEmbeds < recommendationsArray.length && (
                  <motion.button
                    className="rounded-full"
                    whileTap={{ scale: 0.9 }}
                    onClick={handleLoadMore}
                  >
                    <div
                      className={` opacity-0 z-50 px-4 py-2 bg-custom-brown  shadow-xl font-bold rounded-full hover:bg-yellow-700 
                        ${animate ? "loadMore-fade-up opacity-0" : ""} 
                        ${animateOut ? "loadMore-fade-out opacity-100" : ""}
                        `}
                    >
                      <img src="/plus.png" alt="Arrow" width={20} height={20} />
                    </div>
                  </motion.button>
                )}
                <motion.button
                  className="rounded-full"
                  whileTap={{ scale: 0.9 }}
                  onClick={handleShuffle}
                >
                  <div
                    className={` opacity-0 z-50 px-4 py-2 bg-custom-brown  shadow-xl font-bold rounded-full hover:bg-yellow-700 
                    ${animate ? "shuffle-fade-up opacity-0" : ""} 
                    ${animateOut ? "shuffle-fade-out opacity-100" : ""}
                  `}
                  >
                    <img
                      src="/arrow.png"
                      alt="Arrow"
                      style={{ transform: "scaleX(0.9)" }}
                      width={20}
                      height={20}
                    />
                  </div>
                </motion.button>
              </div>
            </>
          )}
        </div>
        {!demo && (
          <div className="relative top-1/2 -translate-y-[5vh] right-0 ml-4 md:mr-[2vw]">
            <button
              className={`relative inline-block 
                  ${animate ? "playlistToggle-fade-in opacity-0" : ""} 
                  ${animateOut ? "playlistToggle-fade-out opacity-100" : ""}
                  `}
            >
              <svg
                onClick={handleShowPlaylistsToggle}
                fill="#ffffff"
                width="28px"
                height="28px"
                className="transition-all hover:fill-custom-brown hover:scale-110 hover:rotate-6"
                viewBox="0 0 22 22"
                xmlns="http://www.w3.org/2000/svg"
                id="memory-music-note"
              >
                <path d="M11 2H18V7H13V18H12V19H11V20H7V19H6V18H5V14H6V13H7V12H11V2M11 15H10V14H8V15H7V17H8V18H10V17H11V15Z" />
              </svg>
              <div className="absolute top-1/2 left-[100%] transform -translate-y-1/2 px-2 py-1 text-custom-brown text-xs font-semi-bold opacity-0 pointer-events-none transition-opacity duration-300 tooltip">
                Unpack Me!
              </div>
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default RecommendationsList;
