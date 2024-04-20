import React, { useState, useEffect } from "react";
import axios from "axios";
import clsx from "clsx";

function PlaylistDropdown({ onRecommendations, setIsLoading, onQueryChange, setIsLocalLoading}) {
  const [playlists, setPlaylists] = useState([]);
  const [selectedPlaylist, setSelectedPlaylist] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  
  
  useEffect(() => {
    const fetchPlaylists = async () => {
      try {
        const response = await axios.get("/search");
        console.log(response.data);
        setPlaylists(response.data || []);
      } catch (error) {
        console.error("Error fetching playlists", error);
      }
    };

    fetchPlaylists();
  }, []);
  const handlePlaylistSelect = async (id) => {
      setSelectedPlaylist(id);
      setIsOpen(false);
      setIsLocalLoading(true); // Set the local loading state to true
      setIsLoading(true);
      onQueryChange(id);
      try {
        const response = await axios.get(`/recommend?link=${id}`);
        onRecommendations(response.data || []);
      } catch (error) {
        console.error("Error fetching search results", error);
        onRecommendations([]);
      }
      setIsLocalLoading(false); // Set the local loading state to false
      setIsLoading(false);
    };

  return (
      <div className="relative w-full max-w-md">
        <button
        
          className={clsx("py-2  border-none rounded-full text-gray-200 placeholder-gray-400 flex items-center justify-between \
                    hover:scale-110 transition-transform-opacity duration-300 hover:translate-x-[5px] ")}
          onClick={() => setIsOpen(!isOpen)}
        >
          <svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M6.1584 3.13508C6.35985 2.94621 6.67627 2.95642 6.86514 3.15788L10.6151 7.15788C10.7954 7.3502 10.7954 7.64949 10.6151 7.84182L6.86514 11.8418C6.67627 12.0433 6.35985 12.0535 6.1584 11.8646C5.95694 11.6757 5.94673 11.3593 6.1356 11.1579L9.565 7.49985L6.1356 3.84182C5.94673 3.64036 5.95694 3.32394 6.1584 3.13508Z" fill="currentColor" fill-rule="evenodd" clip-rule="evenodd"></path></svg>
          {/* <svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M3.13523 6.15803C3.3241 5.95657 3.64052 5.94637 3.84197 6.13523L7.5 9.56464L11.158 6.13523C11.3595 5.94637 11.6759 5.95657 11.8648 6.15803C12.0536 6.35949 12.0434 6.67591 11.842 6.86477L7.84197 10.6148C7.64964 10.7951 7.35036 10.7951 7.15803 10.6148L3.15803 6.86477C2.95657 6.67591 2.94637 6.35949 3.13523 6.15803Z" fill="currentColor" fill-rule="evenodd" clip-rule="evenodd"></path></svg> */}
        </button>
        {isOpen && (
          <ul className="absolute mt-1 max-h-60 overflow-y-auto  bg-gray-700 rounded-md shadow-lg z-20">
            {playlists.map(([name, id]) => (
              <li
                key={id}
                className="px-3 py-2 cursor-pointer hover:bg-gray-600"
                onClick={() => handlePlaylistSelect(id)}
              >
                {name}
              </li>
            ))}
          </ul>
        )}
      </div>
    );
  }
  
  export default PlaylistDropdown;