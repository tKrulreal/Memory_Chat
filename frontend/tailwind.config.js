/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        messenger: {
          blue: '#0084FF',
          'blue-hover': '#0077E6',
          purple: '#A855F7',
          'dark-bg': '#1A1A2E',
          'dark-sidebar': '#0F0F23',
          'dark-card': '#242526',
          'dark-surface': '#3A3B3C',
        },
        background: 'var(--background)',
        foreground: 'var(--foreground)',
        card: {
          DEFAULT: 'var(--card)',
          foreground: 'var(--card-foreground)'
        },
        popover: {
          DEFAULT: 'var(--popover)',
          foreground: 'var(--popover-foreground)'
        },
        primary: {
          DEFAULT: 'var(--primary)',
          foreground: 'var(--primary-foreground)'
        },
        secondary: {
          DEFAULT: 'var(--secondary)',
          foreground: 'var(--secondary-foreground)'
        },
        muted: {
          DEFAULT: 'var(--muted)',
          foreground: 'var(--muted-foreground)'
        },
        accent: {
          DEFAULT: 'var(--accent)',
          foreground: 'var(--accent-foreground)'
        },
        destructive: {
          DEFAULT: 'var(--destructive)',
          foreground: 'var(--destructive-foreground)'
        },
        border: 'var(--border)',
        input: 'var(--input)',
        ring: 'var(--ring)',
        bubble: {
          sent: 'var(--bubble-sent)',
          'sent-text': 'var(--bubble-sent-text)',
          received: 'var(--bubble-received)',
          'received-text': 'var(--bubble-received-text)',
        },
        sidebar: {
          bg: 'var(--sidebar-bg)',
          border: 'var(--sidebar-border)',
          icon: 'var(--sidebar-icon)',
          'icon-active': 'var(--sidebar-icon-active)',
        },
        conversation: {
          hover: 'var(--conversation-hover)',
          active: 'var(--conversation-active)',
        },
        online: 'var(--online-green)',
        'unread-badge': 'var(--unread-badge)',
        'chat-input': 'var(--chat-input-bg)',
        'text-primary': 'var(--text-primary)',
        'text-secondary': 'var(--text-secondary)',
        'text-tertiary': 'var(--text-tertiary)',
        divider: 'var(--divider)',
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
        bubble: '18px',
      },
      boxShadow: {
        'messenger': '0 2px 8px rgba(0, 0, 0, 0.1)',
        'messenger-lg': '0 8px 32px rgba(0, 0, 0, 0.12)',
        'glow-blue': '0 0 20px rgba(0, 132, 255, 0.3)',
      },
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'Roboto', '"Helvetica Neue"', 'Arial', 'sans-serif'],
      },
    }
  },
  plugins: [],
}
