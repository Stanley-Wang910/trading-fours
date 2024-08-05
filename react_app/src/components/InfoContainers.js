import React, { useState, useCallback } from "react";
import { motion } from "framer-motion";
import GlossyContainer from "./GlossyContainer";
import AnimatedCounter from "./AnimatedCounter.js";
import useDelayAnimation from "./DelayAnimation.js";
const InfoContainers = ({
  trendingGenres,
  totalRecs,
  hourlyIncrease,
  isDiv1Visible,
}) => {
  const [isTotalRecsHovered, setIsTotalRecsHovered] = useState(false);
  const [isMoreInfoHovered, setIsMoreInfoHovered] = useState(false);
  const [isSwapped, setIsSwapped] = useState(false);
  const [isAnimating, setIsAnimating] = useState(false);

  const isTotalRecsVisible = useDelayAnimation(isDiv1Visible, 300);
  const isMoreInfoVisible = useDelayAnimation(isTotalRecsVisible, 500);

  const handleContainerClick = () => {
    if (!isAnimating) {
      setIsAnimating(true);
      setIsSwapped(!isSwapped);
      setTimeout(() => setIsAnimating(false), 500);
    }
  };

  const getBackgroundPosition = () => {
    if (isSwapped) {
      return {
        x: isMoreInfoHovered ? "31%" : "30%",
        y: isMoreInfoHovered ? "5%" : "0%",
        scale: 1,
        zIndex: 20,
        opacity: isAnimating ? 0.5 : 1,
        // rotate: isAnimating ? 3 : 0,
      };
    }

    return {
      x:
        isTotalRecsHovered && !isMoreInfoHovered
          ? "40%"
          : isMoreInfoHovered && isTotalRecsHovered
            ? "43%"
            : isTotalRecsVisible
              ? isMoreInfoVisible
                ? "32.5%" // Starting State
                : "30%"
              : "28%",
      y:
        isTotalRecsHovered && !isMoreInfoHovered
          ? "13%"
          : isMoreInfoHovered && isTotalRecsHovered
            ? "40%"
            : isMoreInfoVisible
              ? "7.5%" // Starting State
              : "0%",

      scale: isTotalRecsHovered ? 0.98 : isMoreInfoVisible ? 0.98 : 1,
      zIndex: 10,
      opacity: isAnimating ? 0.5 : 1,
    };
  };

  const getForegroundPosition = () => {
    if (isSwapped) {
      return {
        x:
          isMoreInfoHovered && !isTotalRecsHovered
            ? "40%"
            : isMoreInfoHovered && isTotalRecsHovered
              ? "43%"
              : isTotalRecsVisible
                ? isMoreInfoVisible
                  ? "32.5%"
                  : "30%"
                : "28%",
        y:
          isMoreInfoHovered && !isTotalRecsHovered
            ? "13%"
            : isMoreInfoHovered && isTotalRecsHovered
              ? "40%"
              : isMoreInfoVisible
                ? "7.5%"
                : "0%",
        scale: isMoreInfoHovered ? 0.98 : 0.98,
        zIndex: 10,
        opacity: isAnimating ? 0.5 : 1,
      };
    }

    return {
      x: isTotalRecsHovered ? "31%" : isTotalRecsVisible ? "30%" : "28%",
      y: isTotalRecsHovered ? "5%" : "0%",

      scale: 1,
      zIndex: 20,
      opacity: isAnimating ? 0.5 : 1,
    };
  };

  const handleBackgroundHoverStart = useCallback(() => {
    if (!isSwapped) {
      setIsTotalRecsHovered(true);
    }
    setIsMoreInfoHovered(true);
  }, [isSwapped]);

  const handleBackgroundHoverEnd = useCallback(() => {
    if (!isSwapped) {
      setIsTotalRecsHovered(false);
    }
    setIsMoreInfoHovered(false);
  }, [isSwapped]);

  const handleForegroundHoverStart = useCallback(() => {
    if (isSwapped) {
      setIsMoreInfoHovered(true);
    }
    setIsTotalRecsHovered(true);
  }, [isSwapped]);

  const handleForegroundHoverEnd = useCallback(() => {
    if (isSwapped) {
      setIsMoreInfoHovered(false);
    }
    setIsTotalRecsHovered(false);
  }, [isSwapped]);

  return (
    <>
      <motion.div // Background Glossy Container
        className={`absolute z-30 inline-flex ${isTotalRecsVisible ? "cursor-pointer" : "cursor-events-none invisible user-select-none"}`}
        initial={{ scale: 1.0, opacity: 0 }}
        animate={{
          ...getBackgroundPosition(),
          opacity: isTotalRecsVisible ? 1 : 0,
        }}
        transition={
          isAnimating
            ? { duration: 0.5, ease: [0.68, -0.55, 0.27, 1.55] }
            : { duration: 0.5, ease: [0.22, 0.68, 0.31, 1.0] }
        }
        onClick={handleContainerClick}
        onHoverStart={handleBackgroundHoverStart}
        onHoverEnd={handleBackgroundHoverEnd}
      >
        <GlossyContainer gradientColor="from-slate-700/50  to-slate-900">
          <div className="text-sm montserrat-reg text-slate-300  py-3 px-3 ">
            <motion.div
              animate={{
                opacity: isMoreInfoVisible && isSwapped ? 1 : 0,

                color:
                  isMoreInfoHovered && isSwapped
                    ? "rgb(148 163 184)"
                    : "rgb(203 213 225)",
              }} // Using Tailwind colors: amber-400 and slate-400
              transition={{ duration: 0.3 }}
            >
              This Week's Trending Genres
            </motion.div>
          </div>
          <motion.div
            className={`text-[1.5em] px-4 py-1 lato-regular inline-flex 
                  }`}
            animate={{
              scale: isMoreInfoHovered && isSwapped ? 1.02 : 1,
              opacity: isMoreInfoVisible && isSwapped ? 1 : 0,
              x: isMoreInfoHovered && isSwapped ? 3 : 0,
              y: isMoreInfoHovered && isSwapped ? -3 : 0,
              color:
                isMoreInfoHovered && isSwapped
                  ? "rgb(203,213,225)" //slate-300
                  : "rgb(148 163 184)", //slate-400
            }}
            transition={{
              color: { duration: 0.3, ease: "easeInOut" }, // Change if needed
              scale: { duration: 0.75, ease: [0.22, 0.68, 0.31, 1.0] },
              x: { duration: 0.75, ease: [0.22, 0.68, 0.31, 1.0] },
              y: { duration: 0.75, ease: [0.22, 0.68, 0.31, 1.0] },
              opacity: { duration: 0.3, ease: "easeInOut" },
            }}
            style={{
              willChange: "transform",
            }}
          >
            <span className="tracking-tight  ">
              {trendingGenres.join(", ")}
            </span>
          </motion.div>
        </GlossyContainer>
      </motion.div>

      <motion.div
        className={`relative z-30 inline-flex ${isTotalRecsVisible ? "cursor-pointer" : "cursor-events-none invisible user-select-none"}`}
        initial={{ scale: 1, opacity: 0 }}
        animate={{
          ...getForegroundPosition(),

          opacity: isTotalRecsVisible ? 1 : 0,
        }}
        transition={
          isAnimating
            ? { duration: 0.5, ease: [0.68, -0.55, 0.27, 1.55] }
            : { duration: 0.5, ease: [0.22, 0.68, 0.31, 1.0] }
        }
        onClick={handleContainerClick}
        onHoverStart={handleForegroundHoverStart}
        onHoverEnd={handleForegroundHoverEnd}
      >
        <GlossyContainer gradientColor="from-slate-700/50 to-slate-900">
          <div className="w-full flex flex-col justify-center items-start  overflow-hidden">
            <motion.div
              className="text-sm montserrat-reg text-slate-300 pl-3 pt-3 "
              animate={{
                opacity: isTotalRecsVisible && !isSwapped ? 1 : 0,
                color:
                  isTotalRecsHovered && !isSwapped
                    ? "rgb(148 163 184)"
                    : "rgb(203 213 225)",
              }} // Using Tailwind colors: amber-400 and slate-400
              transition={{ duration: 0.3 }}
              // onMouseEnter={() => {
              //   console.log("hovered on new songs");
              // }}
              // onMouseLeave={() => {
              //   console.log("hovered off new songs");
              // }}
            >
              New Songs Discovered
            </motion.div>
          </div>
          <motion.div
            className={`text-5xl pl-4 lato-regular inline-flex items-center mt-[0.5em] 
                  }`}
            animate={{
              scale: isTotalRecsHovered && !isSwapped ? 1.08 : 1,
              opacity: isTotalRecsVisible && !isSwapped ? 1 : 0,
              x: isTotalRecsHovered && !isSwapped ? -10 : 0,
              y: isTotalRecsHovered && !isSwapped ? "-2vh" : "-1.5vh",
              color:
                isTotalRecsHovered && !isSwapped
                  ? "rgb(203,213,225)" //slate-300
                  : "rgb(148 163 184)", //slate-400
            }}
            transition={{
              color: { duration: 0.3, ease: "easeInOut" }, // Change if needed

              scale: { duration: 0.75, ease: [0.22, 0.68, 0.31, 1.0] },
              x: { duration: 0.75, ease: [0.22, 0.68, 0.31, 1.0] },
              y: { duration: 0.75, ease: [0.22, 0.68, 0.31, 1.0] },
              opacity: { duration: 0.3, ease: "easeInOut" },
            }}
            style={{
              willChange: "transform",
            }}
            onMouseEnter={() => {
              console.log("hovered on Total Recs Counter");
            }}
            onMouseLeave={() => {
              console.log("hovered off Total Recs Counter");
            }}
          >
            <span className="tracking-tight ">
              <AnimatedCounter
                value={Number(totalRecs) || 0}
                isCountVisible={isTotalRecsVisible}
              />
            </span>
          </motion.div>

          <div className={`text-sm right-4 lato-regular absolute  bottom-0`}>
            <motion.div
              animate={{
                opacity: isTotalRecsVisible && !isSwapped ? 1 : 0,
                color:
                  isTotalRecsHovered && !isSwapped
                    ? "rgb(251, 191, 36, 0.8)"
                    : "#64748b",
              }} // Using Tailwind colors: amber-400 and slate-400
              transition={{ duration: 0.3, ease: "easeInOut" }}
              onMouseEnter={() => {
                console.log("hovered on Counter");
              }}
              onMouseLeave={() => {
                console.log("hovered off Counter");
              }}
            >
              ↑{" "}
              <AnimatedCounter
                value={Number(hourlyIncrease) || 0}
                isCountVisible={isTotalRecsVisible}
              />{" "}
              in the past hour
            </motion.div>
          </div>
        </GlossyContainer>
      </motion.div>
    </>
  );
};

export default React.memo(InfoContainers);
