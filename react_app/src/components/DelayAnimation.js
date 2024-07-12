import { useEffect, useState } from "react";

const useDelayAnimation = (triggerState, delay) => {
  const [delayedState, setDelayedState] = useState(false);

  useEffect(() => {
    let timeoutId;
    if (triggerState) {
      timeoutId = setTimeout(() => {
        setDelayedState(true);
      }, delay);
    } else {
      setDelayedState(false);
    }

    return () => {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
    };
  }, [triggerState, delay]);

  return delayedState;
};

export default useDelayAnimation;
