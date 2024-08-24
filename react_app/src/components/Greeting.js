import React, { useState, useEffect } from "react";
import axios from "axios";
import "../styles/Components/Greeting.css";

function Greeting({ lyds = false }) {
  const [user, setUser] = useState(null);
  const [greeting, setGreetings] = useState("");
  const [displayName, setDisplayName] = useState("");
  console.log(lyds);

  const words = [
    "song",
    "genre",
    "vibe",
    "melody",
    "rhythm",
    "tune",
    "beat",
    "mood",
    "groove",
    "jam",
    "track",
    "anthem",
    "ballad",
    "lyrics",
    "solo",
    "chorus",
    "verse",
    "bridge",
    "hook",
    "refrain",
    "playlist",
    "album",
    "EP",
    "mixtape",
  ];
  const [lastWord, setLastWord] = useState("song");
  const [isHovering, setIsHovering] = useState(false);

  useEffect(() => {
    const shuffleWords = () => {
      const shuffledWords = [...words];
      for (let i = shuffledWords.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [shuffledWords[i], shuffledWords[j]] = [
          shuffledWords[j],
          shuffledWords[i],
        ];
      }
      return shuffledWords;
    };

    const animateWords = (shuffledWords) => {
      let currentIndex = 0;
      const interval = setInterval(() => {
        setLastWord(shuffledWords[currentIndex]);
        currentIndex = (currentIndex + 1) % shuffledWords.length;
        if (currentIndex === 0) {
          clearInterval(interval);
        }
      }, 70);
    };

    const shuffledWords = shuffleWords();
    animateWords(shuffledWords);

    const randomIndex = Math.floor(Math.random() * words.length);
    setLastWord(words[randomIndex]);
  }, []);

  // useEffect(() => {
  //     let interval;
  //     if (isHovering) {
  //         let currentIndex = 0;
  //         interval = setInterval(() => {
  //         setLastWord(words[currentIndex]);
  //         currentIndex = (currentIndex + 1) % words.length;
  //         }, 100);
  //     }

  //     return () => {
  //         clearInterval(interval);
  //     };
  // }, [isHovering]);

  // const handleMouseEnter = () => {
  //     setIsHovering(true);
  // };

  // const handleMouseLeave = () => {
  //     setIsHovering(false);
  // };

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const response = await axios.get(`/t4/user`, { withCredentials: true });
        console.log(response.data);
        setUser(response.data || []);
      } catch (error) {
        console.error("Error fetching user", error);
      }
    };

    fetchUser();
  }, []);

  useEffect(() => {
    const currentTime = new Date().getHours();
    let greetingMessage = "";
    console.log(currentTime);
    if (currentTime >= 3 && currentTime < 12) {
      greetingMessage = "Good Morning";
    } else if (currentTime >= 12 && currentTime < 18) {
      greetingMessage = "Good Afternoon";
    } else {
      greetingMessage = "Good Evening";
    }

    setGreetings(greetingMessage);
  }, []);

  useEffect(() => {
    if (user && user.display_name) {
      const name = user.display_name;
      let currentIndex = 0;

      // Delay before starting the animation
      const delayDuration = 300; // Adjust the delay duration as needed (in milliseconds)

      const timeoutId = setTimeout(() => {
        const intervalId = setInterval(() => {
          setDisplayName(name.slice(0, currentIndex + 1));
          currentIndex++;
          if (currentIndex === name.length) {
            clearInterval(intervalId);
          }
        }, 80);
      }, delayDuration);

      return () => {
        clearTimeout(timeoutId);
      };
    }
  }, [user]);

  return (
    <div className="header py-20 translate-y-[60px] translate-x-[10%] text-left">
      <h1 className="montserrat-reg text-[30px] ">
        <div className="flex flex-col items-start">
          <div className="text-gray-300 animate-slide-in opacity-0">
            {greeting},{" "}
            <span className="text-custom-brown italic font-bold">
              {lyds ? "lyds <3" : displayName}
            </span>
          </div>
          <div className="animate-slide-in-words opacity-0">
            <div className="text-[20px] font-merriweather text-stone-200 mt-2 translate-x-[40%] translate-y-1/2 overflow-hidden w-[330px]">
              <div
                className=" whitespace-nowrap"
                // onMouseEnter={handleMouseEnter}
                // onMouseLeave={handleMouseLeave}
              >
                Discover your new favorite&nbsp;
                <span className="text-yellow-500 italic relative inline-block">
                  {lastWord}
                </span>
              </div>
            </div>
          </div>
        </div>
      </h1>
    </div>
  );
}

export default React.memo(Greeting);
