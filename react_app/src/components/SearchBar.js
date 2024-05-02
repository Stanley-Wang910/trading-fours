import React, { useState, useCallback } from "react";
import axios from "axios";
import { useMotionTemplate, useMotionValue, motion } from "framer-motion";
import PlaylistDropdown from "./PlaylistDropdown";

function SearchBar({ onRecommendations, setIsLoading, onQueryChange}) {
  const [query, setQuery] = useState("");
  const [isLocalLoading, setIsLocalLoading] = useState(false);

  const radius = 100;
  const [visible, setVisible] = React.useState(false);
  let mouseX = useMotionValue(0);
  let mouseY = useMotionValue(0);

  // Memoized callback for handling mouse move
  const handleMouseMove = useCallback(({ currentTarget, clientX, clientY }) => {
    const { left, top } = currentTarget.getBoundingClientRect();
    mouseX.set(clientX - left);
    mouseY.set(clientY - top);
  }, [mouseX, mouseY]);

  // Memoized callback for handling form submission
  const handleSubmit = useCallback(async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setIsLocalLoading(true);
    onQueryChange(query);

    try {
      const response = await axios.get(`/recommend?link=${query}`);
      onRecommendations(response.data || []);
      setQuery("");
    } catch (error) {
      console.error("Error fetching search results", error);
      onRecommendations([]);
      setQuery("");
    }

    setIsLoading(false);
    setIsLocalLoading(false);
  }, [query, onQueryChange, onRecommendations, setIsLoading]);

  

  return (
    <div className="flex items-center mx-4">
    <div className="SearchBar w-full flex justify-center items-center">
      <motion.div
        style={{
          background: useMotionTemplate`
            radial-gradient(
              ${visible ? radius + "px" : "0px"} circle at ${mouseX}px ${mouseY}px,
              #cc8e15,
              transparent 80%
            )
          `,
          
        }}
        onMouseMove={handleMouseMove}
        onMouseEnter={() => setVisible(true)}
        onMouseLeave={() => setVisible(false)}
        className="relative w-full max-w-md p-[2px] rounded-full"
      >
        <form onSubmit={handleSubmit} className="relative w-full">
              
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Recommend"
            className="px-3 py-2 pr-10 border-none rounded-full w-full focus:outline-none bg-gray-700 text-gray-200 placeholder-gray-400"
          />
         <motion.button
            type="submit"
            
            whileTap={{ scale: 0.95, onDurationChange: 0}}
            animate={{ scale: isLocalLoading ? 0.9 : 1 }}
            transition={{ type: "spring", stiffness: 300, damping: 20 }}
            className="absolute right-1 top-1 transform -translate-y-1/2 text-black p-1 rounded-full inline-flex items-center justify-center w-8 h-8 bg-custom-brown hover:bg-yellow-700"
            aria-label="Search"
          >
            {isLocalLoading ? (
              <img src="/icons8-pause-button-30.png" alt="Pause" width="17" height="17" />
            ) : (
              <img src="/icons8-play-button-30.png" alt="Play" width="15" height="15" />
            )}
          </motion.button>
        </form>
      </motion.div>
    </div>
      <div className="">
        <PlaylistDropdown onRecommendations={onRecommendations} setIsLoading={setIsLoading} onQueryChange={onQueryChange} setIsLocalLoading={setIsLocalLoading}/>
      </div>
    </div>
  );
}



export default SearchBar;