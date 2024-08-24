import React, { useState, useCallback, useEffect } from "react";
import axios from "axios";
import { useMotionTemplate, useMotionValue, motion } from "framer-motion";
import PlaylistDropdown from "./PlaylistDropdown";
import GradientBackground from "./GradientBackground";

function SearchBar({
  onRecommendations,
  setIsLoading,
  isLocalLoading,
  setIsLocalLoading,
  onQueryChange,
  setAnimateOut,
  setLastActionShuffle,
  userPlaylistIds,
  setUserPlaylistIds,
  demo = false,
  lyds = false,
  ily = false,
}) {
  const [query, setQuery] = useState("");
  const [isHovered, setIsHovered] = useState(false);
  // const [isLocalLoading, setIsLocalLoading] = useState(false);

  const radius = 100;
  const [visible, setVisible] = React.useState(false);
  let mouseX = useMotionValue(0);
  let mouseY = useMotionValue(0);

  useEffect(() => {
    if (lyds) {
      setQuery(""); // Clear the input when lyds becomes true
    }
  }, [lyds]);

  // Memoized callback for handling mouse move
  const handleMouseMove = useCallback(
    ({ currentTarget, clientX, clientY }) => {
      const { left, top } = currentTarget.getBoundingClientRect();
      mouseX.set(clientX - left);
      mouseY.set(clientY - top);
    },
    [mouseX, mouseY]
  );

  // Memoized callback for handling form submission
  const handleSubmit = useCallback(
    async (e) => {
      e.preventDefault();

      if (demo) {
        return;
      }

      setLastActionShuffle(false);

      setAnimateOut(true);
      setTimeout(async () => {
        setIsLoading(true);
        setIsLocalLoading(true);
        onQueryChange(query);

        try {
          const response = await axios.post(
            `/t4/recommend?link=${query}`,
            { userPlaylistIds },
            { withCredentials: true }
          );
          onRecommendations(response.data || []);
          setQuery("");
        } catch (error) {
          console.error("Error fetching search results", error);
          onRecommendations([]);
          setQuery("");
        }

        setIsLoading(false);
        setIsLocalLoading(false);
        setAnimateOut(false);
      }, 500);
    },
    [
      demo,
      setIsLocalLoading,
      query,
      onQueryChange,
      onRecommendations,
      setIsLoading,
      setAnimateOut,
      setLastActionShuffle,
      userPlaylistIds,
      setUserPlaylistIds,
    ]
  );

  return (
    <div className="flex items-center mx-4">
      <div className="SearchBar w-full flex justify-center items-center px-2">
        {/* <motion.div
          // style={{
          //   background: useMotionTemplate`
          //   radial-gradient(
          //     ${visible ? radius + "px" : "0px"} circle at ${mouseX}px ${mouseY}px,
          //     #cc8e15,
          //     transparent 80%
          //   )
          // `,
          // }}
          onMouseMove={handleMouseMove}
          onMouseEnter={() => setVisible(true)}
          onMouseLeave={() => setVisible(false)}
          className="relative w-full max-w-md p-[2px] rounded-full" */}
        {/* > */}
        <form onSubmit={handleSubmit} className="relative w-full">
          <motion.input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={
              ily
                ? "I Love You More!"
                : lyds
                  ? "I Love You!"
                  : "Paste a Spotify Playlist or Track Link!"
            }
            className={`px-3 py-2 pr-10 border-none rounded-full w-full focus:outline-none ${
              isHovered ? "bg-gray-600/35 " : "bg-gray-600/50 "
            } text-gray-300 placeholder-gray-400 font-semibold transition-colors duration-200 `}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
          />
          <motion.button
            type="submit"
            whileTap={{ scale: 0.95, onDurationChange: 0 }}
            animate={{ scale: isLocalLoading ? 0.9 : 1 }}
            transition={{ type: "spring", stiffness: 300, damping: 20 }}
            className="absolute right-1 top-1 transform -translate-y-1/2 text-black p-1 rounded-full inline-flex items-center justify-center w-8 h-8 bg-custom-brown hover:bg-yellow-700"
            aria-label="Search"
          >
            {isLocalLoading ? (
              <img
                src="/icons8-pause-button-30.png"
                alt="Pause"
                width="17"
                height="17"
              />
            ) : (
              <img
                src="/icons8-play-button-30.png"
                alt="Play"
                width="15"
                height="15"
              />
            )}
          </motion.button>
        </form>
        {/* </motion.div> */}
      </div>
      {!demo && (
        <div className="">
          <PlaylistDropdown
            onRecommendations={onRecommendations}
            setIsLoading={setIsLoading}
            onQueryChange={onQueryChange}
            setIsLocalLoading={setIsLocalLoading}
            setAnimateOut={setAnimateOut}
            setLastActionShuffle={setLastActionShuffle}
            userPlaylistIds={userPlaylistIds}
            setUserPlaylistIds={setUserPlaylistIds}
            lyds={lyds}
            ily={ily}
          />
        </div>
      )}
    </div>
  );
}

export default React.memo(SearchBar); // May need to change
