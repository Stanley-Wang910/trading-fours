import React from 'react';

function GradientBackground({ className }) {
  return (
    <>
    <div className="gradient-background fixed top-[55%] left-[105%] lg:top-[55%] lg:left-[95%] w-full h-full flex justify-start items-center">
      <svg className="blur-[100px] " width="585" height="475" viewBox="0 0 585 475" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path className="animate-colorChange2" d="M59.6878 70.4072C2.64247 112.7 -16.8108 220.14 15.7866 303.15C34.714 338.439 85.6079 417.473 137.764 451.308C202.958 493.601 346.492 482.305 380.666 392.728C414.841 303.151 608.848 251.138 582.56 142.122C556.271 33.1053 429.562 31.2664 323.621 6.83623C217.68 -17.5939 116.733 28.1141 59.6878 70.4072Z" fill="#B071FF"/>
      </svg>
    </div>
    {/* <div className="gradient-background fixed top-[55%] right-[75%] lg:top-[0%] lg:right-[0%] w-full h-full flex justify-start items-center">
      <svg className="blur-[100px] scale-x-[-1] " width="585" height="475" viewBox="0 0 585 475" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path className="animate-colorChange1" d="M59.6878 70.4072C2.64247 112.7 -16.8108 220.14 15.7866 303.15C34.714 338.439 85.6079 417.473 137.764 451.308C202.958 493.601 346.492 482.305 380.666 392.728C414.841 303.151 608.848 251.138 582.56 142.122C556.271 33.1053 429.562 31.2664 323.621 6.83623C217.68 -17.5939 116.733 28.1141 59.6878 70.4072Z" fill="#B071FF"/>
      </svg>
    </div> */}

    <div className={`gradient-background absolute top-[-10%] left-[9%] lg:top-[-12%] lg:left-[9%] w-full h-full flex justify-start items-center ${className}`}>      
      <svg className="blur-[75px] " width="700" height="700" viewBox="0 0 500 500" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle className="animate-colorChange1" cx="150" cy="150" r="125" fill="#B071FF"/>
      </svg>
    </div>
  </>
  );
};

export default GradientBackground;