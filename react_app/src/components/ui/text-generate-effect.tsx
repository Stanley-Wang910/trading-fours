import React, { useEffect, useCallback } from "react";
import { motion, stagger, useAnimate } from "framer-motion";
import { cn } from "../../utils/cn.ts";

const TextGenerateEffect = ({
  words,
  isVisible = true,
  className,
  highlightColor = "bg-gradient-to-r from-custom-brown to-amber-400 bg-clip-text text-transparent font-semibold",
  highlightText = "",
  delay = 500, // Add a delay prop with default value
  gradient = 'bg-gradient-to-br from-gray-200 to-gray-400',
  onComplete,
}: {
  words: string;
  isVisible?: boolean;
  className?: string;
  highlightColor?: string;
  highlightText?: string;
  delay?: number; // Define the delay prop type
  gradient?: string;
  onComplete?: () => void; // Add this new prop type
}) => {
  const [scope, animate] = useAnimate();
  const linesArray = words.split("\n");
  const wordsArray = linesArray.map(line => line.split(" "));

    const animateText = useCallback(async () => {
      if (isVisible && scope.current) {
        for (let i = 0; i < wordsArray.length; i++) {
          await animate(
            `div[data-line="${i}"] span`,
            { opacity: 1 },
            { duration: 0.75, delay: stagger(0.075) }
          );
        }
        if (onComplete) {
          onComplete();
        }
      }
    }, [animate, wordsArray, onComplete, isVisible]);
  
    useEffect(() => {
      const timeoutId = setTimeout(animateText, delay); // Add delay before starting the animation
      return () => clearTimeout(timeoutId); // Cleanup the timeout if the component unmounts
    }, [animate, wordsArray, delay, isVisible]);
    
    

  const renderWords = (line: string[], lineIdx: number) => {
    return (
      <motion.div key={`line-${lineIdx}`} data-line={lineIdx} className="flex flex-wrap">
        {line.map((word, idx) => {
          const isHighlighted = highlightText.toLowerCase().includes(word.toLowerCase());
          return (
            <motion.span
              key={word + idx}
              className={cn(
                `opacity-0 ${gradient} bg-clip-text text-transparent`,
                isHighlighted && highlightColor
              )}
            >
              {word}
              <span className="invisible">&nbsp;</span>
            </motion.span>
          );
        })}
      </motion.div>
    );
  };

  return (
    <div className={cn("", className)} ref={scope}>
      <div className="">
        {wordsArray.map((line, idx) => renderWords(line, idx))}
      </div>
    </div>
  );
};

export default React.memo(TextGenerateEffect);
