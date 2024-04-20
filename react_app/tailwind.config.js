const defaultTheme = require("tailwindcss/defaultTheme");
const colors = require("tailwindcss/colors");
const { default: flattenColorPalette } = require("tailwindcss/lib/util/flattenColorPalette");
/** @type {import('tailwindcss').Config} */

module.exports = {
  mode: "jit",
  purge: ["./src/**/*.{js,jsx,ts,tsx}", "./public/index.html"],

  darkMode: false, // or 'media' or 'class'
  theme: {
    extend: {
      keyframes: {
        meteor: {
          "0%": { transform: "rotate(215deg) translateX(0)", opacity: "1" },
          "70%": { opacity: "1" },
          "100%": {
            transform: "rotate(215deg) translateX(-500px)",
            opacity: "0",
          },
        },
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
      },
      animation: {
        "meteor-effect": "meteor 5s linear infinite",
        fadeIn: "fadeIn 1s ease-in-out forwards",
      },

      colors: {
        'custom_dark': '#1C2128',
        'custom-blue-grad': '#000732',
        'custom-blue': '#010D3D',
        'custom-purple': '#6f42c1',
        'custom-green': '#1ED760',
        'custom-brown': '#cc8e15',
      },
      backgroundImage: {
        'custom-gradient': 'linear-gradient(to right, var(--custom-blue), var(--custom-purple))',
      },
    },
  },
  variants: {
    extend: {},
  },
  plugins: [addVariablesForColors]
};

function addVariablesForColors({ addBase, theme }) {
  let allColors = flattenColorPalette(theme("colors"));
  let newVars = Object.fromEntries(
    Object.entries(allColors).map(([key, val]) => [`--${key}`, val])
  );
  addBase({
    ":root": newVars,
  });
}