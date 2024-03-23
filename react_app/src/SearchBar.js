import React, { useState } from 'react';
import axios from 'axios';

function SearchBar({ onSearch}) {
  const [searchInput, setSearchInput] = useState('');

  const handleInputChange = (event) => {
    setSearchInput(event.target.value);
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    axios.post('/api/search', { query: searchInput })
      .then(response => {
        console.log(response.data);
        if (onSearch) {
          onSearch(response.data);
        }
      })
      .catch(error => {
        console.error('Error:', error);
        // handle the error
      });
  };

  return (
    <div style={{ display: 'flex', justifyContent: 'center', marginTop: '50px' }}>
      <form onSubmit={handleSubmit}>
        <input type="text" value={searchInput} onChange={handleInputChange} />
        <input type="submit" value="Search" />
      </form>
    </div>
  );
}

export default SearchBar;