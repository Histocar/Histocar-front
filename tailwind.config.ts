import { type Config } from "tailwindcss";
import { fontFamily } from "tailwindcss/defaultTheme";

export default {
  content: ["./src/**/*.tsx"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["var(--font-geist-sans)", ...fontFamily.sans],
      },
      colors: {
        primary: {
          DEFAULT: "#3B82F6", // blue-500
          hover: "#2563EB", // blue-600
        },
        dark: {
          DEFAULT: "#000000", // pure black
          lighter: "#121212", // very dark gray
          card: "#1A1A1A", // slightly lighter black for cards
        },
        light: {
          DEFAULT: "#FFFFFF", // pure white for text
          muted: "#A0AEC0", // lighter gray for secondary text
        },
      },
    },
  },
  plugins: [],
} satisfies Config;
