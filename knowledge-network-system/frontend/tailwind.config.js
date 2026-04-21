/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{vue,js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#eef4ff",
          100: "#d9e7ff",
          200: "#b8d0ff",
          300: "#8fb2ff",
          400: "#5b88ff",
          500: "#2f63f0",
          600: "#234ec9",
          700: "#1e3f9f",
          800: "#1d367f",
          900: "#1c315f"
        }
      }
    },
  },
  plugins: [],
};
