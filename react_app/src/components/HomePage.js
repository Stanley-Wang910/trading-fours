import React, { useState, useEffect, useRef, useCallback } from "react";
import axios from "axios";
import { TextGenerateEffect } from "./ui/text-generate-effect.tsx";
import {
  motion,
  useMotionValue,
  useMotionTemplate,
  useAnimation,
} from "framer-motion";
import GlossyContainer from "./GlossyContainer.js";
import VerticalScrollingTracks from "./VerticalScrollingTracks.js";
import "../styles/Components/HomePage.css";

const AnimatedCounter = ({ value, isVisible }) => {
  const counterRef = useRef(null);
  const [currentValue, setCurrentValue] = useState(0);
  const [isFirstRender, setIsFirstRender] = useState(true);

  useEffect(() => {
    if (!isVisible) return;

    const animateValue = (start, end, duration) => {
      let startTimestamp = null;
      const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        const animatedValue = Math.floor(progress * (end - start) + start);
        if (counterRef.current) {
          counterRef.current.innerHTML = animatedValue;
        }
        setCurrentValue(animatedValue);
        if (progress < 1) {
          window.requestAnimationFrame(step);
        }
      };
      window.requestAnimationFrame(step);
    };

    if (isFirstRender) {
      animateValue(currentValue, value, 200);
      setIsFirstRender(false);
    } else {
      animateValue(currentValue, value, 200);
    }
  }, [value, isFirstRender, currentValue, isVisible]);

  if (!isVisible) return null;

  return <span ref={counterRef}>{currentValue}</span>;
};

export default function HomePage() {
  const [isVisible, setIsVisible] = useState(false);
  const [isTooltipVisible, setIsTooltipVisible] = useState(false);
  const [totalRecs, setTotalRecs] = useState(0);
  const [isCountVisible, setIsCountVisible] = useState(false);
  const [isTextGenComplete, setIsTextGenComplete] = useState(false);
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);

  const [trackIds, setTrackIds] = useState([
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
  ]);

  function handleMouseMove({ currentTarget, clientX, clientY }) {
    const { left, top } = currentTarget.getBoundingClientRect();
    mouseX.set(clientX - left);
    mouseY.set(clientY - top);
  }

  useEffect(() => {
    const intervalId = setInterval(() => {
      setTrackIds((prevIds) => {
        const newIds = [...prevIds];
        const lastId = newIds.pop();
        newIds.unshift(lastId);
        return newIds;
      });
    }, 2000); // Adjust this interval to match the animation duration

    return () => clearInterval(intervalId);
  }, []);

  const handleTextGenComplete = useCallback(() => {
    setIsTextGenComplete(true);
    setIsVisible(true);
    setIsCountVisible(true);
  }, []);

  useEffect(() => {
    const getTotalRecs = async () => {
      try {
        const response = await axios.get(
          `${process.env.REACT_APP_BACKEND_URL}/total-recommendations`,
          { withCredentials: true }
        );
        setTotalRecs(response.data || 0);
        console.log("Total recommendations fetched:", response.data);
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
        className="h-[60vh] w-full bg-slate-800 relative flex flex-col items-center justify-center overflow-hidden"
      >
        {/* Dot background div with enhanced mask */}
        <div className="absolute inset-0">
          <div className="w-full h-full bg-dot-white/[0.4]"></div>
          <motion.div
            className="absolute inset-0 bg-dot-thick-amber-500 opacity-100"
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
            bg-gradient-to-br from-gray-400 to-gray-200 
            bg-clip-text text-transparent 
            transition-opacity duration-1000
            ${isVisible && isTextGenComplete ? "opacity-100" : "opacity-0"}
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
                ml-2 px-2 py-0.5 bg-gray-700 text-slate-200 text-xs font-slim rounded-lg shadow-md
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
            </div>{" "}
            solo-dev project, created
            <br />
            to inspire your streamlined discovery of good music.
          </div>
        </div>
        <div
          className={`absolute right-4 top-0 bottom-0 w-[30vw] transition-all duration-1000 ease-in-out
                      ${isCountVisible ? "opacity-100" : "opacity-0"}`}
        >
          <VerticalScrollingTracks
            trackIds={trackIds}
            direction="up"
            speed="very-slow"
            pauseOnHover={true}
          />
        </div>
      </div>
      <div className="relative justify-start -translate-y-[60%] translate-x-[10%] ">
        <GlossyContainer className="">
          <div
            className={`text-5xl lato-regular text-slate-300 transition-all duration-1000 ease-in-out pb-4 
                ${isCountVisible ? "opacity-100" : "opacity-0"}
                `}
          >
            <AnimatedCounter value={totalRecs} isVisible={isCountVisible} />
          </div>
        </GlossyContainer>
      </div>
    </div>
  );
}
