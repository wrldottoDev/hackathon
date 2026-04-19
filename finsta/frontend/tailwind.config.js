/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        finsta: {
          bg: "#0a0a0a",
          card: "#1a1a1a",
          border: "#2a2a2a",
          accent: "#e1306c",
          "accent-light": "#f77737",
          blue: "#405de6",
          purple: "#833ab4",
          text: "#fafafa",
          muted: "#8e8e8e",
        },
      },
      fontFamily: {
        sans: ["-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "Helvetica", "Arial", "sans-serif"],
      },
    },
  },
  plugins: [],
};
