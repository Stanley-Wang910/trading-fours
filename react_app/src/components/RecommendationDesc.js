import React from "react";
import { motion } from "framer-motion";
// import GlossyContainer from "./GlossyContainer.js";

const RecommendationDesc = ({
  recommendations,
  animate,
  animateOut,
  isShuffling,
  lastActionShuffle,
  demo = false,
}) => {
  if (demo) return null;

  const shouldAnimate = !lastActionShuffle && !isShuffling;
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
      // weekday: "long",
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
        w-auto max-w-[40vw] mx-auto mt-10 ml-[5vw] mr-[4vw]
       
        `}
    >
      <div className="flex flex-col md:flex-row sm:items-center md:items-start space-y-4 md:space-y-0 md:space-x-6 ">
        <div
          className={`${isShuffling || lastActionShuffle ? "opacity-100" : "opacity-0"} w-full md:w-[15vw] sm:w-[15vw] max-w-xs
                ${animate && shouldAnimate ? "recsDesc-fade-in" : ""} 
                ${animateOut && shouldAnimate ? "recsDesc-fade-out" : ""}
            
            `}
        >
          <motion.div className={` `} whileTap={{ scale: 0.95 }}>
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
        </div>
        <div className="md:text-left md:w-2/3 w-full sm:text-center">
          <div
            className={`${isShuffling || lastActionShuffle ? "opacity-100" : "opacity-0"}
             ${animate && shouldAnimate ? "recsDesc-fade-in" : ""} 
                ${animateOut && shouldAnimate ? "recsDesc-fade-out" : ""}
            `}
          >
            <h1
              className={`text-2xl text-amber-500 font-bold italic mb-2
              `}
            >
              {isPlaylist
                ? recommendations.p_features.playlist_name
                : recommendations.t_features.name}
            </h1>
            <span className="text-gray-400 text-md font-semibold ">
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
              </a>
            </span>
          </div>
          <span
            className={`text-gray-400 md:text-left sm:text-center font-semibold text-sm block mt-2 ${isShuffling || lastActionShuffle ? "opacity-100" : "opacity-0"}
                           ${animate && shouldAnimate ? "recsDesc-fade-in1" : ""} 
                            ${animateOut && shouldAnimate ? "recsDesc-fade-out1" : ""}`}
          >
            {`${isPlaylist ? `${recommendations.p_features.num_tracks} Tracks` : `${formatDate(recommendations.t_features.release_date)}`}`}
            <br />
            {isPlaylist
              ? formatDuration(recommendations.p_features.total_duration_ms)
              : formatDuration(recommendations.t_features.total_duration_ms)}
          </span>
        </div>
      </div>
    </div>
  );
};

export default RecommendationDesc;
