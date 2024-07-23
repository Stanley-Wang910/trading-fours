import React from "react";
import { motion } from "framer-motion";
import PopularityBar from "./PopularityBar.js";
// import GlossyContainer from "./GlossyContainer.js";
import AnimatedCounter from "./AnimatedCounter.js";

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

    return `${hours ? `${hours}hr` : ""}${minutes ? `${hours ? "" : ""} ${minutes}min` : ""}${seconds ? `${minutes ? "" : ""} ${seconds}s` : ""}`;
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
        w-auto max-w-[40vw] mx-auto mt-10 lg:ml-[1.5vw] sm:ml-0.5 h-auto 
        `}
    >
      <div className="flex flex-col md:flex-row sm:items-start lg:items-start sm:space-y-2 lg:space-y-4 md:space-y-0 md:space-x-4 ">
        <div // Image
          className={`${isShuffling || lastActionShuffle ? "opacity-100" : "opacity-0"} w-full lg:w-[12vw] sm:w-[15vw] max-w-xs
                ${animate && shouldAnimate ? "recsDesc-fade-in" : ""} 
                ${animateOut && shouldAnimate ? "recsDesc-fade-out" : ""}
            
            `}
        >
          <motion.div
            className={` `}
            whileTap={{ scale: 0.95 }}
            whileHover={{ opacity: 0.8 }}
          >
            <a
              onClick={() => {
                setTimeout(() => {
                  const url = `https://open.spotify.com/${isPlaylist ? `playlist` : `track`}/${recommendations.id}`;
                  window.open(url, "_blank", "noopener,noreferrer");
                }, 200); // Delay of 1000 milliseconds (1 second)
              }}
              className="inline-block cursor-pointer"
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
        <div className="md:w-[15vw] w-full sm:text-left">
          <div
            className={`${isShuffling || lastActionShuffle ? "opacity-100" : "opacity-0"}
            //  ${animate && shouldAnimate ? "recsDesc-fade-in" : ""} 
            //     ${animateOut && shouldAnimate ? "recsDesc-fade-out" : ""}
            `}
          >
            <h1
              className={`lg:text-2xl sm:text-xl text-amber-500 font-bold italic lg:mb-2 sm:mb-1
              `}
            >
              {isPlaylist
                ? recommendations.p_features.playlist_name
                : recommendations.t_features.name}
            </h1>
            <span className="text-gray-400 lg:text-base sm:text-sm font-semibold ">
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
          <div
            className={`text-gray-400 sm:text-left font-semibold lg:text-sm sm:text-xs block lg:mt-2 sm:mt-1 ${isShuffling || lastActionShuffle ? "opacity-100" : "opacity-0"}
                           ${animate && shouldAnimate ? "recsDesc-fade-in1" : ""} 
                            ${animateOut && shouldAnimate ? "recsDesc-fade-out1" : ""}`}
          >
            <span>
              {`${isPlaylist ? `${recommendations.p_features.num_tracks} Tracks` : `${formatDate(recommendations.t_features.release_date)}`}`}
              <br />
              {isPlaylist
                ? formatDuration(recommendations.p_features.total_duration_ms)
                : formatDuration(recommendations.t_features.total_duration_ms)}
              <br />
            </span>
          </div>
        </div>
      </div>
      <div
        className={`mt-2 text-gray-400 sm:text-left font-semibold lg:text-sm sm:text-xs ${isShuffling || lastActionShuffle ? "opacity-100" : "opacity-0"}
                    ${animate && shouldAnimate ? "recsDesc-fade-in2" : ""} 
                    ${animateOut && shouldAnimate ? "recsDesc-fade-out2" : ""}`}
      >
        {isPlaylist && (
          <span className="mt-2 text-gray-300">
            Defining Genres:
            <br />
            {Object.entries(recommendations.p_features.display_genres).map(
              ([genre, percentage], index, array) => (
                <React.Fragment key={genre}>
                  {genre}:{" "}
                  <span className="text-amber-400">
                    {
                      <AnimatedCounter
                        value={(percentage * 100).toFixed(1)}
                        isCountVisible={true}
                        durationMs={500}
                      />
                    }
                    %{index < array.length - 1 && <br />}
                  </span>
                </React.Fragment>
              )
            )}
          </span>
        )}
        <div className="mt-2">
          {isPlaylist ? "Average Track Popularity:" : "Track Popularity"}
        </div>
        <div className={`w-full md:max-w-[13vw] mt-2 `}>
          <motion.div className="flex items-center ">
            <div className="flex-grow">
              <PopularityBar
                popularity={
                  isPlaylist
                    ? recommendations.p_features.avg_popularity
                    : recommendations.t_features.popularity
                }
                orientation="horizontal"
                delay={0.6} // Delay until recsDesc-fade-in1 animation finishes
              />{" "}
            </div>
            <div className="flex-shrink-0 min-w-[40px] ml-2 text-amber-400">
              <AnimatedCounter
                value={
                  isPlaylist
                    ? recommendations.p_features.avg_popularity
                    : recommendations.t_features.popularity
                }
                isCountVisible={true}
                durationMs={150}
              />
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default RecommendationDesc;
