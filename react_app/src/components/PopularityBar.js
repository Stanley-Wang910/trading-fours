import React from "react";
import { motion } from "framer-motion";

const PopularityBar = ({
  popularity,
  delay = 0,
  orientation = "horizontal",
  height = "100px",
}) => {
  const clampedPopularity = Math.min(Math.max(popularity, 0), 100);

  const containerStyle = {
    width: orientation === "horizontal" ? "100%" : "1.25vh",
    height: orientation === "horizontal" ? "1.25vh" : height,
    backgroundColor: "#94a3b8",
    borderRadius: "5px", // Rounded corners
    overflow: "hidden",
    boxSizing: "border-box",
    margin: 0,
    padding: 0, // To fix bar displacement
  };

  const barStyle = {
    height: "100",
    width: orientation === "horizontal" ? "100%" : "100%",
    height: orientation === "horizontal" ? "100%" : "100%",
    background:
      orientation === "horizontal"
        ? "linear-gradient(to right, #cc8e15, #f59e0b)"
        : "linear-gradient(to top, #cc8e15, #f59e0b)",
  };

  const variants = {
    initial: {
      scaleX: orientation === "horizontal" ? 0 : 1,
      scaleY: orientation === "horizontal" ? 1 : 0,
      originX: 0,
      originY: 1,
    },
    animate: {
      scaleX: orientation === "horizontal" ? clampedPopularity / 100 : 1,
      scaleY: orientation === "horizontal" ? 1 : clampedPopularity / 100,
    },
  };

  return (
    <div style={containerStyle} className="text-amber-500">
      <motion.div
        style={barStyle}
        variants={variants}
        initial="initial"
        animate="animate"
        transition={{ duration: 0.5, ease: "easeInOut", delay: delay }}
      />
    </div>
  );
};

export default PopularityBar;
