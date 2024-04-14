import React, { useState, useEffect } from "react";

function RecommendationsList({ recommendations }) {
  const [visibleEmbeds, setVisibleEmbeds] = useState(5); // State to track the number of visible embeds
  const [loaded, setLoaded] = useState({}); // State to track load status of each iframe
  const isPlaylist = recommendations && recommendations.hasOwnProperty("playlist"); // Check if recommendations is a playlist
  useEffect(() => {
    if (recommendations) {
      const initialVisibleEmbeds = isPlaylist ? 5 : 5; // Set initial number of visible embeds based on whether it's a playlist or not
      setVisibleEmbeds(initialVisibleEmbeds);
    }
  }, [recommendations]);

  // Define loading based on whether search was initiated and recommendations are not yet received
  if (!recommendations || recommendations.length === 0) {
    return null; // If no recommendations or empty array, return null
  }

  const recommendationsArray = recommendations.recommended_ids || []; // Get the array of recommended ids
  console.log(recommendationsArray);

  const handleLoad = (id) => {
    setLoaded((prev) => ({ ...prev, [id]: true })); // Update the loaded state for the specific iframe
  };

  return (
    <div className="max-w-2xl mx-auto p-4">
      {isPlaylist && recommendations.top_genres && recommendations.playlist ? (
        <h2 className="text-xl font-semibold text-gray-300 mb-4">
          <span className="text-gray-400 font-bold ">{recommendations.top_genres.join(", ")}</span> recommendations for{" "}
          <span className="text-gray-300 font-bold italic">{recommendations.playlist}</span>
        </h2>
      ) : (
        <h2 className="text-xl font-semibold text-gray-300 mb-4">
          Here are some recommendations for <span className="text-gray-300 font-bold italic">{recommendations.track}</span> by{" "}
          <span className="text-gray-300 font-bold italic">{recommendations.artist}</span>, released in {""}
          <span className="text-gray-400 font-semibold">{recommendations.release_date}</span>
        </h2>
      )}
      <div className="recommendations-container p-4 bg-gradient-to-r from-gray-800 to-gray-600 shadow-2xl rounded-2xl transform ">
        <ul className="space-y-4">
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
        {visibleEmbeds < recommendationsArray.length && (
          <button
            className="mt-4 px-4 py-2 bg-blue-700 text-gray-200 font-bold rounded-full hover:bg-blue-600 duration-300 mx-auto block hover:scale-105 transition-transform"
            onClick={() => setVisibleEmbeds((prev) => prev + 5)}
          >
            +
          </button>
        )}
      </div>
    </div>
  );
}

export default RecommendationsList;
