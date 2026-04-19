export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: { DEFAULT: '#1e293b', dark: '#0f172a', light: '#334155' },
        accent:  { DEFAULT: '#c2410c', dark: '#9a3412', light: '#ea580c' },
        ink:     { DEFAULT: '#1a1a2e', muted: '#64748b', subtle: '#94a3b8' },
        surface: { DEFAULT: '#fafafa', alt: '#f1f5f9', border: '#e2e8f0' },
        danger:  '#dc2626'
      },
      fontFamily: {
        sans: ['Inter','system-ui','sans-serif'],
        serif: ['"Source Serif Pro"','Georgia','serif']
      }
    }
  }
};
