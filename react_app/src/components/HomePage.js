import React, { useState, useEffect, useRef, useCallback } from "react";
import axios from "axios";
import { TextGenerateEffect } from "./ui/text-generate-effect.tsx";
import {
  motion,
  useMotionValue,
  useMotionTemplate,
  AnimatePresence,
  useAnimation,
} from "framer-motion";
import GlossyContainer from "./GlossyContainer.js";
import VerticalScrollingTracks from "./VerticalScrollingTracks.js";
import "../styles/Components/HomePage.css";

const AnimatedCounter = ({ value, isCountVisible }) => {
  const counterRef = useRef(null);
  const [currentValue, setCurrentValue] = useState(0);
  const [isFirstRender, setIsFirstRender] = useState(true);

  useEffect(() => {
    if (!isCountVisible) return;

    const animateValue = (start, end, duration) => {
      start = Number(start);
      end = Number(end);
      // const start = parseInt(start.replace(/,/g, ""), 10);
      // const end = parseInt(end.replace(/,/g, ""), 10);
      let startTimestamp = null;
      const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        const animatedValue = Math.floor(progress * (end - start) + start);
        if (counterRef.current) {
          counterRef.current.textContent = animatedValue.toLocaleString();
        }
        setCurrentValue(animatedValue);
        if (progress < 1) {
          window.requestAnimationFrame(step);
        }
      };
      window.requestAnimationFrame(step);
    };

    if (isFirstRender) {
      animateValue(Math.max(0, value - 100), value, 200);
      setIsFirstRender(false);
      console.log("First render");
    } else {
      animateValue(currentValue, value, 200);
    }
  }, [value, isFirstRender, currentValue, isCountVisible]);

  if (!isCountVisible) return null;

  return <span ref={counterRef}>{currentValue.toLocaleString()}</span>;
};

const useScrollAnimation = () => {
  const [isVisible, setIsVisible] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.unobserve(entry.target);
        }
      },
      {
        threshold: 0,
      }
    );

    if (ref.current) {
      observer.observe(ref.current);
    }

    return () => {
      if (ref.current) {
        observer.unobserve(ref.current);
      }
    };
  }, []);

  return [ref, isVisible];
};

export default function HomePage() {
  const DEFAULT_TRACK_IDS = [
    "2IwL0fwckPbO9sau1EHslH", // Live from kitchen
    "5gcYcp5Tg5u4SO8zVa4nSS", // Pol
    "5bemClhFeQ7fcth7mjjnKO",
    "1LLgtfY4umP78sh5LmyVpW",
    "1AJHaJFNM2Q4UpJ1fG1bIi",
    "0y5CnV2idm2KkQEudDjfDT",
    "4vjvx7Zxkb4AltGcZ0BBvI",
    "1UbwpyozDvufPs6aNPW3ti",
    "6zMQAgnWYRvzNIQGfjmXad",
    "5GUYJTQap5F3RDQiCOJhrS",
    // "1",
    // "1",
    // "1",
    // "1",
    // "1",
  ];
  const [isDescVisible, setIsDescVisible] = useState(false);
  const [isTooltipVisible, setIsTooltipVisible] = useState(false);
  const [totalRecs, setTotalRecs] = useState(0);
  const [hourlyIncrease, setHourlyIncrease] = useState(0);
  // const [isCountVisible, setIsCountVisible] = useState(false);
  const [isScrollVisible, setIsScrollVisible] = useState(false);
  const [isTextGenComplete, setIsTextGenComplete] = useState(false);
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);
  const [isMouseOver, setIsMouseOver] = useState(false);
  const [isTotalRecsHovered, setIsTotalRecsHovered] = useState(false);
  const [isMoreInfoHovered, setIsMoreInfoHovered] = useState(false);
  const [isSwapped, setIsSwapped] = useState(false);
  const [isAnimating, setIsAnimating] = useState(false);
  const totalRecRef = useRef(null);

  const [scrollTotalRecsRef, isTotalRecsVisible] = useScrollAnimation();
  const [scrollMoreInfoRef, isMoreInfoVisible] = useScrollAnimation();
  const [trackIds, setTrackIds] = useState(DEFAULT_TRACK_IDS);
  const [isRandomLoading, setIsRandomLoading] = useState(true);

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
        y: isMoreInfoHovered ? "-45%" : "-50%",
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
                ? "33%"
                : "30%"
              : "25%",
      y:
        isTotalRecsHovered && !isMoreInfoHovered
          ? "-37%"
          : isMoreInfoHovered && isTotalRecsHovered
            ? "-10%"
            : isMoreInfoVisible
              ? "-42%"
              : "-50%",

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
                  ? "33%"
                  : "30%"
                : "25%",
        y:
          isMoreInfoHovered && !isTotalRecsHovered
            ? "-37%"
            : isMoreInfoHovered && isTotalRecsHovered
              ? "-10%"
              : isMoreInfoVisible
                ? "-42%"
                : "-50%",
        scale: isMoreInfoHovered ? 0.98 : 1,
        zIndex: 10,
        opacity: isAnimating ? 0.5 : 1,
      };
    }

    return {
      x: isTotalRecsHovered ? "31%" : isTotalRecsVisible ? "30%" : "25%",
      y: isTotalRecsHovered ? "-45%" : "-50%",

      scale: 1,
      zIndex: 20,
      opacity: isAnimating ? 0.5 : 1,
    };
  };

  useEffect(() => {
    const getRandomRecs = async () => {
      try {
        const response = await axios.get(
          `${process.env.REACT_APP_BACKEND_URL}/random-recommendations`,
          { withCredentials: true }
        );
        if (response.data && response.data.length > 0) {
          setTrackIds(response.data);
          console.log("Random recommendations fetched:", response.data);
          console.log(trackIds, "Track ids");
        } else {
          console.log("Response null, setting default track ids");
          setTrackIds(DEFAULT_TRACK_IDS);
        }
      } catch (error) {
        console.error("Error fetching random recommendations", error);
        setTrackIds(DEFAULT_TRACK_IDS);
      } finally {
        setIsRandomLoading(false);
      }
    };
    getRandomRecs();
  }, []);

  function handleMouseMove({ currentTarget, clientX, clientY }) {
    const { left, top } = currentTarget.getBoundingClientRect();
    mouseX.set(clientX - left);
    mouseY.set(clientY - top);
  }

  function handleMouseEnter() {
    setIsMouseOver(true);
  }

  function handleMouseLeave() {
    setIsMouseOver(false);
  }

  const handleTextGenComplete = useCallback(() => {
    setIsTextGenComplete(true);
    setIsDescVisible(true);
    setIsScrollVisible(true);
  }, []);

  useEffect(() => {
    const getTotalRecs = async () => {
      try {
        const response = await axios.get(
          `${process.env.REACT_APP_BACKEND_URL}/total-recommendations`,
          { withCredentials: true }
        );
        const [total, hourly] = response.data;
        setTotalRecs(total);
        setHourlyIncrease(hourly);
        // console.log("Total recommendations fetched:", response.data);
      } catch (error) {
        console.error("Error fetching total recommendations", error);
      }
    };

    getTotalRecs();
    const intervalId = setInterval(getTotalRecs, 5000);

    return () => clearInterval(intervalId);
  }, []);

  return (
    <div className="mt-[55px]">
      <div
        onMouseMove={handleMouseMove}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        className="h-[60vh] w-full bg-slate-800 relative flex flex-col items-center justify-center overflow-visible"
      >
        {/* Dot background div with enhanced mask */}
        <div className="absolute inset-0">
          <div className="w-full h-full bg-dot-white/[0.4]"></div>
          <motion.div
            className="absolute inset-0 bg-dot-thick-amber-500 transition-opacity duration-1000 ease-in-out"
            animate={{ opacity: isMouseOver ? 1 : 0 }}
            initial={{ opacity: 0 }}
            style={{
              WebkitMaskImage: useMotionTemplate`
                radial-gradient(
                  250px circle at ${mouseX}px ${mouseY}px,
                  black 0%,
                  transparent 100%
                )
              `,
              maskImage: useMotionTemplate`
                radial-gradient(
                  250px circle at ${mouseX}px ${mouseY}px,
                  black 0%,
                  transparent 100%
                )
              `,
            }}
          />
          <div className="absolute inset-0 bg-gray-900 [mask-image:radial-gradient(ellipse_at_20%_50%,transparent_0%,rgba(0,0,0,0.5)_30%,black_70%)]"></div>
        </div>

        {/* Additional gradient overlay for smoother transition */}
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-gray-900/10 to-gray-900"></div>

        <div className="w-full justify-start -translate-y-[10%] translate-x-[10%]  montserrat-reg text-3xl relative">
          <TextGenerateEffect
            words={"Built, by design,\nFor the way\nYou listen."}
            highlightText="Built, For You"
            onComplete={handleTextGenComplete}
          />
          <div
            className={`
            text-sm mt-4 
            sm:w-[35vw]
            bg-gradient-to-br from-gray-400 to-gray-200 
            bg-clip-text text-transparent 
            transition-opacity duration-1000 
            ${isDescVisible && isTextGenComplete ? "opacity-100" : "opacity-0"}
            `}
          >
            An{" "}
            <div className="relative inline-block">
              <a
                onMouseEnter={() => setIsTooltipVisible(true)}
                onMouseLeave={() => setIsTooltipVisible(false)}
                href="https://github.com/Stanley-Wang910/spotify-rec-engine"
                target="_blank"
                rel="noopener noreferrer"
                className="hover-effect-link"
                data-replace="open-source"
              >
                <span>open-source</span>
              </a>

              <div
                className={`
                absolute top-3/4 transform -translate-y-8
                ml-2 px-2 py-0.5 bg-gray-700 text-slate-300 text-xs font-slim rounded-lg shadow-md
                whitespace-nowrap z-10 transition-all duration-300 ease-in-out
                ${
                  isTooltipVisible
                    ? "opacity-100 translate-x-2"
                    : "opacity-0 pointer-events-none translate-x-12"
                }
              `}
              >
                GitHub
              </div>
            </div>
            , solo-dev project, created with Spotify magic, <br />
            meant to inspire your streamlined discovery of good music.
          </div>
        </div>
        <div className="flex flex-col">
          <div
            className={`group absolute right-[10%] translate-x-[-10%] top-0 lg:w-[25vw] sm:w-[30vw] sm:translate-x-[20%] transition-all duration-1000 ease-in-out 
                        ${isScrollVisible ? "opacity-100" : "opacity-0"}`}
          >
            {!isRandomLoading && (
              <VerticalScrollingTracks
                trackIds={trackIds}
                direction="up"
                speed="very-slow"
                pauseOnHover={true}
              />
            )}
            <div className="bg-gradient-to-br w-full from-gray-300 to-slate-400 bg-clip-text text-transparent text-sm montserrat-reg absolute bottom-0 translate-x-3/4 right-1/2 translate-y-[8vh] opacity-0 group-hover:opacity-100 group-hover:translate-y-[6vh] transition-all duration-300">
              <div className="font-regular">Some of Today's Discoveries</div>
            </div>
          </div>
        </div>
      </div>
      <div ref={scrollTotalRecsRef} className="h-1 w-full mt-[35vh] absolute" />
      <div ref={scrollMoreInfoRef} className="h-1 w-full mt-[45vh] absolute" />
      <div className="relative">
        <div className="flex flex-col items-start">
          <div className="sm:-translate-x-14 lg:translate-x-0">
            <motion.div // Background Glossy Container
              className="absolute cursor-pointer"
              initial={{ scale: 1.0, opacity: 0, y: "-50%" }}
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
              onHoverStart={() => {
                if (!isSwapped) {
                  setIsTotalRecsHovered(true);
                }
                setIsMoreInfoHovered(true);
              }}
              onHoverEnd={() => {
                if (!isSwapped) {
                  setIsTotalRecsHovered(false);
                }
                setIsMoreInfoHovered(false);
              }}
            >
              <GlossyContainer className="" />
            </motion.div>
            <motion.div
              // ref={totalRecRef}
              className={`relative cursor-pointer`}
              initial={{ scale: 1, opacity: 0, y: "-50%" }}
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
              onHoverStart={() => {
                if (isSwapped) {
                  setIsMoreInfoHovered(true);
                }
                setIsTotalRecsHovered(true);
              }}
              onHoverEnd={() => {
                if (isSwapped) {
                  setIsMoreInfoHovered(false);
                }
                setIsTotalRecsHovered(false);
              }}
            >
              <GlossyContainer className="">
                <div className="text-sm montserrat-reg text-slate-300  py-3 px-3 ">
                  <motion.div
                    animate={{
                      color:
                        isTotalRecsHovered && !isSwapped
                          ? "rgb(148 163 184)"
                          : "rgb(203 213 225)",
                    }} // Using Tailwind colors: amber-400 and slate-400
                    transition={{ duration: 0.3 }}
                    onMouseEnter={() => {
                      console.log("hovered on new songs");
                    }}
                    onMouseLeave={() => {
                      console.log("hovered off new songs");
                    }}
                  >
                    New Songs Discovered
                  </motion.div>
                </div>
                <motion.div
                  className={`text-5xl pl-4 lato-regular  inline-flex transition-colors duration-300 
                  }`}
                  initial={{ scale: 1, opacity: 0, color: "rgb(148 163 184)" }}
                  animate={{
                    scale: isTotalRecsHovered && !isSwapped ? 1.08 : 1,
                    opacity: isTotalRecsVisible && !isSwapped ? 1 : 0,
                    x: isTotalRecsHovered && !isSwapped ? -18 : 0,
                    y: isTotalRecsHovered && !isSwapped ? -3 : 0,
                    color:
                      isTotalRecsHovered && !isSwapped
                        ? "rgb(203,213,225)" //slate-300
                        : "rgb(148 163 184)", //slate-400

                    // fill: isTotalRecsHovered
                    //   ? "rgba(125,20,205)"
                    //   : "rgba(203,213,225)", // slate-300
                  }}
                  transition={{
                    scale: { duration: 0.75, ease: [0.22, 0.68, 0.31, 1.0] },
                    x: { duration: 0.75, ease: [0.22, 0.68, 0.31, 1.0] },
                    y: { duration: 0.75, ease: [0.22, 0.68, 0.31, 1.0] },
                    opacity: { duration: 0.5, ease: "easeInOut" },
                    color: { duration: 0.3, ease: "easeInOut" }, // Change if needed
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
                  <AnimatedCounter
                    value={Number(totalRecs) || 0}
                    isCountVisible={isTotalRecsVisible}
                  />
                </motion.div>

                <div
                  className={`text-sm right-4 lato-regular absolute
                                 `}
                >
                  <motion.div
                    animate={{
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
          </div>

          {/* <div className="mt-4 text-white">Hello</div> */}
        </div>
      </div>
    </div>
  );
}
