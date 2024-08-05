import React, { useState, useCallback } from "react";
import { motion } from "framer-motion";

function PlaylistToggle({
  setAnimateOut,
  setLastActionShuffle,
  setIsLocalLoading,
  setIsLoading,
  setIsShuffling,
  animate,
  animateOut,
  setShowPlaylistRecs,
  showPlaylistRecs,
}) {
  const [showToggleToolTip, setShowToggleToolTip] = useState(false);

  const handleHoverStart = useCallback(() => {
    setShowToggleToolTip(true);
  }, []);

  const handleHoverEnd = useCallback(() => {
    setShowToggleToolTip(false);
  }, []);

  const handleShowPlaylistsToggle = () => {
    setAnimateOut(true);
    setLastActionShuffle(true);
    setTimeout(() => {
      setIsLocalLoading(true);
      setIsLoading(true);
      setIsShuffling(true);

      setShowPlaylistRecs(!showPlaylistRecs);

      setTimeout(() => {
        setIsLoading(false);
        setIsLocalLoading(false);
        setAnimateOut(false);
        setIsShuffling(false);
      }, 1500);
    }, 500);
  };

  return (
    <div className=" relative top-1/2 -translate-y-[5vh] right-0 lg:ml-4 sm:ml-1 lg:mr-[1.5vw] overflow-x-visible">
      <div
        className={`opacity-0 relative inline-block 
      ${animate ? "playlistToggle-fade-in opacity-0" : ""} 
      ${animateOut ? "playlistToggle-fade-out opacity-100" : ""}
      `}
      >
        <motion.svg
          onClick={() => {
            setTimeout(() => {
              handleShowPlaylistsToggle();
            }, 50);
          }}
          whileTap={{ rotate: -10, transition: { duration: 0.05 } }}
          whileHover={{
            fill: "#fbbf24",
            scale: 1.05,
            rotate: 10,
            transition: { duration: 0.1 },
          }}
          onHoverStart={handleHoverStart}
          onHoverEnd={handleHoverEnd}
          fill="#cbd5e1"
          width="28px"
          height="28px"
          className="cursor-pointer focus:outline-none"
          viewBox="0 0 22 22"
          xmlns="http://www.w3.org/2000/svg"
          id="memory-music-note"
        >
          <path d="M11 2H18V7H13V18H12V19H11V20H7V19H6V18H5V14H6V13H7V12H11V2M11 15H10V14H8V15H7V17H8V18H10V17H11V15Z" />
        </motion.svg>
        <div
          className={`absolute top-0 left-0 translate-y-[3vh] py-2 text-amber-400 text-[0.75em] font-bold
      ${showToggleToolTip ? "opacity-100" : "opacity-0"} pointer-events-none transition-opacity duration-300 tooltip`}
        >
          {showPlaylistRecs ? "Tracks" : "Playlists"}
        </div>
      </div>
    </div>
  );
}

export default React.memo(PlaylistToggle);
