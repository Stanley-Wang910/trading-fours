import React from "react";
import { motion } from "framer-motion";
import VideoEmbed from "./VideoEmbed.js";
import AnimatedDivider from "./AnimatedDivider.js";

function Showcase({ isDiv2Visible, isVideoEmbedVisible, token }) {
  return (
    <div
      className={`mt-[8vh] sm:translate-x-[5vw] lg:translate-x-0 ${isDiv2Visible ? "" : "cursor-events-none invisible user-select-none"}`}
    >
      <motion.div
        className={`mb-6  montserrat-reg w-full text-lg flex-col flex translate-x-[10vw] translate-y-5 `}
        initial={{ opacity: 0 }}
        animate={{ opacity: isDiv2Visible ? 1 : 0 }}
        transition={{ duration: 0.5, ease: "easeInOut" }}
      >
        <span className="bg-gradient-to-r from-gray-300 to-gray-200 bg-clip-text text-transparent font-bold">
          Watch the{" "}
          <span className="bg-gradient-to-r from-custom-brown to-amber-400 bg-clip-text text-transparent font-bold">
            Showcase
          </span>
        </span>
      </motion.div>
      <AnimatedDivider
        direction="left"
        isVisible={isDiv2Visible}
        className="absolute"
        width="39vw"
        xOffset="8vw"
        yOffset={0}
      />

      <VideoEmbed
        isVisible={isVideoEmbedVisible}
        id="tzjeOJVYI7o"
        title="Demo"
        className="rounded-lg mt-4 w-full lg:max-w-[35vw] sm:max-w-[45vw] mx-auto inline-flex my-auto "
      />
    </div>
  );
}

export default React.memo(Showcase);
