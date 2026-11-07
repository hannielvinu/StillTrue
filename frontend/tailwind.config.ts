export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: { paper: "var(--bg)", ink: "var(--ink)", brand: "var(--brand)" },
    },
  },
  plugins: [],
};
