// Fetch AI/AI-companion news from reliable RSS feeds at build time.
const FEEDS = [
  { name: 'TechCrunch AI',   url: 'https://techcrunch.com/category/artificial-intelligence/feed/' },
  { name: 'The Verge AI',    url: 'https://www.theverge.com/ai-artificial-intelligence/rss/index.xml' },
  { name: 'VentureBeat AI',  url: 'https://venturebeat.com/category/ai/feed/' },
  { name: 'AI Business',     url: 'https://aibusiness.com/rss.xml' },
  { name: 'MIT Tech Review AI', url: 'https://www.technologyreview.com/feed/?topic=artificial-intelligence' }
];

const KEYWORDS = /companion|chatbot|girlfriend|boyfriend|virtual friend|replika|character\.ai|nomi|kindroid|woebot|wysa|talkpal|jasper|copy\.ai|claude|chatgpt|anthropic|openai|gemini|mental health ai|senior tech|elliq/i;

function parseItems(xml, source) {
  const items = [];
  const matches = [...xml.matchAll(/<item[^>]*>([\s\S]*?)<\/item>/g)];
  for (const m of matches.slice(0, 25)) {
    const block = m[1];
    const title = (block.match(/<title[^>]*>(?:<!\[CDATA\[)?([\s\S]*?)(?:\]\]>)?<\/title>/) || [])[1] || '';
    const link  = (block.match(/<link[^>]*>([\s\S]*?)<\/link>/) || [])[1] || '';
    const date  = (block.match(/<pubDate>([\s\S]*?)<\/pubDate>/) || [])[1] || '';
    const desc  = (block.match(/<description[^>]*>(?:<!\[CDATA\[)?([\s\S]*?)(?:\]\]>)?<\/description>/) || [])[1] || '';
    const plain = desc.replace(/<[^>]+>/g, '').slice(0, 180);
    if (title && link) items.push({ title: title.trim(), url: link.trim(), date, summary: plain, source: source.name });
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
