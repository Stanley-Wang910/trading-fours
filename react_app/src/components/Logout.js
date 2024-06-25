import React from "react";
import axios from "axios";

function Logout({ setToken, setRecommendations }) {
  const handleLogout = async () => {
    try {
        const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/auth/logout`, {withCredentials: true});
        console.log("Logout response:", response);

        if (response.status === 200) {
          console.log("Logged out");
          setToken("");
          setRecommendations([]);
      } else {
        console.error("Logout failed", response);
      }
    } catch (error) {
      console.error("Error logging out", error);
    }
  };

  return (
    <button
      className="logout absolute top-4 right-2 px-1 py-[4px] font-bold text-[14px] text-gray-400"
      onClick={handleLogout}>
      Logout  
    </button>
  );
}

export default Logout;
