import React, { useState, useEffect } from 'react';

function RecommendationsList({ recommendations }) {
  const [visibleEmbeds, setVisibleEmbeds] = useState(5); // State to track the number of visible embeds
  const [loaded, setLoaded] = useState({});  // State to track load status of each iframe
  const isPlaylist = recommendations && recommendations.hasOwnProperty('playlist'); // Check if recommendations is a playlist
  useEffect(() => {
    if (recommendations) {
      const initialVisibleEmbeds = isPlaylist ? 10 : 5; // Set initial number of visible embeds based on whether it's a playlist or not
      setVisibleEmbeds(initialVisibleEmbeds);
    }
  }, [recommendations]);

  // Define loading based on whether search was initiated and recommendations are not yet received
  if (!recommendations || recommendations.length === 0) {
    return null; // If no recommendations or empty array, return null
  }

  const recommendationsArray= recommendations.recommended_ids || []; // Get the array of recommended ids
  console.log(recommendationsArray)

  const handleLoad = (id) => {
    setLoaded(prev => ({ ...prev, [id]: true }));  // Update the loaded state for the specific iframe
  };

  return (
    <div className="max-w-2xl mx-auto p-4">
      {isPlaylist && recommendations.top_genres && recommendations.playlist ? (
        <h2 className="text-2xl font-semibold text-gray-800 mb-4">
          {recommendations.top_genres.join(', ')} recommendations for {recommendations.playlist}
        </h2>
      ) : (
        <h2 className="text-2xl font-semibold text-gray-800 mb-4">
          Here are some recommendations for {recommendations.track} by {recommendations.artist}, released in {''}
          {recommendations.release_date}
        </h2>
      )}
      <ul className="space-y-4">
        {recommendationsArray.slice(0, visibleEmbeds).map((id, index) => (
          <li key={index} className="bg-white shadow-md rounded-lg overflow-hidden">
            <div className="w-full h-20 bg-gray-200">
              <iframe
                onLoad={() => handleLoad(id)}
                className={`w-full h-20 rounded-lg ${loaded[id] ? 'opacity-100' : 'opacity-0'} transition-opacity duration-500 delay-${index * 100}`}
                src={`https://open.spotify.com/embed/track/${id}?utm_source=generator`}
                width="100%"
                height="132"
                allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
                loading="eager"
              >
              </iframe>
            </div>
          </li>
        ))}
      </ul>
      {visibleEmbeds < recommendationsArray.length && (
        <button
          className="mt-4 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors duration-300"
          onClick={() => setVisibleEmbeds(prev => prev + 5)}
        >
          Load More
        </button>
      )}
    </div>
  );
}

export default RecommendationsList;