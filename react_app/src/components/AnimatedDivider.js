import React from "react";
import { motion } from "framer-motion";

const AnimatedDivider = ({
  isVisible,
  direction = "left",
  className = "",
  width = "100vw",
  xOffset = 0,
  yOffset = 0,
  color = "rgb(71, 85, 105)",
  ...props
}) => {
  const gradientDir = direction === "left" ? "to right" : "to left";
  return (
    <motion.div
      className={`h-[2.5px] w-full rounded-full  ${className}`}
      initial={{ scaleX: 0 }}
      animate={isVisible ? { scaleX: 1 } : { scaleX: 0 }}
      transition={{ duration: 0.3, ease: "easeInOut" }}
      style={{
        width,
        transformOrigin: direction,
        background: `linear-gradient(${gradientDir}, rgba(71, 85, 105, 1), rgba(71, 85, 105, 0))`, //rgba for accurate gradient
        position: "absolute",
        x: xOffset,
        y: yOffset,
      }}
      {...props}
    />
  );
};

export default AnimatedDivider;
