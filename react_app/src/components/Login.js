import React from "react";

function Login() {
  const backendURL = process.env.REACT_APP_BACKEND_URL
  return (
    <div className="App">
      <div className="App-header flex justify-center items-center min-h-screen">
        <a
          className="btn-spotify px-8 py-4 bg-green-500 text-white font-bold rounded-full shadow-lg hover:bg-green-600 transition-colors duration-300"
          href={`${backendURL}/auth/login`}
        >
          Login with Spotify
        </a>
      </div>
    </div>
  );
}

export default Login;