import React, {
  useState,
  useEffect,
  useRef,
  useCallback,
  useMemo,
} from "react";
import axios from "axios";
import { Meteors } from "./ui/meteors.tsx"; // Adjust the path as necessary based on your project structure
import RecommendationDesc from "./RecommendationDesc.js";
import { motion } from "framer-motion";
import LoadingBars from "./LoadingBars.js";
import IFrames from "./IFrames.js";
import LoadMoreButton from "./LoadMoreButton.js";
import ShuffleButton from "./ShuffleButton.js";
import PlaylistToggle from "./PlaylistToggle.js";

function RecommendationsList({
  recommendations,
  onRecommendations,
  setIsLoading,
  setIsLocalLoading,
  query,
  onQueryChange,
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
  const [showMeteors, setShowMeteors] = useState(false);
  const [animate, setAnimate] = useState(false);
  const [showPlaylistRecs, setShowPlaylistRecs] = useState(false);
  // const [recommendationsArray, setRecommendationsArray] = useState([]);

  const scrollContainerRef = useRef(null);

  const recommendationsArray = useMemo(() => {
    if (showPlaylistRecs) {
      return recommendations.playlist_rec_ids || [];
    } else {
      return recommendations.recommended_ids || [];
    }
  }, [showPlaylistRecs, recommendations]);

  // Handler for shuffling recommendations

  // Handler for clicking track
  const handleTrackRecommend = useCallback(
    async (index) => {
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
            `${process.env.REACT_APP_BACKEND_URL}/t4/recommend?link=${trackID}`,
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
    },
    [
      setAnimateOut,
      setIsLoading,
      onQueryChange,
      onRecommendations,
      setIsLocalLoading,
      setLastActionShuffle,
      userPlaylistIds,
      recommendationsArray,
    ]
  );

  // Set the initial number of visible embeds
  useEffect(() => {
    if (recommendations) {
      setAnimate(true);
      const initialVisibleEmbeds = showPlaylistRecs ? 3 : 5;
      setVisibleEmbeds(initialVisibleEmbeds);
    }
  }, [recommendations, lastActionShuffle, showPlaylistRecs]);

  // Get the array of recommended ids

  // console.log(recommendationsArray);

  // Load meteors when recommendations are received

  // Define loading based on whether search was initiated and recommendations are not yet received
  if (!recommendations || recommendations.length === 0) {
    return null; // If no recommendations or empty array, return null
  }

  return (
    <div
      className={`relative ${demo ? "w-[35vw]  z-0" : "h-[75vh] mt-10 overflow-hidden "}`}
    >
      <div className="flex justify-center h-full">
        {!demo && (
          <RecommendationDesc
            recommendations={recommendations}
            animate={animate}
            animateOut={animateOut}
            isShuffling={isShuffling}
            lastActionShuffle={lastActionShuffle}
            demo={demo}
          />
        )}
        <div
          className={`${demo ? "w-[35vw] " : "lg:ml-4 sm:ml-4  w-3/4 flex flex-col h-full "} `}
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
              recommendations-container pt-5 ${showPlaylistRecs ? "lg:px-10 sm:pl-8 sm:pr-4" : "px-5"} pb-5 bg-gradient-to-tr from-gray-900 via-gray-800 to-blue-900 shadow-2xl rounded-2xl relative  container-transition opacity-0 
              ${animate ? "recs-fade-up opacity-0" : ""} 
                  ${animateOut ? "recs-fade-out opacity-100" : ""}
              `}
                // style={{ "--container-height": `${containerHeight}px` }}
                // onScroll={(e) => setScrollPosition(e.target.scrollTop)}
              >
                {/* {showMeteors && !demo && (
                  <Meteors
                    number={25}
                    className="absolute inset-0 -translate-y-[4px]"
                    style={{ zIndex: -1 }}
                  />
                )} */}
                <IFrames
                  recommendationsArray={recommendationsArray}
                  visibleEmbeds={visibleEmbeds}
                  showPlaylistRecs={showPlaylistRecs}
                  handleTrackRecommend={handleTrackRecommend}
                  scrollContainerRef={scrollContainerRef}
                  setShowMeteors={setShowMeteors}
                  lastActionShuffle={lastActionShuffle}
                  animateOut={animateOut}
                  demo={demo}
                />
              </motion.div>
              <div className="flex justify-between py-4 px-1 relative z-10 ">
                {visibleEmbeds < recommendationsArray.length && (
                  <LoadMoreButton
                    visibleEmbeds={visibleEmbeds}
                    animate={animate}
                    animateOut={animateOut}
                    setVisibleEmbeds={setVisibleEmbeds}
                    showPlaylistRecs={showPlaylistRecs}
                    scrollContainerRef={scrollContainerRef}
                  />
                )}
                {!demo && (
                  <ShuffleButton
                    animate={animate}
                    animateOut={animateOut}
                    setAnimateOut={setAnimateOut}
                    setIsLoading={setIsLoading}
                    onRecommendations={onRecommendations}
                    setIsLocalLoading={setIsLocalLoading}
                    setIsShuffling={setIsShuffling}
                    setLastActionShuffle={setLastActionShuffle}
                    userPlaylistIds={userPlaylistIds}
                    query={query}
                  />
                )}
              </div>
            </>
          )}
        </div>
        {!demo && (
          <PlaylistToggle
            setAnimateOut={setAnimateOut}
            setLastActionShuffle={setLastActionShuffle}
            setIsLocalLoading={setIsLocalLoading}
            setIsLoading={setIsLoading}
            setIsShuffling={setIsShuffling}
            animate={animate}
            animateOut={animateOut}
            setShowPlaylistRecs={setShowPlaylistRecs}
            showPlaylistRecs={showPlaylistRecs}
          />
        )}
      </div>
    </div>
  );
}

export default React.memo(RecommendationsList);
