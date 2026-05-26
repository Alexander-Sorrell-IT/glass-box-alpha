import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#0a0a0f",
        panel: "#13131a",
        panelHover: "#1c1c26",
        border: "#26262f",
        accent: "#7c5cff",
        accentHover: "#9173ff",
        signal: {
          bull: "#3eea8c",
          bear: "#ff5c7c",
          neutral: "#8a8a99",
        },
        agent: {
          chronos: "#5dade2",
          devilsAdvocate: "#ff8c5a",
          web: "#a78bfa",
          mood: "#ffd966",
        },
      },
      fontFamily: {
        mono: ["ui-monospace", "SF Mono", "Menlo", "monospace"],
      },
      animation: {
        "reasoning-fade": "reasoningFade 0.4s ease-out",
        "reveal-pop": "revealPop 0.6s cubic-bezier(0.34, 1.56, 0.64, 1)",
      },
      keyframes: {
        reasoningFade: {
          "0%": { opacity: "0", transform: "translateY(4px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        revealPop: {
          "0%": { opacity: "0", transform: "scale(0.85)" },
          "70%": { opacity: "1", transform: "scale(1.05)" },
          "100%": { opacity: "1", transform: "scale(1)" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
