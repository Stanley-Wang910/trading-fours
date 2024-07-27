import React, { useState, useEffect, useRef, useCallback } from "react";
import axios from "axios";
import clsx from "clsx";

function PlaylistDropdown({
  onRecommendations,
  setIsLoading,
  onQueryChange,
  setIsLocalLoading,
  setAnimateOut,
  setLastActionShuffle,
  userPlaylistIds,
  setUserPlaylistIds,
}) {
  // State variables
  const [playlists, setPlaylists] = useState([]); // Holds list of playlists
  const [selectedPlaylist, setSelectedPlaylist] = useState(""); // Holds the selected playlist
  const [isOpen, setIsOpen] = useState(false); // Determines if the dropdown is open
  const [hoveredPlaylist, setHoveredPlaylist] = useState(null); // State for if playlist is hovered
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 }); // Caculates the mouse position
  const imageRef = useRef(null); // Reference for image preview, used to handle when display
  const [searchQuery, setSearchQuery] = useState(""); // Holds the search playlists query
  const [showImagePreview, setShowImagePreview] = useState(false); // Determines if the image preview is shown
  const [keyImagePreview, setKeyImagePreview] = useState(false);
  const [focusedIndex, setFocusedIndex] = useState(0); // Holds the index of the focused playlist
  const [isKeyNavigating, setIsKeyNavigating] = useState(false);
  const [hasMouseMoved, setHasMouseMoved] = useState(true); // Determines if the mouse has moved post key navigation
  const [focusedItemPos, setFocusedItemPos] = useState({ top: 0, left: 0 });

  // Refs
  const dropdownRef = useRef(null); // Reference for the dropdown
  const searchInputRef = useRef(null); // Reference for the search input
  const listRef = useRef(null); // Reference dropdownRef // Effecgt hook to fetch playlists
  const itemsRef = useRef([]); // Reference for the items in the list

  const filteredPlaylists = playlists.filter((playlist) =>
    playlist[0].toLowerCase().includes(searchQuery.toLowerCase())
  );

  useEffect(() => {
    const fetchPlaylists = async () => {
      try {
        const response = await axios.get(
          `${process.env.REACT_APP_BACKEND_URL}/t4/search`,
          { withCredentials: true }
        );
        setPlaylists(response.data || []);
        console.log(response);
      } catch (error) {
        console.error("Error fetching playlists", error);
      }
    };

    fetchPlaylists();
  }, []); // dropdownRefunt

  useEffect(() => {
    setUserPlaylistIds(playlists.map((item) => item[1]));
  }, [playlists]); // This effect runs whenever playlists changes

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
          mousePosition.y < listRect.top + scrollTop ||
          mousePosition.y > listRect.bottom + scrollTop;

        if (isOutsideListVertically) {
          // console.log("Mouse is outside the list vertically");
          setShowImagePreview(false);
        }
      }
    };

    const handleMouseMove = (event) => {
      setMousePosition({ x: event.pageX, y: event.pageY });
      setHasMouseMoved(true); // Set to true when mouse moves
    };

    const handleClickOutside = (event) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target) &&
        listRef.current &&
        !listRef.current.contains(event.target)
      ) {
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

  const handlePlaylistSelect = useCallback(
    async (id) => {
      // Why is this not Callback?
      setLastActionShuffle(false);
      setSelectedPlaylist(id);
      setIsOpen(false);
      setAnimateOut(true);
      setTimeout(async () => {
        console.log("User saved playlists", userPlaylistIds);
        setIsLocalLoading(true); // Set the local loading state to true : for the playbutton change on searchdropdownRef
        setIsLoading(true); // Set the global loading state to true : for loading animation
        onQueryChange(id); // Set Query Change to ensure playlist data stored in session : recognized by RecommendationList Comp. for Shuffle
        try {
          const response = await axios.post(
            `${process.env.REACT_APP_BACKEND_URL}/t4/recommend?link=${id}`,
            { userPlaylistIds },
            { withCredentials: true }
          );
          onRecommendations(response.data || []);
        } catch (error) {
          console.error("Error fetching search results", error);
          onRecommendations([]);
        }
        setIsLocalLoading(false); // Set the local loading state to false
        setIsLoading(false);
        setAnimateOut(false);
      }, 500); // Change based on the recommendation animation times
    },
    [
      onQueryChange,
      onRecommendations,
      setIsLoading,
      setAnimateOut,
      setIsLocalLoading,
      userPlaylistIds,
      setLastActionShuffle,
    ]
  );

  const handleKeyDown = (e) => {
    if (!isOpen) return;

    setIsKeyNavigating(true);
    setHasMouseMoved(false);
    setKeyImagePreview(true);
    setShowImagePreview(false);

    switch (e.key) {
      case "ArrowDown":
        e.preventDefault();
        setHoveredPlaylist(null); // Clear the hovered playlist when navigating with keys
        setFocusedIndex((prevIndex) => {
          const newIndex = (prevIndex + 1) % filteredPlaylists.length;
          if (itemsRef.current[newIndex]) {
            const item = itemsRef.current[newIndex];
            const rect = item.getBoundingClientRect();
            const newTop = rect.top + window.scrollY;
            const newLeft = rect.left;
            setFocusedItemPos({ top: newTop, left: newLeft });
            item.scrollIntoView({ block: "nearest" });
          }
          return newIndex;
        });
        break;
      case "ArrowUp":
        e.preventDefault();
        setHoveredPlaylist(null);
        setFocusedIndex((prevIndex) => {
          const newIndex =
            (prevIndex - 1 + filteredPlaylists.length) %
            filteredPlaylists.length;
          if (itemsRef.current[newIndex]) {
            const item = itemsRef.current[newIndex];
            const rect = item.getBoundingClientRect();
            const newTop = rect.top + window.scrollY;
            const newLeft = rect.left;
            setFocusedItemPos({ top: newTop, left: newLeft });
            item.scrollIntoView({ block: "nearest" });
            console.log("item position", { top: newTop, left: newLeft });
          }
          return newIndex;
        });
        break;
      case "Enter":
        e.preventDefault();
        if (focusedIndex >= 0 && focusedIndex < filteredPlaylists.length) {
          const selectedPlaylist = filteredPlaylists[focusedIndex];
          if (selectedPlaylist && selectedPlaylist.length > 1) {
            handlePlaylistSelect(filteredPlaylists[focusedIndex][1]);
          } else {
            console.error("Selected playlist is invalid", selectedPlaylist);
          }
        }
        break;
      default:
        break;
    }

    setIsKeyNavigating(false); // Reset setIsKeyNavigating(false);
  };

  useEffect(() => {
    if (isOpen) {
      window.addEventListener("keydown", handleKeyDown);
    } else {
      window.removeEventListener("keydown", handleKeyDown);
    }

    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen, handleKeyDown, filteredPlaylists.length]);

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
            placeholder="Search Playlists..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="px-3 py-2 w-full bg-gray-800 text-gray-300 rounded-md focus:outline-none text-sm"
            ref={searchInputRef}
          />
        </li>
        {filteredPlaylists.map((playlist, index) => {
          if (!playlist || playlist.length < 2) return null;
          const [name, id] = playlist;
          return (
            <li
              key={id}
              className={clsx(
                "px-3 py-2 cursor-pointer text-gray-300 text-sm  border-b border-gray-500",
                { "bg-gray-600": focusedIndex === index }
              )}
              onClick={() => handlePlaylistSelect(id)}
              onMouseEnter={() => {
                if (!isKeyNavigating && hasMouseMoved) {
                  setHoveredPlaylist(playlist);
                  setShowImagePreview(true);
                  setKeyImagePreview(false);
                  setFocusedIndex(index);
                }
              }}
              onMouseLeave={() => {
                setHoveredPlaylist(null);
                setShowImagePreview(false);
              }}
              ref={(element) => (itemsRef.current[index] = element)}
            >
              {name}
            </li>
          );
        })}
      </ul>
      {isOpen && hoveredPlaylist && showImagePreview && hoveredPlaylist[2] && (
        <div
          ref={imageRef}
          className="fixed z-50 p-2 transition-transform duration-300 ease-out"
          style={{
            transform: `translate(${mousePosition.x - 700}px, ${mousePosition.y - 302}px)`, // Adjust position without affecting the scale
            width: "120px",
            // height: "200px",
          }}
        >
          <img
            src={hoveredPlaylist[2]}
            alt={hoveredPlaylist[0]}
            className="w-full translate-x-[-20px] translate-y-[-170px] lg:translate-x-[-400px] lg:translate-y-[-170px] rounded shadow-lg pointer-events-none"
          />
        </div>
      )}

      {isOpen &&
        focusedIndex >= 0 &&
        !showImagePreview &&
        keyImagePreview &&
        filteredPlaylists[focusedIndex] &&
        (() => {
          const { top, left } = focusedItemPos;
          return (
            <div
              className="fixed z-50 p-2 transition-transform duration-300 "
              style={{
                transform: `translate(${left - window.innerWidth * 0.95}px, ${top - window.innerHeight * 0.5}px)`, // Adjust position to the left of the focused item

                width: "120px",
              }}
            >
              <img
                src={filteredPlaylists[focusedIndex][2]}
                alt={filteredPlaylists[focusedIndex][0]}
                className="w-full rounded lg:translate-x-[335%]  shadow-lg pointer-events-none"
              />
            </div>
          );
        })()}
    </div>
  );
}

export default PlaylistDropdown;
