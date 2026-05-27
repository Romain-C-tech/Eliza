/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx,vue}",
  ],
  theme: {
    extend: {
      colors: {
        forge: {
          black: "#0F0F0F",
          coal: "#1A1A1A",
          steel: "#2B2B2B",
          fire: "#FF6A00",
          ember: "#FF8C42",
          spark: "#FFC857",
          ash: "#F5F5F5"
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        title: ['Orbitron', 'sans-serif'],
      }
    },
  },
  plugins: [],
}

