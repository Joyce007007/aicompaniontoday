import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';
import sitemap from '@astrojs/sitemap';
import mdx from '@astrojs/mdx';

export default defineConfig({
  site: 'https://aicompaniontoday.com',
  output: 'static',
  integrations: [tailwind(), sitemap(), mdx()],
  vite: { define: { 'import.meta.env.GHOST_URL': JSON.stringify(process.env.GHOST_URL), 'import.meta.env.GA4_ID': JSON.stringify(process.env.GA4_ID || ''),
      'import.meta.env.GSC_VERIFY': JSON.stringify(process.env.GSC_VERIFY || ''),
      'import.meta.env.GHOST_CONTENT_KEY': JSON.stringify(process.env.GHOST_CONTENT_KEY) }}
});
