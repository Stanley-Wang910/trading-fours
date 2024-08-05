import React, { useState, useCallback } from "react";
import { motion } from "framer-motion";

function LoadMoreButton({
  visibleEmbeds,
  animate,
  animateOut,
  setVisibleEmbeds,
  showPlaylistRecs,
  scrollContainerRef,
}) {
  const [scrollPosition, setScrollPosition] = useState(0);

  // Memoized callbakc to handle loading more embeds
  const handleLoadMore = useCallback(() => {
    const incrementCounter = showPlaylistRecs ? 3 : 5;
    const scrollMultiplier = showPlaylistRecs ? 372 : 132;
    const newVisibleEmbeds = visibleEmbeds + incrementCounter;
    setVisibleEmbeds(newVisibleEmbeds);
    // setContainerHeight((prev) => Math.min(prev + extendRec, maxHeight));

    setTimeout(() => {
      const scrollContainer = scrollContainerRef.current;
      if (scrollContainer) {
        const newScrollPosition =
          (newVisibleEmbeds - incrementCounter) * scrollMultiplier;
        scrollContainer.scrollTo({
          top: newScrollPosition,
          behavior: "smooth",
        });
        setScrollPosition(newScrollPosition);
      }
    }, 500);
  }, [visibleEmbeds, showPlaylistRecs, scrollContainerRef, setVisibleEmbeds]);

  return (
    <motion.button
      className="rounded-full"
      whileTap={{ scale: 0.9 }}
      onClick={handleLoadMore}
    >
      <div
        className={` opacity-0 z-50 px-4 py-2 bg-custom-brown shadow-xl font-bold rounded-full hover:bg-yellow-700 
        ${animate ? "loadMore-fade-up opacity-0" : ""} 
        ${animateOut ? "loadMore-fade-out opacity-100" : ""}
        `}
      >
        <img src="/plus.png" alt="Arrow" width={20} height={20} />
      </div>
    </motion.button>
  );
}

export default React.memo(LoadMoreButton);
