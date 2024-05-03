import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import clsx from "clsx";

function PlaylistDropdown({ onRecommendations, setIsLoading, onQueryChange, setIsLocalLoading}) {
  // State variables
  const [playlists, setPlaylists] = useState([]); // Holds list of playlists
  const [selectedPlaylist, setSelectedPlaylist] = useState(""); // Holds the selected playlist
  const [isOpen, setIsOpen] = useState(false); // Determines if the dropdown is open
  const [hoveredPlaylist, setHoveredPlaylist] = useState(null); // State for if playlist is hovered
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 }); // Caculates the mouse position
  const imageRef = useRef(null); // Reference for image preview, used to handle when display
  const [searchQuery, setSearchQuery] = useState(""); // Holds the search playlists query
  const [showImagePreview, setShowImagePreview] = useState(false); // Determines if the image preview is shown
  
  // Refs
  const dropdownRef = useRef(null); // Reference for the dropdown
  const searchInputRef = useRef(null); // Reference for the search input
  const listRef = useRef(null); // Reference dropdownRef // Effecgt hook to fetch playlists 
  useEffect(() => {
    const fetchPlaylists = async () => {
      try {
        const response = await axios.get("/search");
        setPlaylists(response.data || []);
      } catch (error) {
        console.error("Error fetching playlists", error);
      }
    };

    fetchPlaylists();
  }, []); // dropdownRefunt
  
  // Effect hook to fcus on searchbar when Dropdown Opens
  useEffect(() => {
    if (isOpen && searchInputRef.current) {
      searchInputRef.current.focus({ preventScroll: true });
    }
  }, [isOpen]); // Runs when isOpen changes

  // Effect hook to handle mouse movement and clicks outside the dropdown
  useEffect(() => {
    const checkMousePosition = () => {
      if (listRef.current) {
        const listRect = listRef.current.getBoundingClientRect();
        const scrollTop = window.scrollY || document.documentElement.scrollTop;
        const isOutsideListVertically =
          mousePosition.y < listRect.top + scrollTop || mousePosition.y > listRect.bottom + scrollTop;

        if (isOutsideListVertically) {
          // console.log("Mouse is outside the list vertically");
          setShowImagePreview(false);
        }
      }
    };

    const handleMouseMove = (event) => {
      setMousePosition({ x: event.pageX, y: event.pageY });
    };

    const handleClickOutside = (event) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target) &&
        listRef.current && !listRef.current.contains(event.target)) {
        setIsOpen(false);
        setShowImagePreview(false);
      }
    };

    window.addEventListener("mousemove", handleMouseMove);
    document.addEventListener("mousedown", handleClickOutside);

    // Check mouse position when the search query changes
    checkMousePosition();

    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [searchQuery, mousePosition]);

  const handlePlaylistSelect = async (id) => {
    setSelectedPlaylist(id);
    setIsOpen(false);
    setIsLocalLoading(true); // Set the local loading state to true : for the playbutton change on seadropdownRef  
    setIsLoading(true); // Set the global loading state to true : for loading animation
    onQueryChange(id); // Set Query Change to ensure playlist data stored in session : recognized by RecommendationList Comp. for Shuffle
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
  
 const filteredPlaylists = playlists.filter((playlist) =>
    playlist[0].toLowerCase().includes(searchQuery.toLowerCase())
  );
   
  return (
    <div ref={dropdownRef} className="relative w-full max-w-md">
      <div className="dropdownButton relative inline-block">
        <button
          className={clsx(
            "py-2 rounded-full text-gray-200 placeholder-gray-400 flex items-center justify-between transition-transform-opacity duration-300 ",
            {
              "hover:translate-x-[5px]": !isOpen,
              "translate-x-[5px]": isOpen,
            }
          )}
          onClick={() => setIsOpen(!isOpen)}
        >
          <svg
            width="15"
            height="15"
            viewBox="0 0 15 15"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            className={clsx("transition duration-100", {
              "rotate-90": isOpen,
              "animate-click": isOpen,
              "animate-close": !isOpen,
            })}
          >
            <path
              d="M6.1584 3.13508C6.35985 2.94621 6.67627 2.95642 6.86514 3.15788L10.6151 7.15788C10.7954 7.3502 10.7954 7.64949 10.6151 7.84182L6.86514 11.8418C6.67627 12.0433 6.35985 12.0535 6.1584 11.8646C5.95694 11.6757 5.94673 11.3593 6.1356 11.1579L9.565 7.49985L6.1356 3.84182C5.94673 3.64036 5.95694 3.32394 6.1584 3.13508Z"
              fill="#cc8e15"
              fillRule="evenodd"
              clipRule="evenodd"
            ></path>
          </svg>
        </button>
        <div className="w-[115px] absolute top-1/2 left-full transform -translate-y-1/2 translate-x-2 ml-2 px-2 py-1 bg-gray-800 text-white text-xs font-semi-bold rounded opacity-0 pointer-events-none transition-opacity duration-300 tooltip">
          My Saved Playlists
        </div>
      </div>
       
        <ul
          className={clsx(
            "dropdown-height-animate overflow-y-auto absolute mt-3 w-80 bg-gray-700 rounded-xl shadow-lg z-20 transition-all duration-200 ease-in-out lg:translate-x-[-10px] translate-x-[-180px] custom-scrollbar",
            {
              "max-h-0": !isOpen,
              "max-h-[400px]": isOpen,
            }
          )} 
          
          ref={listRef}
        >
          <li className="px-3 py-2">
              <input
                type="text"
                placeholder="Search playlists..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="px-3 py-2 w-full bg-gray-800 text-gray-300 rounded-md focus:outline-none text-sm"
                ref={searchInputRef}
              />
          </li>
          {filteredPlaylists.map((playlist) => {
            if (!playlist || playlist.length < 2) return null;
            const [name, id] = playlist;
            return (
              <li 
                key={id} 
                className="px-3 py-2 cursor-pointer text-gray-300 text-sm hover:bg-gray-600 border-b border-gray-500" 
                onClick={() => handlePlaylistSelect(id)}
                onMouseEnter={() => {
                  setHoveredPlaylist(playlist)
                  setShowImagePreview(true)
                }}
                onMouseLeave={() => {
                  setHoveredPlaylist(null)
                  setShowImagePreview(false)
                }}
              >
                {name}
              </li>
            );
          })}
        </ul>
        {isOpen && hoveredPlaylist && showImagePreview && (
          <div
            ref={imageRef}
            className="fixed z-50 p-2 "
            style={{
              transform: `translate(${mousePosition.x-700}px, ${mousePosition.y - 302}px)`, // Adjust position without affecting the scale
              width: "120px"
              // height: "200px",
            }}
          >
            <img src={hoveredPlaylist[2]} alt={hoveredPlaylist[0]} className="w-full translate-x-[-20px] translate-y-[-170px] lg:translate-x-[-400px] lg:translate-y-[-170px] rounded shadow-lg pointer-events-none" />
          </div>
        )}
      </div>
    );
  }
  
  export default PlaylistDropdown;