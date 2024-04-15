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
      className="absolute top-4 right-2 px-4 py-2 font-semibold text-xs bg-custom-brown shadow-xl rounded-full hover:bg-yellow-700 duration-300"
      onClick={handleLogout}>
      Logout
    </button>
  );
}

export default Logout;
