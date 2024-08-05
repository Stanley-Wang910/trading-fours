import React, { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";

// This is causing the page to not finish loading

const VideoEmbed = ({ isVisible, id, title, className = "" }) => {
  const [isHovering, setIsHovering] = useState(false);
  const isMounted = useRef(true);
  useEffect(() => {
    return () => {
      isMounted.current = false;

      // Delay cleanup for 5 seconds
      setTimeout(() => {
        if (!isMounted.current) {
          // Clean up Youtube related stuff
          const youtubeIframe = document.querySelector(
            `iframe[src*="youtube.com/embed/${id}"]`
          );
          if (youtubeIframe) {
            youtubeIframe.remove();
          }
        }
      }, 5000);
    };
  }, [id]);

  return (
    <motion.div
      className={`aspect-[16/9] ${className}`}
      initial={{ opacity: 0, y: "0vh" }}
      animate={{
        opacity: isVisible ? (isHovering ? 1 : 0.9) : 0,
        x: isVisible ? "9vw" : "6vw",
        scale: isHovering ? 1 : 0.98,
        boxShadow: isHovering
          ? "10px 10px 20px rgba(0, 0, 0, 0.5)"
          : "5px 5px 10px rgba(0, 0, 0, 0.5)",
      }}
      transition={{ duration: 0.5, ease: [0.22, 0.68, 0.31, 1.0] }}
      onHoverStart={() => setIsHovering(true)}
      onHoverEnd={() => setIsHovering(false)}
      style={{
        backdropFilter: "blur(5px)",
        WebkitBackdropFilter: "blur(5px)",
      }}
    >
      <div
        className="absolute inset-0 rounded-lg pointer-events-none transition-opacity duration-300"
        style={{
          boxShadow: "inset 0 0 0 2.5px rgba(128, 128, 128, 0.2)",
          opacity: isHovering ? 1 : 0.5,
        }}
      />
      <iframe
        className="w-full h-full rounded-lg"
        // src={`https://www.youtube.com/embed/${id}`}
        title={title}
        // frameBorder="0"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        allowFullScreen
      ></iframe>
    </motion.div>
  );
};

export default VideoEmbed;
