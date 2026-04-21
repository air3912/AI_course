/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{vue,js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#f1f6ff",
          100: "#dceaff",
          200: "#b9d3ff",
          300: "#84b1ff",
          400: "#4d87ff",
          500: "#2a62f0",
          600: "#1f4dca",
          700: "#1b3ea4",
          800: "#1a357f",
          900: "#182f66"
        }
      }
    },
  },
  plugins: [],
};
