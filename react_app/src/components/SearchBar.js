import React, { useState } from "react";
import axios from "axios";
import { useMotionTemplate, useMotionValue, motion } from "framer-motion";


function SearchBar({ onRecommendations, setIsLoading, onQueryChange}) {
  const [query, setQuery] = useState("");
  //const [responseMessage, setResponseMessage] = useState({ recommendations: [] });
  const [isLoading, setIsLocalLoading] = useState(false);

  const radius = 100;
  const [visible, setVisible] = React.useState(false);
  let mouseX = useMotionValue(0);
  let mouseY = useMotionValue(0);

  function handleMouseMove({ currentTarget, clientX, clientY }) {
    let { left, top } = currentTarget.getBoundingClientRect();
    mouseX.set(clientX - left);
    mouseY.set(clientY - top);
  }


  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setIsLocalLoading(true);
    onQueryChange(query);
    try {
      const response = await axios.get(`/RecEngine/recommend?link=${query}`);
      // Assuming the backend response structure is { message: "Your input was: query" }
      //setResponseMessage(response.data); // Access the message property
      onRecommendations(response.data || []); // Access the recommendations property or default to an empty array
    } catch (error) {
      console.error("Error fetching search results", error);
      //setResponseMessage({ recommendations: [] });
      onRecommendations([]);
    }
    setIsLoading(false);
    setIsLocalLoading(false);
  };

  return (
    <div className="SearchBar w-full flex justify-center items-center px-4">
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
        className="relative w-full max-w-md hover:scale-105 transition-transform duration-300 p-[2px] rounded-full"
      >
        <form onSubmit={handleSubmit} className="relative w-full">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Recommend"
            className="px-3 py-2 pr-10 border-none rounded-full w-full focus:outline-none bg-gray-700 text-gray-200 placeholder-gray-400"
          />
          <button
            type="submit"
            className="absolute right-1 top-1/2 transform -translate-y-1/2 text-black p-1 rounded-full inline-flex items-center justify-center w-8 h-8 transition duration-300 ease-in-out bg-custom-brown hover:bg-yellow-700"
            aria-label="Search"
          >
          {isLoading ? (
            <img src="/icons8-pause-button-30.png" alt="Pause" width="17" height="17"  />
          ) : (
            <img src="/icons8-play-button-30.png" alt="Play" width="15" height="15" />
          )}
          </button>
        </form>
      </motion.div>
    </div>
  );
}



export default SearchBar;