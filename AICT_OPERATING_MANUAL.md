# AI Companion Today — Operating Manual (no assistant needed)

Last updated: 2026-05-13 UTC

## What AICT is

AICT is a static Astro affiliate site plus a small FastAPI tracking backend and a Ghost CMS instance.

- Public site: https://aicompaniontoday.com/
- Ghost admin: https://aicompaniontoday.com/ghost/
- Source repo: https://github.com/Joyce007007/aicompaniontoday
- VPS source path: /root/aict-astro
- Live webroot: /var/www/aicompaniontoday.com
- Tracking backend service: aict-pb.service
- Ghost service: aict-ghost.service

## How the site updates

### Static pages / money pages

Most visible pages are static Astro files under `src/pages/`.
To change a ranking/review/nav page:

1. Edit the relevant `.astro` file.
2. Run `npm run build` from `/root/aict-astro`.
3. Deploy `dist/` to `/var/www/aicompaniontoday.com/`.
4. Reload nginx only if nginx config changed.
5. Commit and push to GitHub.

Commands:

```bash
cd /root/aict-astro
npm run build
rsync -a --delete dist/ /var/www/aicompaniontoday.com/
chown -R www-data:www-data /var/www/aicompaniontoday.com
git status --short
git add . && git commit -m "update AICT" && git push
```

### News page

`/news/` is generated at build time from two sources:

1. RSS feeds in `src/lib/ai-news.js`:
   - TechCrunch AI
   - The Verge AI
   - VentureBeat AI
   - AI Business
   - MIT Technology Review AI

2. Ghost posts via `src/lib/ghost.js`, only if Ghost Content API key is configured during build.

Important: news are **not continuously dynamic on every page view**. They refresh when the Astro site is rebuilt/deployed. If you publish a Ghost post or want fresher RSS news, rebuild and deploy.

Current cron found:

- `/root/scripts/aict_heal_mapping.sh` every 5 minutes keeps offer mapping healthy.
- `/root/scripts/aict_rebuild_news.sh` every 6 hours rebuilds/deploys Astro so RSS/Ghost-driven news refresh automatically.

Ghost content changes also trigger rebuild through `aict-ghost-webhook.service` on `POST /hooks/ghost-rebuild` with a secret stored in `/root/.joyce-vault.json`.

### Ghost

Ghost is available for CMS/admin content:

- Admin URL: https://aicompaniontoday.com/ghost/
- Local path: /var/www/aict-ghost
- SQLite DB: /var/www/aict-ghost/content/data/ghost-local.db
- Service: `systemctl status aict-ghost`

Ghost content appears in Astro only if the site is rebuilt with a valid `GHOST_CONTENT_KEY`.

### Tracking / monetization links

CTA links generally go through `/go?offer=...&sid=...`.
Backend:

- `/go` records click then redirects to affiliate URL from `public/aict_mapping.json` deployed as `/var/www/aicompaniontoday.com/aict_mapping.json`.
- `/best` is a backend smart router for paid/prelander traffic. It reads `/var/www/aicompaniontoday.com/best_offer_matrix.json`, chooses an offer by vertical/country/device, then redirects to `/go`.
- `/pv` records pageviews.
- `/pb` receives affiliate postbacks.
- `/admin` gives a basic stats dashboard if credentials are available.

Do not test `/go` repeatedly from monitors: it pollutes click stats. If `/best` is used publicly, nginx must proxy `location = /best` to the FastAPI backend.

## Header tabs / menu status

Header is in `src/layouts/Base.astro` for most pages.
Romance page has a custom standalone header in `src/pages/romance/index.astro`.

Main header tabs:

- AI Girlfriend Apps: `/romance/` — static page + client-side persona tab filtering.
- Free Trials: `/best-ai-girlfriend-free/` — static page.
- Candy Review: `/candy-ai-honest-review-2026/` — static page.
- Candy vs Secrets: `/candy-ai-vs-secrets-ai-2026/` — static page.
- Replika Alternatives: `/replika-alternatives-2026/` — static page.
- Privacy: `/ai-companion-privacy-compared-2026/` — static page.
- Matcher: `/tools/matcher/` — static HTML with client-side JavaScript quiz; it is dynamic in the browser, not server-side.
- Methodology: `/methodology/` — static page.

## Monetization layers present / recommended

Present:

- CPA/affiliate links via CrakRevenue `/go` mapping.
- EVADAV push widget on romance page.
- Partner/sponsored placement page at `/partner/`.
- Newsletter capture endpoint `/api/newsletter`.
- Tracking DB for pageviews/clicks/conversions.

Recommended next monetization additions:

1. CPA first: fix offers and prove paid conversions.
2. Sponsored placement second: use `/partner/` once traffic proof exists.
3. CPC/native ads only after clean traffic: adult-friendly networks can be tested, but not before UX and conversion proof.
4. SaaS last: only after affiliate proof, and preferably a lightweight matcher/pro tool, not a full adult chat product.

## Arborescence important

## src
- components/
- data/
- layouts/
- lib/
- pages/
- styles/
## src/pages
- [slug].astro
- about/
- advertising-disclosure/
- affiliate-disclosure/
- ai-companion-privacy-compared-2026/
- best-ai-companion-apps-2026/
- best-ai-companion-seniors-2026/
- best-ai-girlfriend-apps/
- best-ai-girlfriend-free/
- best-ai-language-tutor-2026/
- best-ai-mental-health-2026/
- best-ai-writing-assistant-2026/
- candy-ai-honest-review-2026/
- candy-ai-vs-secrets-ai-2026/
- companion.astro
- contact/
- disclaimer-mental-health/
- editorial-team.astro
- education.astro
- free-ai-girlfriend-apps/
- gaming.astro
- how-affiliate-links-work/
- index.astro
- index.astro.bak-pre-bundle-cta-1777135613
- language.astro
- mental-health.astro
- methodology/
- news.astro
- partner.astro
- premium-guide.astro
- privacy/
- productivity.astro
- replika-alternatives-2026/
- reviews/
- romance/
- rss.xml.js
- seniors.astro
- terms/
- tools/
## src/components
- AmazonBox.astro
- ComparisonTable.astro
- NewsletterForm.astro
- SchemaOrg.astro
- SchemaOrg.astro.bak-pre-audit
- StickyAffiliateCTA.astro
## src/lib
- ai-news.js
- ghost.js
## public/assets
- candy-ai-card.png
- candy-ai-card.svg
- kupid-ai-card.png
- kupid-ai-card.svg
- nomi-ai-card.png
- nomi-ai-card.svg
- ourdream-ai-card.png
- ourdream-ai-card.svg
- secrets-ai-card.png
- secrets-ai-card.svg
- sofia-ai-companion.png
## public/creatives_ai
- banner_01_sofia.png
- banner_02_amara.png
- banner_02_anna.png
- banner_03_erin.png
- banner_03_kat.png
- banner_04_lea.png
- banner_04_priya.png
- banner_05_maria.png
- banner_05_mei.png
- banner_06_emma.png
- banner_06_isabela.png
- banner_07_layla.png
- banner_07_nina.png
- banner_08_astrid.png
- banner_08_julia.png
- banner_09_valeria.png
- banner_09_vera.png
- banner_10_tara.png
- banner_11_mei.png
- banner_12_yuki.png
- banner_13_priya.png
- banner_14_kavya.png
- banner_15_yasmina.png
- banner_16_layla.png
- banner_17_chloe.png
- banner_18_isla.png
- banner_19_hanna.png
- banner_20_astrid.png
- banner_21_amber.png
- banner_22_scarlett.png
- banner_23_jade.png
- banner_24_camille.png
- banner_25_zara.png
- banner_26_aria.png
- banner_27_raven.png
- banner_28_selene.png

## Smoke checks

```bash
systemctl is-active nginx aict-pb aict-ghost
nginx -t
curl -I https://aicompaniontoday.com/
curl -I https://aicompaniontoday.com/ghost/
curl -I https://aicompaniontoday.com/news/
```

## P0 rules

- Never expose secrets from env/config/vault in public docs.
- Keep `/go`, `/pv`, `/pb`, Ghost and nginx alive.
- After changing images/nav/money pages: build, deploy, screenshot mobile, test links, then commit.
