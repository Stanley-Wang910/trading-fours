import React from 'react';

function RecommendationsList({ recommendations }) {
  if (!recommendations || recommendations.length === 0) {
    return <p>No recommendations to display.</p>;
  }

  const isPlaylist = recommendations.hasOwnProperty('playlist');
  console.log(isPlaylist)
  const recommendationsArray= recommendations.recommendations || [];
  console.log(recommendationsArray)
  return (
    <div className="recommendations-list">
      {isPlaylist && recommendations.top_genres && recommendations.playlist ? (
        <h2>
          {recommendations.top_genres.join(', ')} recommendations for {recommendations.playlist}
        </h2>
      ) : (
        <h2>
          Here are some recommendations for {recommendations.track} by {recommendations.artist}, released in {''}
          {recommendations.release_date}
        </h2>
      )}
      <ul>
        {recommendationsArray.map((rec, index) => (
          <li key={index}>
            <div>
              <strong>Song:</strong> {rec.Song}
            </div>
            <div>
              <strong>Artist:</strong> {rec.Artist}
            </div>
            <div>
              <strong>Genre:</strong> {rec.Genre}
            </div>
            <div>
              <strong>Similarity:</strong> {rec.Similarity}
            </div>
            <div>
              <a href={rec.Link} target="_blank" rel="noopener noreferrer">Listen on Spotify</a>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default RecommendationsList;