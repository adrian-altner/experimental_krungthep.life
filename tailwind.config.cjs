module.exports = {
  content: [
    "./core/templates/**/*.html",
    "./home/templates/**/*.html",
    "./blog/templates/**/*.html",
    "./search/templates/**/*.html",
    "./frontend/src/**/*.js",
  ],
  theme: {
    extend: {},
  },
  plugins: [require("@tailwindcss/typography")],
};
