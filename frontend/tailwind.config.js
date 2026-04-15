/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        shell: "#F4F2EB",
        ink: "#1A2433",
        accent: "#0F766E",
        coral: "#E76F51",
        sky: "#2D6CDF",
        pine: "#2F855A",
        sand: "#EED9B4"
      },
      boxShadow: {
        panel: "0 18px 45px rgba(26, 36, 51, 0.12)"
      },
      backgroundImage: {
        dots:
          "radial-gradient(circle at 1px 1px, rgba(15, 118, 110, 0.15) 1px, transparent 0)"
      }
    }
  },
  plugins: []
};
