const GHOST_URL = import.meta.env.GHOST_URL || 'https://aicompaniontoday.com';
const KEY = import.meta.env.GHOST_CONTENT_KEY;

async function fetchAll(resource, extra='') {
  const items = [];
  let page = 1;
  while (true) {
    const url = `${GHOST_URL}/ghost/api/content/${resource}/?key=${KEY}&limit=50&page=${page}&include=tags,authors${extra}`;
    const r = await fetch(url);
    if (!r.ok) break;
    const d = await r.json();
    items.push(...(d[resource] || []));
    if (!d.meta?.pagination?.next) break;
    page++;
  }
  return items;
}

export async function getAllPosts() { return fetchAll('posts', '&filter=status:published'); }
export async function getAllPages() { return fetchAll('pages'); }
export async function getPostBySlug(slug) {
  const r = await fetch(`${GHOST_URL}/ghost/api/content/posts/slug/${slug}/?key=${KEY}&include=tags,authors`);
  if (!r.ok) return null;
  const d = await r.json();
  return d.posts?.[0] || null;
}
export async function getPageBySlug(slug) {
  const r = await fetch(`${GHOST_URL}/ghost/api/content/pages/slug/${slug}/?key=${KEY}`);
  if (!r.ok) return null;
  const d = await r.json();
  return d.pages?.[0] || null;
}
