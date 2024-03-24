import React from 'react';

function RecommendationsList({ recommendations }) {
  return (
    <div className="recommendations-list">
      <h2>Recommendations</h2>
      {recommendations.length > 0 ? (
        <ul>
          {recommendations.map((rec, index) => (
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
      ) : (
        <p>No recommendations to display.</p>
      )}
    </div>
  );
}

export default RecommendationsList;