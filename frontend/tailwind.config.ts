import type { Config } from "tailwindcss";

/**
 * Design tokens for the app.
 *
 * `brand` is the primary indigo family (trustworthy, modern).
 * `accent` is the warm coral/orange family (friendly, energetic).
 * Together they give the UI a soft "sunrise" feel without relying on jargon.
 */
const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#eef2ff",
          100: "#e0e7ff",
          200: "#c7d2fe",
          300: "#a5b4fc",
          400: "#818cf8",
          500: "#6366f1",
          600: "#4f46e5",
          700: "#4338ca",
          800: "#3730a3",
          900: "#312e81",
          950: "#1e1b4b",
        },
        accent: {
          50: "#fff7ed",
          100: "#ffedd5",
          200: "#fed7aa",
          300: "#fdba74",
          400: "#fb923c",
          500: "#f97316",
          600: "#ea580c",
          700: "#c2410c",
          800: "#9a3412",
          900: "#7c2d12",
        },
      },
      fontFamily: {
        sans: [
          "-apple-system",
          "BlinkMacSystemFont",
          "Segoe UI",
          "Roboto",
          "Helvetica Neue",
          "Arial",
          "sans-serif",
        ],
      },
      boxShadow: {
        card: "0 1px 2px 0 rgb(15 23 42 / 0.04), 0 10px 30px -14px rgb(15 23 42 / 0.14)",
        "card-hover": "0 24px 48px -16px rgb(79 70 229 / 0.20)",
        glow: "0 12px 40px -10px rgb(79 70 229 / 0.45)",
        soft: "0 2px 10px -2px rgb(15 23 42 / 0.08)",
      },
      maxWidth: {
        content: "72rem",
      },
    },
  },
  plugins: [],
};

export default config;
