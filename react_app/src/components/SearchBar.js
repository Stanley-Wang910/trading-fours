import React, { useEffect, useState, useCallback } from "react";
import axios from "axios";
import { useMotionTemplate, useMotionValue, motion } from "framer-motion";
import Select from "react-select";


function SearchBar({ onRecommendations, setIsLoading, onQueryChange}) {
  const [query, setQuery] = useState("");
  const [isLoading, setIsLocalLoading] = useState(false);
  const [playlists, setPlaylists] = useState([]);
  const [selectedOption, setSelectedOption] = useState(null);



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
  const handleSearch = useCallback(async () => {
    const searchQuery = selectedOption ? selectedOption.value : query;
    console.log("Query value before search:", query);
    setIsLoading(true);
    setIsLocalLoading(true);
    onQueryChange(query);
    if (query) {
      console.log("Querying", query);
    }
    if (searchQuery.trim() !== "") {
      console.log("Querying", searchQuery);
      try {
        const response = await axios.get(`/recommend?query=${searchQuery}`);
        onRecommendations(response.data || []);
        setQuery("");
        setSelectedOption (null);
      } catch (error) {
        console.error("Error fetching search results", error);
        onRecommendations([]);
      }
    } else {
      onRecommendations([]);
    }
    setIsLoading(false);
    setIsLocalLoading(false);
  }, [selectedOption, query, onQueryChange, onRecommendations, setIsLoading]);


  useEffect(() => {
    const fetchPlaylists = async () => {
      try {
        const response = await axios.get("/search");
        setPlaylists(response.data);
      } catch (error) {
        console.error("Error fetching playlists", error);
      }
    };

    fetchPlaylists();
  }, []);


   // Map the playlists data to the format expected by react-select
   const options = playlists.map((playlist) => ({
    value: playlist[1],
    label: playlist[0],
  }));


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
        className="relative w-full max-w-md p-[2px] rounded-full"
      >
        <div className="relative w-full">
          <Select
            value={selectedOption}
            onChange={(selectedOption) => {
              setSelectedOption(selectedOption);
              if (selectedOption) {
                setQuery(selectedOption.value);
              } 
            }}
            onInputChange={(inputValue) => {
              setQuery(inputValue);
              console.log("Query value:", query);
            }}
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                event.preventDefault();
                handleSearch();
              }
            }}
   
            options={options}
            isClearable
            placeholder="Recommend"
            classNamePrefix="react-select"
            className="px-3 py-2 pr-10 border-none rounded-full w-full focus:outline-none bg-gray-700 text-gray-200 placeholder-gray-400"
            styles={{
              control: (provided) => ({
                ...provided,
                backgroundColor: "transparent",
                borderRadius: "9999px",
                borderColor: "transparent",
                boxShadow: "none",
                "&:hover": {
                  borderColor: "transparent",
                },
              }),
              input: (provided) => ({
                ...provided,
                color: "inherit",
              }),
              placeholder: (provided) => ({
                ...provided,
                color: "inherit",
              }),
              singleValue: (provided) => ({
                ...provided,
                color: "inherit",
              }),
              option: (provided, state) => ({
                ...provided,
                backgroundColor: state.isSelected ? "rgb(59, 130, 246)" : "transparent",
                color: state.isSelected ? "white" : "inherit",
                "&:hover": {
                  backgroundColor: "rgb(96, 165, 250)",
                  color: "white",
                },
              }),
            }}
          />
         <button
            
            onClick={handleSearch}
            // whileHover={{ scale: 1}}
            // whileTap={{ scale: 0.9 }}
            // animate={{ scale: isLoading ? 0.9 : 1 }}
            // transition={{ type: "spring", stiffness: 300, damping: 20 }}
            className="absolute right-1 top-1 transform -translate-y-1/2 text-black p-1 rounded-full inline-flex items-center justify-center w-8 h-8 bg-custom-brown hover:bg-yellow-700"
            // aria-label="Search"
          >
            {isLoading ? (
              <img src="/icons8-pause-button-30.png" alt="Pause" width="17" height="17" />
            ) : (
              <img src="/icons8-play-button-30.png" alt="Play" width="15" height="15" />
            )}
          </button>

          
        </div>
      </motion.div>
    </div>
  );
}



export default SearchBar;