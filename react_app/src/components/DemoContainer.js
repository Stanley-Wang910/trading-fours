import React, { useState, useEffect, useMemo, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import GlossyContainer from "./GlossyContainer";
import RecommendationsList from "./RecommendationList";
import SearchBar from "./SearchBar";

const DemoContainer = ({
  isDemoVisible,
  isDemoContainerHovered,
  setIsDemoContainerHovered,
  searchAnimate,
  recAnimate,
}) => {
  const [isLargeScreen, setIsLargeScreen] = useState(false);

  useEffect(() => {
    const checkScreenSize = () => {
      setIsLargeScreen(window.innerWidth >= 1024);
    };

    checkScreenSize();

    window.addEventListener("resize", checkScreenSize);

    return () => {
      window.removeEventListener("resize", checkScreenSize);
    };
  }, []);

  const containerAnimationProps = useMemo(
    () => ({
      x: isDemoVisible ? "51vw" : "56vw",
      opacity: isDemoVisible ? 1 : 0,
    }),
    [isDemoVisible]
  );

  const handleHoverStart = useCallback(() => {
    setIsDemoContainerHovered(true);
  }, [setIsDemoContainerHovered]);

  const handleHoverEnd = useCallback(() => {
    setIsDemoContainerHovered(false);
  }, [setIsDemoContainerHovered]);

  const mockRecommendations = {
    playlist: "Demo Playlist",
    top_genres: ["Pop", "Rock", "Electronic"],
    recommended_ids: [
      "3BdHMOIA9B0bN53jbE5nWe", // Live from kitchen
      "5WbfFTuIldjL9x7W6y5l7R", // Pol
      "5DRnssBoVo8e7uAQZkNT8O",
    ],
  };
  const noop = () => {};

  return (
    <AnimatePresence>
      {isLargeScreen && (
        <motion.div
          className={`absolute z-20 inline-flex ${isDemoVisible ? "cursor-events-auto" : "cursor-events-none invisible user-select-none lg:block hidden"}`}
          initial={{ scale: 1.0, x: "54vw", opacity: 0 }}
          animate={containerAnimationProps}
          transition={{ duration: 1, ease: [0.22, 0.68, 0.31, 1.0] }}
          onHoverStart={handleHoverStart}
          onHoverEnd={handleHoverEnd}
        >
          <GlossyContainer
            className="relative md:w-[40vw] h-[70vh] opacity-[100%]"
            degree={2}
            radius="550"
            brightness="0.15"
            gradientPoint="ellipse_at_top_right"
            gradientColor="from-slate-800/60 via-slate-900/60 to-slate-800/20"
            shadow={false}
          >
            <div className="text-[1.4em] lato-regular font-bold  mt-12 px-12  ">
              <span className=" bg-gradient-to-b from-gray-200 to-gray-400 bg-clip-text text-transparent ">
                <span className="bg-gradient-to-r from-custom-brown to-amber-400 bg-clip-text text-transparent">
                  Infinite
                </span>{" "}
                possibilities for where the music takes{" "}
                <span className="bg-gradient-to-r from-custom-brown to-amber-400 bg-clip-text text-transparent">
                  you
                </span>
                .
              </span>
              <span className="  mt-4 text-sm text-gray-400 leading-snug block">
                Enter any playlist or track — a unique improvisation of a sound
                or vibe you want to capture — and receive a brand new take on
                it.
              </span>
            </div>
            <motion.div
              className="mt-10 pointer-events-auto w-[33vw]  "
              initial={{ opacity: 0 }}
              animate={{
                scale: isDemoContainerHovered ? 1 : 0.95,
                x: searchAnimate
                  ? isDemoContainerHovered
                    ? "12%"
                    : "5%"
                  : "15%",
                y: isDemoContainerHovered ? "30%" : "10%",
                opacity: searchAnimate ? 1 : 0,
              }}
              transition={{ duration: 0.75, ease: [0.22, 0.68, 0.31, 1.0] }}
            >
              <SearchBar demo={true} />
            </motion.div>
            <motion.div
              className="absolute pointer-events-auto mt-6"
              animate={{
                x: recAnimate
                  ? isDemoContainerHovered
                    ? "8%"
                    : "12%"
                  : "-10%",
                y: recAnimate ? (isDemoContainerHovered ? "2%" : "10%") : "2%",

                scale: isDemoContainerHovered ? 1 : 1,
                opacity: searchAnimate ? 1 : 0,
              }}
              transition={{ duration: 0.75, ease: [0.22, 0.68, 0.31, 1.0] }}
            >
              <RecommendationsList
                recommendations={mockRecommendations}
                onRecommendations={noop}
                setIsLoading={noop}
                query="demo query"
                position=""
                onTogglePosition={noop}
                setFavoritedTracks={noop}
                animateOut={false}
                setAnimateOut={noop}
                demo={true}
              />
            </motion.div>
          </GlossyContainer>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default React.memo(DemoContainer);
