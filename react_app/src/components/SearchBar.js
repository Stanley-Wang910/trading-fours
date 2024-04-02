import React, { useState } from 'react';
import axios from 'axios';


function SearchBar({ onRecommendations }) {
    const [query, setQuery] = useState('');
    //const [responseMessage, setResponseMessage] = useState({ recommendations: [] });

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.get(`/RecEngine/recommend?link=${query}`);
            // Assuming the backend response structure is { message: "Your input was: query" }
            console.log(response.data); // Log the entire response object
            //setResponseMessage(response.data); // Access the message property
            onRecommendations(response.data || []); // Access the recommendations property or default to an empty array
        } catch (error) {
            console.error('Error fetching search results', error);
            //setResponseMessage({ recommendations: [] });
            onRecommendations([]);
        }
    };

    return (
        <div className="SearchBar">
            <form onSubmit={handleSubmit}>
                <input
                    type="text"
                    value={query}
                    onChange={e => setQuery(e.target.value)}
                    placeholder="Search..."
                />
                <button type="submit">Search</button>
            </form>
            {/*<RecommendationsList recommendations={responseMessage.recommendations || []} /> */}
        </div>
    );
}

export default SearchBar;