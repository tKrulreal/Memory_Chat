import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        app: "var(--bg-app)",
        surface: "var(--bg-surface)",
        elevated: "var(--bg-elevated)",
        input: "var(--bg-input)",
        accent: {
          DEFAULT: "var(--accent-primary)",
          hover: "var(--accent-primary-hover)",
        },
        warning: "var(--accent-warning)",
        "ai-card": "var(--accent-ai)",
        primary: "var(--text-primary)",
        secondary: "var(--text-secondary)",
        subtle: "var(--border-subtle)",
        online: "var(--online)",
      },
      borderRadius: {
        bubble: "var(--radius-bubble)",
        button: "var(--radius-button)",
        composer: "var(--radius-composer)",
      },
      fontFamily: {
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
      },
      width: {
        nav: "var(--width-nav)",
        "chat-list": "var(--width-chat-list)",
        "info-panel": "var(--width-info-panel)",
      },
    },
  },
  plugins: [],
};

export default config;
