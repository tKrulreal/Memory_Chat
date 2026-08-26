import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
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
        warning: "var(--accent-warning)",
        "ai-card": "var(--accent-ai)",
        online: "var(--online)",
        
        // Shadcn UI Variables
        background: "var(--bg-app)",
        foreground: "var(--text-primary)",
        card: {
          DEFAULT: "var(--bg-surface)",
          foreground: "var(--text-primary)",
        },
        popover: {
          DEFAULT: "var(--popover)",
          foreground: "var(--popover-foreground)",
        },
        primary: {
          DEFAULT: "var(--primary)",
          foreground: "var(--primary-foreground)",
        },
        secondary: {
          DEFAULT: "var(--bg-elevated)",
          foreground: "var(--text-secondary)",
        },
        muted: {
          DEFAULT: "var(--bg-elevated)",
          foreground: "var(--text-secondary)",
        },
        accent: {
          DEFAULT: "var(--accent-primary)",
          hover: "var(--accent-primary-hover)",
          foreground: "var(--primary-foreground)",
        },
        destructive: {
          DEFAULT: "var(--destructive)",
          foreground: "var(--primary-foreground)",
        },
        border: "var(--border-subtle)",
        ring: "var(--accent-primary)",
        chart: {
          "1": "var(--chart-1)",
          "2": "var(--chart-2)",
          "3": "var(--chart-3)",
          "4": "var(--chart-4)",
          "5": "var(--chart-5)",
        },
      },
      borderRadius: {
        bubble: "var(--radius-bubble)",
        button: "var(--radius-button)",
        composer: "var(--radius-composer)",
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
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
