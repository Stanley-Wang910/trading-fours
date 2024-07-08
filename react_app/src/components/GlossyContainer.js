import React, { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";

const GlossyContainer = ({ children }) => {
  const containerRef = useRef(null);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [isHovering, setIsHovering] = useState(false);
  const [opacity, setOpacity] = useState(0);

  useEffect(() => {
    const handleMouseMove = (event) => {
      if (containerRef.current) {
        const rect = containerRef.current.getBoundingClientRect();
        setMousePosition({
          x: event.clientX - rect.left,
          y: event.clientY - rect.top,
        });
      }
    };

    const handleMouseEnter = () => {
      setIsHovering(true);
      setTimeout(() => setOpacity(1), 50);
    };

    const handleMouseLeave = () => {
      setIsHovering(false);
      setOpacity(0);
      setMousePosition({ x: 0, y: 0 });
    };

    const container = containerRef.current;
    if (container) {
      container.addEventListener("mousemove", handleMouseMove);
      container.addEventListener("mouseenter", handleMouseEnter);
      container.addEventListener("mouseleave", handleMouseLeave);
    }

    return () => {
      if (container) {
        container.removeEventListener("mousemove", handleMouseMove);
        container.removeEventListener("mouseenter", handleMouseEnter);
        container.removeEventListener("mouseleave", handleMouseLeave);
      }
    };
  }, []);

  const gradientStyle = {
    background: `radial-gradient(circle 250px at ${mousePosition.x}px ${mousePosition.y}px, rgba(125,20,205,0.2), transparent 80%)`,
  };

  return (
    <motion.div
      ref={containerRef}
      className="relative p-6 rounded-lg w-[30vw] h-[15vh] overflow-hidden bg-[radial-gradient(ellipse_at_bottom_left,_var(--tw-gradient-stops))] from-slate-800 via-gray-900 to-slate-900"
      style={{
        boxShadow: "0 4px 30px rgba(0, 0, 0, 0.1)",
        backdropFilter: "blur(5px)",
        "--border-color": "rgba(128, 128, 128, 0.2)",
      }}
      transition={{ type: "spring", stiffness: 300, damping: 20 }}
    >
      <div
        className="absolute inset-0 rounded-lg pointer-events-none transition-opacity duration-500"
        style={{
          boxShadow: "inset 0 0 0 1.5px var(--border-color)",
          opacity: isHovering ? 1 : 0.5,
        }}
      />
      {isHovering && (
        <div
          className="absolute inset-0 pointer-events-none"
          style={{
            ...gradientStyle,
            opacity: opacity,
            transition: "opacity 0.3s ease-in-out",
            filter: "blur(40px)",
          }}
        />
      )}

      <div className="relative z-10">{children}</div>
    </motion.div>
  );
};

export default GlossyContainer;
