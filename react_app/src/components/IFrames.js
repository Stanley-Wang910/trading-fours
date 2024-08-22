import React, { useState, useEffect, useRef, useCallback } from "react";
import axios from "axios";
import { motion } from "framer-motion";

const IFrameItem = React.memo(
  ({
    id,
    index,
    showPlaylistRecs,
    loaded,
    visibleButtons,
    handleTrackRecommend,
    handleLoad,
    demo,
  }) => {
    const [isHovered, setisHovered] = useState(null);
    const [isButtonHovered, setIsButtonHovered] = useState(null);

    const handleHoverStart = useCallback(() => {
      setisHovered(true);
    }, []);

    const handleHoverEnd = useCallback(() => {
      setisHovered(false);
    }, []);

    const handleButtonEnter = useCallback(() => {
      setIsButtonHovered(true);
    }, []);

    const handleButtonLeave = useCallback(() => {
      setIsButtonHovered(false);
    }, []);

    return (
      <motion.li
        key={index}
        className="w-full bg-transparent overflow-visible relative flex group"
        onHoverStart={handleHoverStart}
        onHoverEnd={handleHoverEnd}
      >
        {loaded && visibleButtons && (
          <motion.button
            className={`absolute left-0 
                  ${showPlaylistRecs ? "pr-4" : "pr-1"}
                  top-1/2`}
            onClick={() => (demo ? null : handleTrackRecommend(index))}
            onMouseEnter={handleButtonEnter}
            onMouseLeave={handleButtonLeave}
            whileTap={{ scale: 1.05 }}
            initial={{ opacity: 0, x: "0%", y: "-50%" }}
            animate={{
              opacity: isHovered ? 1 : 0,
              x: isHovered ? "-75%" : "0%",
              y: isHovered ? "-50%" : "-50%",
              scale: isButtonHovered ? 1.1 : 1.0,
            }}
            transition={{ duration: 0.2 }}
          >
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <motion.path
                fillRule="evenodd"
                clipRule="evenodd"
                d="M10.1205 19.0028C8.94206 18.9775 8 18.015 8 16.8363C8 15.6576 8.94206 14.6951 10.1205 14.6698C11.2988 14.6951 12.2409 15.6576 12.2409 16.8363C12.2409 18.015 11.2988 18.9775 10.1205 19.0028V19.0028Z"
                animate={{
                  stroke: isButtonHovered ? "#fbbf24" : "#cbd5e1",
                }}
                transition={{ duration: 0.3 }}
                stroke-width="1.5"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
              <motion.path
                d="M11.5024 16.8358C11.5024 17.25 11.8382 17.5858 12.2524 17.5858C12.6666 17.5858 13.0024 17.25 13.0024 16.8358H11.5024ZM13.0024 8.50279C13.0024 8.08857 12.6666 7.75279 12.2524 7.75279C11.8382 7.75279 11.5024 8.08857 11.5024 8.50279H13.0024ZM12.2524 8.50279H11.5024C11.5024 8.71537 11.5926 8.91798 11.7506 9.06021C11.9086 9.20244 12.1196 9.27093 12.331 9.24866L12.2524 8.50279ZM12.2524 7.00279H13.0024C13.0024 6.98925 13.0021 6.97573 13.0013 6.96221L12.2524 7.00279ZM12.8061 5.5565L13.3365 6.08683L12.8061 5.5565ZM14.2524 5.00279L14.2118 5.75169C14.2254 5.75242 14.2389 5.75279 14.2524 5.75279V5.00279ZM15.4084 5.00279V5.75279L15.4119 5.75278L15.4084 5.00279ZM16.9927 6.49867L16.2437 6.53814V6.53814L16.9927 6.49867ZM15.5744 8.15279L15.4991 7.40657L15.4958 7.40691L15.5744 8.15279ZM13.0024 16.8358V8.50279H11.5024V16.8358H13.0024ZM13.0024 8.50279V7.00279H11.5024V8.50279H13.0024ZM13.0013 6.96221C12.9837 6.63607 13.1055 6.31779 13.3365 6.08683L12.2758 5.02617C11.7436 5.55838 11.4628 6.2918 11.5035 7.04336L13.0013 6.96221ZM13.3365 6.08683C13.5674 5.85587 13.8857 5.73402 14.2118 5.75169L14.293 4.25388C13.5414 4.21317 12.808 4.49396 12.2758 5.02617L13.3365 6.08683ZM14.2524 5.75279H15.4084V4.25279H14.2524V5.75279ZM15.4119 5.75278C15.8543 5.7507 16.2204 6.09636 16.2437 6.53814L17.7416 6.4592C17.6762 5.21805 16.6478 4.24695 15.4049 4.25279L15.4119 5.75278ZM16.2437 6.53814C16.267 6.97993 15.9393 7.36215 15.4991 7.40658L15.6497 8.89899C16.8863 8.77418 17.807 7.70036 17.7416 6.4592L16.2437 6.53814ZM15.4958 7.40691L12.1738 7.75691L12.331 9.24866L15.653 8.89866L15.4958 7.40691Z"
                animate={{
                  fill: isButtonHovered ? "#fbbf24" : "#cbd5e1",
                }}
                transition={{ duration: 0.3 }}
              />
            </svg>
          </motion.button>
        )}
        <div className="embed-container w-full">
          <div
            className={`${showPlaylistRecs ? "embed-p" : "embed"} ${loaded ? "active" : ""}`}
          >
            <iframe
              onLoad={() => handleLoad(index)}
              src={`https://open.spotify.com/embed/${
                showPlaylistRecs ? `playlist` : `track`
              }/${id}?utm_source=generator`}
              style={{ border: "none" }}
              width="100%"
              height={showPlaylistRecs ? "352" : "83"}
              allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
              loading="lazy"
            ></iframe>
          </div>
        </div>
      </motion.li>
    );
  }
);

function IFrames({
  recommendationsArray,
  visibleEmbeds,
  showPlaylistRecs,
  handleTrackRecommend,
  scrollContainerRef,
  setShowMeteors,
  lastActionShuffle,
  animateOut,
  demo,
}) {
  const [loaded, setLoaded] = useState([]);
  const [visibleButtons, setVisibleButtons] = useState({});

  console.log(recommendationsArray);

  const handleLoad = useCallback(
    (index) => {
      // Mark the embed as active
      const embedElements =
        scrollContainerRef.current?.querySelectorAll(".embed");
      if (embedElements?.[index]) {
        embedElements[index].classList.add("active");
      }

      // Update the loaded state
      setLoaded((prev) => {
        if (!prev.includes(index)) {
          return [...prev, index];
        }
        return prev;
      });
    },
    [scrollContainerRef]
  );

  useEffect(() => {
    if (recommendationsArray.length > 0 && loaded.length >= 5) {
      setTimeout(() => {
        setShowMeteors(true);
      }, 2000);
    }
  }, [loaded.length, recommendationsArray.length, setShowMeteors]);

  useEffect(() => {
    loaded.forEach((index) => {
      if (!visibleButtons[index]) {
        const timer = setTimeout(() => {
          setVisibleButtons((prev) => ({ ...prev, [index]: true }));
        }, 1750); // Animation time for embed-container

        return () => clearTimeout(timer);
      }
    });
  }, [loaded, visibleButtons]);

  useEffect(() => {
    // Effect to prevent premature rendering out and in of iframes on shufle
    if (lastActionShuffle && animateOut) {
      setTimeout(() => {
        setLoaded([]);
      }, 500); // Timeout to wait until rec container aniamtes out
    }
  }, [lastActionShuffle, animateOut]);

  return (
    <ul className="space-y-5 z-10 relative">
      {recommendationsArray.slice(0, visibleEmbeds).map((id, index) => (
        <IFrameItem
          id={id}
          index={index}
          showPlaylistRecs={showPlaylistRecs}
          loaded={loaded.includes(index)}
          visibleButtons={visibleButtons[index]}
          handleTrackRecommend={handleTrackRecommend}
          handleLoad={handleLoad}
          demo={demo}
        />
      ))}
    </ul>
  );
}

export default React.memo(IFrames);
