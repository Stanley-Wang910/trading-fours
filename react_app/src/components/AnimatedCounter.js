import React, { useEffect, useRef, useState } from "react";

const AnimatedCounter = ({
  value,
  isCountVisible,
  durationMs = 200,
  className = "",
}) => {
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
      animateValue(Math.max(0, value - 100), value, durationMs);
      setIsFirstRender(false);
      console.log("First render");
    } else {
      animateValue(currentValue, value, durationMs);
    }
  }, [value, isFirstRender, currentValue, isCountVisible]);

  if (!isCountVisible) return null;

  return (
    <span className={`${className}`} ref={counterRef}>
      {currentValue.toLocaleString()}
    </span>
  );
};

export default React.memo(AnimatedCounter);
