import React, { useEffect, useState, useRef } from "react";
import axios from "axios";
import { motion } from "framer-motion";
import { cn } from "../utils/cn.ts";

export const VerticalScrollingTracks = ({
  trackIds,
  direction = "up",
  speed = "normal",
  pauseOnHover = true,
  className,
}) => {
  const containerRef = useRef(null);
  const scrollerRef = useRef(null);
  useEffect(() => {
    addAnimation();
  }, []);

  const [start, setStart] = useState(false);
  // const [isLoading, setIsLoading] = useState(true);
  // const [trackIds, setTrackIds] = useState([]);
  // const [fetchError, setFetchError] = useState(false);

  // useEffect(() => {
  //   if (!isLoading && (fetchError || trackIds.length === 0)) {
  //     console.log("No recommendations found, setting default track ids");
  //     setTrackIds(DEFAULT_TRACK_IDS);
  //   }
  // }, [isLoading, fetchError, trackIds]);

  function addAnimation() {
    if (containerRef.current && scrollerRef.current) {
      const scrollerContent = Array.from(scrollerRef.current.children);
      scrollerContent.forEach((item) => {
        const duplicatedItem = item.cloneNode(true);
        scrollerRef.current.appendChild(duplicatedItem);
      });
      getDirection();
      getSpeed();
      setStart(true);
    }
  }

  const getDirection = () => {
    if (containerRef.current) {
      if (direction === "up") {
        containerRef.current.style.setProperty(
          "--animation-direction",
          "forwards"
        );
      } else {
        containerRef.current.style.setProperty(
          "--animation-direction",
          "reverse"
        );
      }
    }
  };

  const getSpeed = () => {
    if (containerRef.current) {
      if (speed === "fast") {
        containerRef.current.style.setProperty("--animation-duration", "20s");
      } else if (speed === "normal") {
        containerRef.current.style.setProperty("--animation-duration", "40s");
      } else {
        containerRef.current.style.setProperty("--animation-duration", "80s");
      }
    }
  };

  return (
    <div
      ref={containerRef}
      className={cn(
        "scroller relative z-20 max-h-[60vh] overflow-hidden [mask-image:linear-gradient(to_bottom,transparent,white_20%,white_80%,transparent)]",
        className
      )}
    >
      <ul
        ref={scrollerRef}
        className={cn(
          "flex flex-col min-h-full shrink-0 gap-4 py-4 h-max",
          start && "animate-scroll",
          pauseOnHover && "hover:[animation-play-state:paused]"
        )}
      >
        {trackIds.map((trackId, idx) => (
          <li key={`${trackId}-${idx}`} className="w-full h-20 flex-shrink-0">
            <iframe
              src={`https://open.spotify.com/embed/track/${trackId}?utm_source=generator`}
              width="100%"
              height="80"
              allowFullScreen=""
              allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
              loading="lazy"
              onLoad={() =>
                console.log(`Iframe with trackId ${trackId} loaded`)
              } // Add this line
            />
          </li>
        ))}
      </ul>
    </div>
  );
};

export default VerticalScrollingTracks;
