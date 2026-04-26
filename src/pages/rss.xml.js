// RSS feed dynamique - liste les pages principales + nouveaux articles
// Endpoint: /rss.xml

const SITE_URL = 'https://aicompaniontoday.com';
const TITLE = 'AI Companion Today';
const DESCRIPTION = 'Independent editorial publication reviewing AI companion apps across 8 verticals: companion, mental health, seniors, language, productivity, romance, gaming, education.';

const ITEMS = [
  // Best-of (top tier)
  { title: 'Best AI Companion Apps 2026', url: '/best-ai-companion-apps-2026/', category: 'companion', pub: '2026-04-19' },
  { title: 'Best AI Mental Health Apps 2026', url: '/best-ai-mental-health-2026/', category: 'mental-health', pub: '2026-04-19' },
  { title: 'Best AI Companion Apps for Seniors 2026', url: '/best-ai-companion-seniors-2026/', category: 'seniors', pub: '2026-04-19' },
  { title: 'Best AI Language Tutor Apps 2026', url: '/best-ai-language-tutor-2026/', category: 'language', pub: '2026-04-19' },
  { title: 'Best AI Writing Assistant 2026', url: '/best-ai-writing-assistant-2026/', category: 'productivity', pub: '2026-04-19' },
  { title: 'Best AI Boyfriend Apps 2026', url: '/best-ai-boyfriend-apps-2026/', category: 'romance', pub: '2026-04-20' },
  { title: 'Best AI Girlfriend Free 2026', url: '/best-ai-girlfriend-free/', category: 'romance', pub: '2026-04-20' },
  // Reviews
  { title: 'Replika Pro vs Free Comparison', url: '/replika-pro-vs-free/', category: 'companion', pub: '2026-04-21' },
  { title: 'Claude Pro vs ChatGPT Plus 2026', url: '/claude-pro-vs-chatgpt-plus/', category: 'productivity', pub: '2026-04-22' },
  { title: 'Candy.AI Honest Review 2026', url: '/candy-ai-honest-review-2026/', category: 'romance', pub: '2026-04-21' },
  // Guides
  { title: 'AI Therapist App 2026 Guide', url: '/ai-therapist-app-2026/', category: 'mental-health', pub: '2026-04-20' },
  { title: 'AI Companion for Anxiety 2026', url: '/ai-companion-for-anxiety-2026/', category: 'mental-health', pub: '2026-04-20' },
  { title: 'AI Companion for Widows', url: '/ai-companion-for-widows/', category: 'seniors', pub: '2026-04-21' },
  { title: 'AI Companion Pricing Guide 2026', url: '/ai-companion-pricing-guide-2026/', category: 'companion', pub: '2026-04-21' },
  { title: 'AI Companion Voice Chat Guide 2026', url: '/ai-companion-voice-chat-guide-2026/', category: 'companion', pub: '2026-04-21' },
  { title: 'AI Companion Trust & Safety 2026', url: '/ai-companion-trust-safety-2026/', category: 'companion', pub: '2026-04-22' },
  { title: 'AI Companion Privacy Compared 2026', url: '/ai-companion-privacy-compared-2026/', category: 'companion', pub: '2026-04-22' },
  { title: 'Best AI Chatbot for Loneliness', url: '/best-ai-chatbot-for-loneliness/', category: 'companion', pub: '2026-04-22' },
  { title: 'Best AI Image Generator for Characters', url: '/best-ai-image-generator-character/', category: 'productivity', pub: '2026-04-22' },
  { title: 'Talkpal vs Babbel Honest Comparison', url: '/talkpal-vs-babbel-review/', category: 'language', pub: '2026-04-23' },
  // Editorial
  { title: 'Editorial Team', url: '/editorial-team/', category: 'meta', pub: '2026-04-25' },
  { title: 'Education AI for Kids 2026', url: '/education/', category: 'education', pub: '2026-04-25' },
  { title: 'Methodology', url: '/methodology/', category: 'meta', pub: '2026-04-19' }
];

export async function GET() {
  const items = ITEMS.map(i => `
    <item>
      <title><![CDATA[${i.title}]]></title>
      <link>${SITE_URL}${i.url}</link>
      <guid>${SITE_URL}${i.url}</guid>
      <category>${i.category}</category>
      <pubDate>${new Date(i.pub).toUTCString()}</pubDate>
      <description><![CDATA[${i.title} — ${i.category} vertical at AI Companion Today.]]></description>
    </item>`).join('');

  const xml = `<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
  <title>${TITLE}</title>
  <link>${SITE_URL}/</link>
  <description>${DESCRIPTION}</description>
  <language>en</language>
  <atom:link href="${SITE_URL}/rss.xml" rel="self" type="application/rss+xml" />
  <lastBuildDate>${new Date().toUTCString()}</lastBuildDate>${items}
</channel>
</rss>`;

  return new Response(xml, {
    headers: { 'Content-Type': 'application/xml; charset=utf-8' }
  });
}
