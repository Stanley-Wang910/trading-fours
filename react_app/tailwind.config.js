/** @type {import('tailwindcss').Config} */
module.exports = {
  mode: "jit",
  purge: ["./src/**/*.{js,jsx,ts,tsx}", "./public/index.html"],
  darkMode: false, // or 'media' or 'class'
  theme: {
    extend: {
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
      },
      animation: {
        fadeIn: "fadeIn 1s ease-in-out forwards",
      },

      colors: {
        'custom_dark': '#1C2128',
        'custom-blue': '#007bff',
        'custom-purple': '#6f42c1',
      },
      backgroundImage: {
        'custom-gradient': 'linear-gradient(to right, var(--custom-blue), var(--custom-purple))',
      },
    },
  },
  variants: {
    extend: {},
  },
  plugins: [],
};
