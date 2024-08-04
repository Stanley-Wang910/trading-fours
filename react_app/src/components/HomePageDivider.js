import React from "react";
import { motion } from "framer-motion";
import AnimatedDivider from "./AnimatedDivider.js";

const HomePageDivider = ({ isDiv1Visible }) => {
  return (
    <>
      <motion.div
        className="mb-6 translate-x-[10vw] montserrat-reg w-full text-lg flex-col flex"
        initial={{ opacity: 0 }}
        animate={{ opacity: isDiv1Visible ? 1 : 0 }}
        transition={{ duration: 0.5, ease: "easeInOut" }}
      >
        <span className="bg-gradient-to-r from-gray-300 to-gray-200 bg-clip-text text-transparent font-bold">
          A Look{" "}
          <span className="bg-gradient-to-r from-custom-brown to-amber-400 bg-clip-text text-transparent font-bold">
            Inside
          </span>
        </span>
      </motion.div>
      <AnimatedDivider
        direction="left"
        isVisible={isDiv1Visible}
        className=""
        width="90vw"
        xOffset="8vw"
        yOffset={-20}
      />
    </>
  );
};

export default React.memo(HomePageDivider);
