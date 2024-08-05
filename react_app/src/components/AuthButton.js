import React from "react";

function AuthButton({ token, setToken, setRecommendations }) {
  const handleLogout = async () => {
    console.log("Logout button clicked");
    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/auth/logout`,
        {
          method: "GET",
          credentials: "include",
        }
      );

      console.log("Response received:", response);
      if (response.ok) {
        const data = await response.json();
        console.log("Logout successful:", data);
        setToken("");
        setRecommendations([]);
      } else {
        console.error("Logout failed:", response.statusText);
      }
    } catch (error) {
      console.error("Error logging out:", error);
    }
  };

  return (
    <button
      className="authButton absolute top-4 right-2 px-1 py-[4px] font-bold text-[14px] text-gray-400"
      onClick={
        token
          ? handleLogout
          : () =>
              (window.location.href = `${process.env.REACT_APP_BACKEND_URL}/auth/login`)
      }
    >
      {token ? "Logout" : "Login"}
    </button>
  );
}

export default React.memo(AuthButton);
