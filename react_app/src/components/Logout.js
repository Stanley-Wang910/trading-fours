import React from "react";

function Logout({ setToken, setRecommendations }) {
  const handleLogout = async () => {
    try {
      await fetch("/auth/logout");
      setToken("");
      setRecommendations([]);
    } catch (error) {
      console.error("Error logging out", error);
    }
  };

  return (
    <button
      className="logout absolute top-4 right-2 px-4 py-2 font-bold text-[14px] text-gray-400"
      onClick={handleLogout}>
      Logout  
    </button>
  );
}

export default Logout;
