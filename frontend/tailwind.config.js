// tailwind.config.js
module.exports = {
  darkMode: 'class', // ✅ Enable dark mode via class strategy
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [require('tailwind-scrollbar-hide')],
};
