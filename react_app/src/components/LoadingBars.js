// LoadingBars.js

import React from "react";

const LoadingBars = ({ className }) => {
  return (
    <div className={`loader justify-center text-center  ${className}`}>
      <div className="bar1"></div>
      <div className="bar2"></div>
      <div className="bar3"></div>
      <div className="bar4"></div>
      <div className="bar5"></div>
      <div className="bar6"></div>
    </div>
  );
};

export default LoadingBars;
