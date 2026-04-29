// Fetch AI/AI-companion news from reliable RSS feeds at build time.
const FEEDS = [
  { name: 'TechCrunch AI',   url: 'https://techcrunch.com/category/artificial-intelligence/feed/' },
  { name: 'The Verge AI',    url: 'https://www.theverge.com/ai-artificial-intelligence/rss/index.xml' },
  { name: 'VentureBeat AI',  url: 'https://venturebeat.com/category/ai/feed/' },
  { name: 'AI Business',     url: 'https://aibusiness.com/rss.xml' },
  { name: 'MIT Tech Review AI', url: 'https://www.technologyreview.com/feed/?topic=artificial-intelligence' }
];

const KEYWORDS = /companion|chatbot|girlfriend|boyfriend|virtual friend|replika|character\.ai|nomi|kindroid|woebot|wysa|talkpal|jasper|copy\.ai|claude|chatgpt|anthropic|openai|gemini|mental health ai|senior tech|elliq/i;

function cleanXmlText(value = '') {
  return value
    .replace(/^<!\[CDATA\[/, '')
    .replace(/\]\]>$/, '')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .trim();
}

function extractTag(block, tag) {
  const match = block.match(new RegExp(`<${tag}[^>]*>([\\s\\S]*?)<\\/${tag}>`, 'i'));
  return cleanXmlText((match || [])[1] || '');
}

function isSafeExternalUrl(url) {
  try {
    const u = new URL(url);
    return u.protocol === 'https:' && !!u.hostname && !url.includes('<![CDATA[') && !url.includes(']]>');
  } catch (_) {
    return false;
  }
}

function parseItems(xml, source) {
  const items = [];
  const matches = [...xml.matchAll(/<item[^>]*>([\s\S]*?)<\/item>/g)];
  for (const m of matches.slice(0, 25)) {
    const block = m[1];
    const title = extractTag(block, 'title');
    const link = extractTag(block, 'link');
    const date = extractTag(block, 'pubDate');
    const desc = extractTag(block, 'description');
    const plain = cleanXmlText(desc.replace(/<[^>]+>/g, '')).slice(0, 180);
    if (title && isSafeExternalUrl(link)) items.push({ title, url: link, date, summary: plain, source: source.name });
  }
  return items;
}

export async function getCompanionNews(limit = 8) {
  const collected = [];
  await Promise.all(FEEDS.map(async (f) => {
    try {
      const res = await fetch(f.url, { headers: { 'User-Agent': 'Mozilla/5.0 (AICT/1.0)' } });
      if (!res.ok) return;
      const xml = await res.text();
      const items = parseItems(xml, f);
      for (const it of items) {
        if (KEYWORDS.test(`${it.title} ${it.summary}`)) collected.push(it);
      }
    } catch (e) {}
  }));
  collected.sort((a, b) => new Date(b.date || 0) - new Date(a.date || 0));
  return collected.slice(0, limit);
}
