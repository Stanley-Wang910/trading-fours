import React, { useState, useCallback } from "react";
import { motion } from "framer-motion";
import axios from "axios";

function ShuffleButton({
  animate,
  animateOut,
  setAnimateOut,
  setIsLoading,
  onRecommendations,
  setIsLocalLoading,
  setIsShuffling,
  setLastActionShuffle,
  userPlaylistIds,
  query,
}) {
  const handleShuffle = useCallback(async () => {
    setAnimateOut(true);
    setLastActionShuffle(true);
    setTimeout(async () => {
      setIsLoading(true);
      setIsLocalLoading(true);
      setIsShuffling(true);

      try {
        const response = await axios.post(
          `${process.env.REACT_APP_BACKEND_URL}/t4/recommend?link=${query}`,
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
  }, [
    query,
    setAnimateOut,
    setIsLoading,
    onRecommendations,
    setIsShuffling,
    setIsLocalLoading,
    userPlaylistIds,
    setLastActionShuffle,
  ]);

  return (
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
  );
}

export default React.memo(ShuffleButton);
