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
      className="absolute top-4 right-4 px-4 py-2 bg-blue-700 text-gray-200 rounded-full hover:bg-blue-600 transition-colors duration-300"
      onClick={handleLogout}>
      Logout
    </button>
  );
}

export default Logout;
