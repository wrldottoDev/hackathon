/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        sc: {
          bg: "#050a14",
          card: "#0c1524",
          "card-hover": "#111d32",
          border: "#1a2744",
          accent: "#00d4aa",
          "accent-dim": "#00a88a",
          danger: "#ff3b5c",
          "danger-dim": "#cc2e49",
          warn: "#ffb020",
          blue: "#3b82f6",
          text: "#e8edf5",
          muted: "#6b7a94",
          surface: "#0f1a2e",
        },
      },
      fontFamily: {
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "monospace"],
      },
      boxShadow: {
        glow: "0 0 20px rgba(0, 212, 170, 0.15)",
        "glow-danger": "0 0 20px rgba(255, 59, 92, 0.2)",
        "glow-warn": "0 0 20px rgba(255, 176, 32, 0.15)",
      },
    },
  },
  plugins: [],
};
