import React from "react";
import { motion, useMotionValue, useMotionTemplate } from "framer-motion";
import GlossyContainer from "./GlossyContainer.js";

const RecommendationDesc = ({
  recommendations,
  animate,
  animateOut,
  demo = false,
}) => {
  if (demo) return null;

  const isPlaylist = recommendations.top_genres && recommendations.p_features;
  console.log(recommendations);

  function formatDuration(ms) {
    const hours = Math.floor(ms / 3600000);
    const minutes = Math.floor((ms % 3600000) / 60000);
    const seconds = Math.floor((ms % 60000) / 1000);

    return `${hours ? `${hours} hours` : ""}${minutes ? `${hours ? ", " : ""} ${minutes} minutes` : ""}${seconds ? `${minutes ? ", " : ""} ${seconds} seconds` : ""}`;
  }

  function formatDate(date) {
    var options = {
      weekday: "long",
      year: "numeric",
      month: "long",
      day: "numeric",
    };
    const d = new Date(date);
    return `${d.toLocaleDateString("en-US", options)}`;
  }

  return (
    <div
      className={`
        w-[35vw] lg:ml-[10vh] mt-[10vh]
       
        `}
    >
      <div className="mr-4">
        <div
          className={`opacity-0
                ${animate ? "recsDesc-fade-in" : ""} 
                ${animateOut ? "recsDesc-fade-out" : ""}
            
            `}
        >
          <motion.div
            className={`w-[15vw] mx-auto 
                  `}
            whileTap={{ scale: 0.95 }}
          >
            <a
              href={`https://open.spotify.com/track/${recommendations.id}`}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block"
            >
              <img
                src={
                  isPlaylist
                    ? recommendations.p_features.playlist_image
                    : recommendations.t_features.track_image
                }
                alt={
                  isPlaylist
                    ? recommendations.p_features.playlist_name
                    : recommendations.t_features.name
                }
                className="w-full rounded-xl "
              />
            </a>
          </motion.div>
          <div className="text-center">
            <h1
              className={`text-2xl text-center text-amber-500 font-bold italic
              `}
            >
              {isPlaylist
                ? recommendations.p_features.playlist_name
                : recommendations.t_features.name}
            </h1>
            <span className="text-gray-400 text-md font-semibold">
              <a
                href={
                  isPlaylist
                    ? recommendations.p_features.playlist_owner_link
                    : recommendations.t_features.artist_url
                }
                target="_blank"
                rel="noopener noreferrer"
                className="hover-effect-link"
                data-replace={
                  isPlaylist
                    ? recommendations.p_features.playlist_owner
                    : recommendations.t_features.artist
                }
              >
                <span>
                  {isPlaylist
                    ? recommendations.p_features.playlist_owner
                    : recommendations.t_features.artist}
                </span>
              </a>{" "}
              <br />
            </span>
          </div>
        </div>
        <span
          className={`text-gray-400 text-center font-semibold text-sm block mt-2 opacity-0
                           ${animate ? "recsDesc-fade-in1" : ""} 
                            ${animateOut ? "recsDesc-fade-out1" : ""}`}
        >
          {`${isPlaylist ? `${recommendations.p_features.num_tracks} Tracks` : `Released ${formatDate(recommendations.t_features.release_date)}`}`}
          <br />
          {isPlaylist
            ? formatDuration(recommendations.p_features.total_duration_ms)
            : formatDuration(recommendations.t_features.total_duration_ms)}
        </span>
      </div>
    </div>
  );
};

export default RecommendationDesc;
