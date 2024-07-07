import React, { useState, useEffect } from "react";
import { TextGenerateEffect } from "./ui/text-generate-effect.tsx";
import { motion } from "framer-motion";
import "../styles/Components/HomePage.css";

export default function HomePage() {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(true);
    }, 3500); // 5000ms delay

    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="w-full flex flex-col items-center justify-center h-[60vh] bg-gray-900">
      <div className="w-full justify-start translate-y-[20%] translate-x-[10%] py-20 montserrat-reg text-3xl">
        <TextGenerateEffect
          words={"Built, by design,\nFor the way\nYou listen."}
          highlightText="Built, For You"
        />
        <div
          className={`
            text-sm mt-4 
            bg-gradient-to-br from-gray-400 to-gray-200 
            bg-clip-text text-transparent 
            transition-opacity duration-1000
            ${isVisible ? "opacity-100" : "opacity-0"}
          `}
        >
          An{" "}
          <a
            href="https://github.com/Stanley-Wang910/spotify-rec-engine"
            target="_blank"
            rel="noopener noreferrer"
            className="hover-effect-link"
            data-replace="open-source"
          >
            <span>open-source</span>
          </a>{" "}
          solo-dev project, created
          <br />
          to inspire your streamlined discovery of good music.
        </div>
      </div>
    </div>
  );
}
