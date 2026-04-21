import typography from '@tailwindcss/typography';
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#1e293b',
        accent: '#c2410c',
        'accent-dark': '#9a3412',
        ink: '#1a1a2e',
        'ink-muted': '#64748b',
        'ink-subtle': '#94a3b8',
        danger: '#dc2626',
        warning: '#c2410c',
        surface: { DEFAULT: '#ffffff', alt: '#fafafa', border: '#e2e8f0' }
      },
      fontFamily: {
        sans: ['Inter','system-ui','sans-serif'],
        serif: ['Source Serif Pro','Georgia','serif']
      }
    }
  },
  plugins: [typography],
};
