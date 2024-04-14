import React, { useState } from "react";
import axios from "axios";

function SearchBar({ onRecommendations, setIsLoading}) {
  const [query, setQuery] = useState("");
  //const [responseMessage, setResponseMessage] = useState({ recommendations: [] });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const response = await axios.get(`/RecEngine/recommend?link=${query}`);
      // Assuming the backend response structure is { message: "Your input was: query" }
      console.log(response.data); // Log the entire response object
      //setResponseMessage(response.data); // Access the message property
      onRecommendations(response.data || []); // Access the recommendations property or default to an empty array
    } catch (error) {
      console.error("Error fetching search results", error);
      //setResponseMessage({ recommendations: [] });
      onRecommendations([]);
    }
    setIsLoading(false);
  };

  return (
    <div className="SearchBar w-full flex justify-center items-center px-4 ">
      <form onSubmit={handleSubmit} className="relative w-full max-w-md hover:scale-105 transition-transform duration-300">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Recommend"
          className="px-3 py-2 pr-10 border-2 rounded-full border-gray-500 border-opacity-50 w-full focus:outline-none bg-custom_dark text-white placeholder-gray-400"
        />
        <button
          type="submit"
          className="absolute right-1 top-1/2 transform -translate-y-1/2 bg-gradient-to-r from-green-600 to-green-800 text-black p-1 rounded-full inline-flex items-center justify-center w-8 h-8 transition duration-300 ease-in-out hover:from-green-900 hover:to-green-900"
          aria-label="Search"
        >
          <svg
            width="17"
            height="17"
            viewBox="0 0 14 14"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              fill="white"
              d="M3.24182 2.32181C3.3919 2.23132 3.5784 2.22601 3.73338 2.30781L12.7334 7.05781C12.8974 7.14436 13 7.31457 13 7.5C13 7.68543 12.8974 7.85564 12.7334 7.94219L3.73338 12.6922C3.5784 12.774 3.3919 12.7687 3.24182 12.6782C3.09175 12.5877 3 12.4252 3 12.25V2.75C3 2.57476 3.09175 2.4123 3.24182 2.32181ZM4 3.57925V11.4207L11.4288 7.5L4 3.57925Z"
            />
          </svg>
        </button>
      </form>
    </div>
  );
}

export default SearchBar;