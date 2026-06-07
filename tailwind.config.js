/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./layouts/**/*.html",
    "./content/**/*.md",
    "./themes/**/*.html"
  ],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        serif: ['ui-serif', 'Georgia', 'Cambria', '"Times New Roman"', '"Noto Serif"', 'serif'],
        sans: ['ui-sans-serif', 'system-ui', '-apple-system', '"Segoe UI"', 'Roboto', '"Helvetica Neue"', 'Arial', '"Noto Sans"', 'sans-serif'],
        mono: ['ui-monospace', 'SFMono-Regular', '"JetBrains Mono"', 'Menlo', 'Consolas', 'monospace'],
      },
      maxWidth: {
        reading: '68ch',
      },
      boxShadow: {
        soft: '0 1px 0 rgba(28, 25, 23, 0.04), 0 8px 24px -12px rgba(28, 25, 23, 0.08)',
      },
    },
  },
  plugins: [],
}
