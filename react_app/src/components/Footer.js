import React, { useCallback, useState } from "react";
import { motion } from "framer-motion";

const Footer = () => {
  const [isHovered, setIsHovered] = useState(false);

  const handleScrollToTop = useCallback(() => {
    window.scrollTo({ top: 0, behavior: "smooth" });
    window.open(
      "https://posidovega.com/jazz-lingo#:~:text=of%20the%20tune.-,Trading%204s,-(or%208s%2C%202s",
      "_blank"
    );
  }, []);

  const handleMouseEnter = useCallback(() => {
    setIsHovered(true);
  }, []);

  const handleMouseLeave = useCallback(() => {
    setIsHovered(false);
  }, []);

  return (
    <>
      <footer
        id="footer"
        className="mt-[0vh] z-[50] w-full h-[240px] flex flex-row justify-between items-center px-[2vw] py-20 relative text-gray-400 "
      >
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-black z-[-7]"></div>
        <div className="col col1 flex flex-col items-start justify-start p-4 w-[28%]">
          <div className="relative translate-y-14 flex items-center before:content-[''] before:absolute before:top-[-50px] before:left-[-5px] before:w-[40px] before:h-[2px] before:bg-gray-400">
            <button
              onClick={handleScrollToTop}
              className="svg-short mb-2  justify items-col over"
              onMouseEnter={handleMouseEnter}
              onMouseLeave={handleMouseLeave}
            >
              <svg
                className="absolute top-0"
                width="11"
                height="21"
                viewBox="0 0 10 18"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M5.112 17.216C4.104 17.216 3.36 16.984 2.88 16.52C2.4 16.056 2.16 15.32 2.16 14.312V5.504H0.6V4.256C0.728 4.208 0.96 4.128 1.296 4.016C1.632 3.888 1.888 3.784 2.064 3.704C2.336 3.496 2.568 3.136 2.76 2.624C2.904 2.288 3.168 1.456 3.552 0.128H5.472L5.568 3.656H9.24V5.504H5.592V12.248C5.592 13.144 5.616 13.776 5.664 14.144C5.712 14.512 5.816 14.752 5.976 14.864C6.136 14.96 6.416 15.008 6.816 15.008C7.216 15.008 7.632 14.968 8.064 14.888C8.496 14.792 8.856 14.68 9.144 14.552L9.6 15.896C9.152 16.232 8.496 16.536 7.632 16.808C6.768 17.08 5.928 17.216 5.112 17.216Z"
                  fill="#CC8E15"
                />
              </svg>

              <div className="ml-0.5">
                <svg
                  className="svg-container absolute left-[13px] top-[1px]"
                  width="17"
                  height="21"
                  viewBox="0 0 11 14"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    d="M3.39152 0.229941L3.39192 0.229786C3.47272 0.19789 3.52867 0.1862 3.56112 0.181972C3.57736 0.179855 3.58784 0.17959 3.59275 0.179626C3.59364 0.179633 3.59435 0.179649 3.59488 0.179667L3.6016 0.180667L3.612 0.180476L6.42933 0.128815C6.39474 0.192859 6.34952 0.274281 6.29203 0.373744C6.12236 0.667335 5.84588 1.118 5.42034 1.74275C4.56921 2.9923 3.12216 4.93765 0.74138 7.71473L0.564471 7.92109H0.83628H4.94933H5.06708L5.07411 7.80356L5.13768 6.74154L5.1379 6.74156V6.73408L5.01291 6.73408H5.0129C5.1379 6.73408 5.1379 6.73399 5.1379 6.73391L5.1379 6.73374L5.1379 6.73337L5.13789 6.73254L5.13786 6.73052L5.13768 6.72508C5.1375 6.72084 5.13717 6.71539 5.13659 6.70881C5.13542 6.69563 5.13323 6.67792 5.12912 6.65631C5.12089 6.61307 5.10502 6.55434 5.07448 6.48551C5.02273 6.36888 4.93018 6.22625 4.76639 6.08206L7.44548 2.72286L7.52479 7.79804L7.52672 7.92109H7.64978H8.875V8.28156H7.62859H7.50359V8.40656V10.0336H7.50328L7.5039 10.0425L7.62859 10.0336C7.5039 10.0425 7.50391 10.0425 7.50391 10.0426L7.50392 10.0428L7.50395 10.0432L7.50405 10.0444L7.50435 10.048L7.50556 10.0603C7.50667 10.0707 7.50842 10.0852 7.5111 10.1033C7.51646 10.1393 7.52557 10.1899 7.54077 10.2498C7.57104 10.3691 7.62623 10.5287 7.72641 10.6858C7.82703 10.8435 7.9738 10.9998 8.1861 11.1081C8.36971 11.2018 8.59653 11.2566 8.875 11.2505V11.8504L3.84654 11.8744V11.4221C3.8826 11.4133 3.92676 11.4017 3.97677 11.3869C4.11338 11.3465 4.29628 11.2814 4.47749 11.1827C4.83446 10.9883 5.2189 10.6418 5.16733 10.0732V9.45028L5.16787 9.44137C5.16832 9.43261 5.16877 9.4204 5.16891 9.40522C5.16918 9.3749 5.16819 9.33244 5.16329 9.28175C5.15356 9.181 5.12807 9.04421 5.06367 8.90496C4.99885 8.76478 4.89419 8.62148 4.72742 8.51227C4.56064 8.40305 4.3396 8.33307 4.05024 8.32699L4.05025 8.3269L4.04548 8.32698L0.150061 8.39376C0.143966 8.37804 0.138013 8.35954 0.133441 8.33881C0.118186 8.26963 0.117516 8.17394 0.18357 8.06575C0.311872 7.85658 0.469284 7.62089 0.644384 7.3587C1.60935 5.91384 3.11148 3.66466 3.23882 0.619001L3.24027 0.607733C3.24167 0.597388 3.24391 0.582173 3.24717 0.563549C3.25372 0.526007 3.26414 0.476056 3.27957 0.424853C3.29523 0.37285 3.31466 0.324329 3.33746 0.287043C3.36112 0.248355 3.38077 0.234144 3.39152 0.229941ZM0.177224 8.44864C0.177309 8.44877 0.17725 8.44868 0.17706 8.4484L0.177224 8.44864Z"
                    fill="#FFFFFF"
                    stroke="#FFFFFF"
                    strokeWidth="0.25"
                    strokeMiterlimit="10"
                  />
                </svg>
              </div>

              {isHovered && (
                <motion.div className="absolute bottom-[35px] left-0 right-0 h-[1px]">
                  <svg width="33" height="7" viewBox="0 0 33 7" fill="none">
                    <motion.path
                      d="M1 5.39971C7.48565 -1.08593 6.44837 -0.12827 8.33643 6.47992C8.34809 6.52075 11.6019 2.72875 12.3422 2.33912C13.8991 1.5197 16.6594 2.96924 18.3734 2.96924C21.665 2.96924 23.1972 1.69759 26.745 2.78921C29.7551 3.71539 32.6954 3.7794 35.8368 3.7794"
                      stroke="#CC8E15"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      initial={{
                        strokeDasharray: 84.20591735839844,
                        strokeDashoffset: 84.20591735839844,
                      }}
                      animate={{
                        strokeDashoffset: 0,
                      }}
                      transition={{
                        duration: 0.75,
                      }}
                    />
                  </svg>
                </motion.div>
              )}
            </button>
            <p className="relative mt-10 left-[-3px]">Made by Stanley Wang</p>
          </div>
          <p className="transform translate-y-[60px] text-[#818181] text-xs">
            2024 © All Rights Reserved
          </p>
        </div>

        <div className="flex flex-col text-right relative translate-y-10">
          <a
            href="https://github.com/Stanley-Wang910"
            target="_blank"
            rel="noopener noreferrer"
            className=" relative inline-block text-gray-400 hover:text-custom-brown transition-all duration-300 hover:translate-x-[-5px] "
          >
            GitHub |
          </a>
          <a
            href="https://www.linkedin.com/in/stanley910/"
            target="_blank"
            rel="noopener noreferrer"
            className=" relative inline-block text-gray-400 hover:text-custom-brown transition-all duration-300 hover:translate-x-[-5px] "
          >
            LinkedIn |
          </a>
          <a
            href="https://www.youtube.com/channel/UCtDa8TWqWz3aymp3tJ8F8uw"
            target="_blank"
            rel="noopener noreferrer"
            className=" relative inline-block text-gray-400 hover:text-custom-brown transition-all duration-300 hover:translate-x-[-5px] "
          >
            YouTube |
          </a>
        </div>
        <div className="backdrop absolute inset-0 z-[-5] backdrop-blur-[40px] bg-gradient-b from-transparent via-black to-black"></div>
      </footer>
    </>
  );
};

export default Footer;
