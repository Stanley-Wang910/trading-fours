import React from "react";

function Login() {
  return (
    <div className="App">
      <div className="App-header flex justify-center items-center min-h-screen">
        <a
          className="btn-spotify px-8 py-4 bg-green-500 text-white font-bold rounded-full shadow-lg hover:bg-green-600 transition-colors duration-300"
          href="/auth/login"
        >
          Login with Spotify
        </a>
      </div>
    </div>
  );
}

export default Login;