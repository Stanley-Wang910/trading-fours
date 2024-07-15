import React from "react";
import { motion, useMotionValue, useMotionTemplate } from "framer-motion";
import GlossyContainer from "./GlossyContainer.js";

const RecommendationDesc = ({ recommendations, demo = false }) => {
  if (demo) return null;

  const isPlaylist = recommendations.top_genres && recommendations.p_features;
  console.log(recommendations.id);

  function formatDuration(ms) {
    const hours = Math.floor(ms / 3600000);
    const minutes = Math.floor((ms % 3600000) / 60000);

    return `${hours ? `${hours} hours` : ""}${minutes ? `, ${minutes} minutes` : ""}`;
  }

  return (
    <div className="w-[35vw] lg:ml-[10vh] mt-8">
      <div className="mr-4">
        {isPlaylist ? (
          <>
            <motion.div className="w-[15vw] mx-auto" whileTap={{ scale: 0.95 }}>
              <a
                href={`https://open.spotify.com/playlist/${recommendations.id}`}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-block"
              >
                <img
                  src={recommendations.p_features.playlist_image}
                  alt={recommendations.p_features.playlist_name}
                  className="w-full rounded-xl "
                />
              </a>
            </motion.div>
            {/* <motion.div
              className={`relative lg:w-[20vw] h-[15vh] inline-flex }`}
              initial={{ scale: 1.0, opacity: 1 }}
              animate={{}}
              transition={{ duration: 1, ease: [0.22, 0.68, 0.31, 1.0] }}
              // onHoverStart={() => {
              //   setIsDemoContainerHovered(true);
              // }}
              // onHoverEnd={() => {
              //   setIsDemoContainerHovered(false);
              // }}
            >
              <GlossyContainer
                className="relative h-full w-full opacity-[100%]"
                degree={2}
                radius="550"
                brightness="0.15"
                gradientPoint="ellipse_at_top_right"
                gradientColor="from-slate-800/60 via-slate-900/60 to-slate-800/20"
                shadow={false}
              > */}
            <div className="text-center">
              <h1 className="text-2xl text-center bg-gradient-to-b from-amber-400 to-custom-brown bg-clip-text text-transparent font-bold italic">
                {recommendations.p_features.playlist_name}
              </h1>
              {/* <h2 className="text-xl font-semibold text-gray-400 mb-4 text-center">
                <span className="text-gray-400 font-bold">
                  {recommendations.top_genres.join(", ")}
                </span>{" "}
                recommendations
              </h2> */}

              <span className="text-gray-400 text-md font-semibold">
                <a
                  href={recommendations.p_features.playlist_owner_link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover-effect-link"
                  data-replace={recommendations.p_features.playlist_owner}
                >
                  <span>{recommendations.p_features.playlist_owner}</span>
                </a>{" "}
                <br />
                <span className="text-sm block mt-2">
                  {recommendations.p_features.num_tracks} Tracks,{" "}
                  {formatDuration(recommendations.p_features.total_duration_ms)}
                </span>
              </span>
            </div>
            {/* </GlossyContainer>
            </motion.div> */}
          </>
        ) : (
          <h2 className="text-xl font-semibold text-gray-400 mb-4 text-center">
            <span className="text-yellow-600 font-bold italic">
              {recommendations.track}
            </span>{" "}
            by{" "}
            <span className="text-gray-400 font-bold italic">
              {recommendations.artist}
            </span>
            , released in{" "}
            <span className="text-gray-400 font-semibold">
              {recommendations.release_date}
            </span>
          </h2>
        )}
      </div>
    </div>
  );
};

export default RecommendationDesc;
