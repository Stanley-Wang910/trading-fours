import React from 'react';

const Navbar = ({LogoutComponent }) => {

  const handleScrollToTop = () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  };


  return (
    <nav className="fixed top-0 left-0 right-0 bg-custom_dark bg-opacity-60 py-4 border-b border-gray-700 backdrop-filter backdrop-blur-md z-50">
      <div className="container pl-8 mr-auto px-4 flex justify-between items-center">
        <div className="flex items-center">
          <button onClick={handleScrollToTop}>
            <img src="/trading-fours.png" alt="Descriptive Alt Text" className=''/>
          </button>
            
        </div>
        <div className="flex items-center">
          {LogoutComponent}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;