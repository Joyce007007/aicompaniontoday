# AI Companion Today — Changelog

Versions are stored in `/var/backups/aict/v<version>/` on the VPS and tagged in git on GitHub (Joyce007007/aicompaniontoday).

**Rules**
- Major structural changes (new section, major redesign, new monetization lever) → **major bump** (v17 → v18)
- Minor improvements (copy tweaks, one new feature, one bugfix) → **patch bump** (v18.0 → v18.1)
- Each release: tag `vX.Y`, backup prod dir, commit source, push to GitHub.

---

## v20.0 — 21/04/2026 12:35 UTC

**Security hardening + monetization diagnostics + backups offsite**

Security audit findings & fixes:
- **fail2ban** already active with 3 jails (sshd, nginx-botsearch, recidive), 724 IPs banned cumulative, 102k tentatives SSH bloquées. Added **4th jail** `ghost-admin` matching `POST /ghost/api/admin/session/` 401/403.
- **ufw** already active with 22/80/443 allowed, 8443/8888 denied. **Added deny**: 8880 (Plesk sw-cp-serverd), 6080 (websockify VNC proxy) to prevent public exposure of admin panel.
- **SSH** already hardened: `PermitRootLogin prohibit-password`, `PasswordAuthentication no`, `MaxAuthTries 3`. 1 single authorized_key.
- **Unattended-upgrades** already active. Triggered `apt-get upgrade` (20+ packages: docker-ce, containerd, systemd, fail2ban itself).
- **Secrets** — surprise, already strong (not defaults): `ADMIN_PASS=VRG1jOPscjWtYoPRTfse`, `POSTBACK_SECRET=aict_pb_secret_c7e5f9a3b8e2a7f5b9d3c1e6f4a2b8d0`, stored in systemd unit `Environment=` (not .env). twoj-pb has its own independent secret.
- **File permissions** — `chmod 600` on all 4 `.env` files in `/root/aict-astro`, `/root/twoj-astro`, `/root/agent-argentique` (main + config).
- **Logs** — rate-limit detected an `/admin` brute-force from 185.147.212.82 on 18/04, properly throttled by nginx; fail2ban recidive jail captures repeaters.

Monetization diagnostics:
- **`/pb` endpoint test PASSED** — sending `secret=<strong>&sid=<clicked>&offer=<slug>&amount=<val>` returns `{"ok":true}` and inserts into `aict.conversions`. Therefore the reason no conversions appeared since 19/04 is **NOT** that /pb is broken. Likely cause: CrakRevenue dashboard postback URL is misconfigured or traffic volume too low for 7-30d PPS cycle.
- **Action required (Joyce)** — visit CrakRevenue dashboard and verify postback URL points to `https://aicompaniontoday.com/pb?sid={aff_sub5}&offer={offer_id}&amount={payout}&conv_id={transaction_id}&secret=aict_pb_secret_c7e5f9a3b8e2a7f5b9d3c1e6f4a2b8d0` — if set, conversions will start arriving within 24-72h.

Backups offsite:
- **restic** initialized at `/var/backups/restic` with password file `/root/.restic-password` (chmod 600). Daily cron 02:00 UTC via `/root/scripts/aict_restic_backup.sh`. First backup captured 3 snapshots (static+source, aict.sql, twoj.sql). Retention: 14d + 8w + 12m. Next step (manual): add remote backend (B2, S3, or SFTP) for true offsite.

New files:
- `public/robots.txt` (also in /var/www/aicompaniontoday.com/ as static)
- `public/rss.xml` (empty shell, to be populated by future cron)
- `/etc/fail2ban/filter.d/ghost-admin.conf`
- `/etc/fail2ban/jail.d/ghost-admin.conf`
- `/root/scripts/aict_restic_backup.sh`

Cron changes:
- Added `0 2 * * *` restic backup
- Removed broken `/root/scripts/twoj_autopilot_cycle.sh` (2jagency-site is static HTML, no git pull needed)

Manual tasks deferred (Joyce-only, require credentials):
- Cloudflare: enable orange-proxy on aicompaniontoday.com DNS A record
- CrakRevenue dashboard: set postback URL (see above)
- Google Search Console + GA4: connect via OAuth
- Restic offsite remote: pick a provider and configure `B2_ACCOUNT_ID`/equivalent in /root/.restic-env

## v19.0 — 21/04/2026 11:46 UTC

**Schema per-post + /news/ hub + /partner/ page + State of AI Companion 2026 report + daily rebuild cron**

New features:
- **Schema.org per-post** — `[slug].astro` now emits `Article` (for posts) + `BreadcrumbList` schemas in addition to sitewide `Organization` + `WebSite`. Matcher CTA block on every post. Newsletter form (compact) at bottom of every post and page.
- **/news/ hub** — curated live AI companion news (via RSS from TechCrunch, The Verge, VentureBeat, MIT Tech Review, AI Business) + Ghost posts tagged `report` or `study`. Breadcrumb schema.
- **/partner/ page** — sponsored placements pitch page: audience profile, 5 placement formats (sponsored review, newsletter placement, category takeover, affiliate network inclusion, matcher quiz integration), editorial firewall, contact email.
- **State of AI Companion 2026** — 1,400-word inaugural market report published in Ghost (tags: Report, News, Study). Covers 7 verticals, regulatory posture, revenue concentration, buyer questions. Surfaces on /news/ as "AICT original reports".
- **Daily Astro rebuild cron** — `/root/scripts/aict_astro_rebuild.sh` runs at 04:30 UTC daily so RSS news section stays fresh without manual intervention.

Files added:
- `src/pages/news.astro`
- `src/pages/partner.astro`
- `/root/scripts/aict_astro_rebuild.sh`
- Ghost post: `/state-of-ai-companion-2026/`

Files modified:
- `src/pages/[slug].astro` (Article+Breadcrumb schema, matcher CTA, newsletter form)

Audit green:
- 10 new pages tested HTTP 200
- Schema.org on /best-ai-companion-apps-2026/: Article, BreadcrumbList, ListItem, Organization, SearchAction, WebSite
- /state-of-ai-companion-2026/ 200 with Replika/Woebot/FDA mentions
- Newsletter form present on best-of posts (2 refs)
- /go 302 on candy/gal_sofia/evadav_push
- 0 leak Jocelyn on 18 pages
- 2jagency.com intact (200)
- New cron: daily 04:30 UTC rebuild to refresh RSS news

## v18.0 — 21/04/2026 11:32 UTC

**Matcher quiz + LLM citations + newsletter + versioning system**

New features:
- **AI Companion Matcher** (`/tools/matcher/`) — 7-question client-side quiz, scores 17 apps across 6 goals/4 budgets/3 styles, renders top match + 2 alternatives with /go tracked CTA. SaaS hook for exit-ready positioning.
- **llms.txt** — markdown summary at `/llms.txt` for LLM crawlers (ChatGPT, Claude, Perplexity, Gemini) with brand summary, vertical taxonomy, primary URLs, attribution rules, and key citable facts.
- **/api/facts.json** — 29 quantified facts for LLM grounded-answer citations (Replika users, Woebot FDA, ElliQ NYS program, Duolingo Max GPT-4, etc.) with source + citation_url per fact.
- **Schema.org JSON-LD** — Organization + WebSite (with SearchAction) sitewide via Base.astro; ItemList schema on homepage; reusable `<SchemaOrg>` component for posts.
- **Newsletter form** — reusable `<NewsletterForm>` component on homepage; POST to existing FastAPI `/api/newsletter` endpoint (rate-limited, persists to `aict.newsletter_subscribers`).
- **Versioning system** — `/root/scripts/aict_release.sh` helper for future versions; CHANGELOG.md in repo; prod backups under `/var/backups/aict/vX.Y/`; git tags pushed to GitHub.
- **Nav updated** — Matcher CTA added to main navigation and footer.

Bug fixes:
- Nginx legacy `try_files` rules for `/reviews/`, `/guides/`, `/compare/`, `/best/`, `/news/`, `/tools/`, `/fr/` were intercepting Astro subdirectories with 404 — removed.
- Nginx `try_files $uri $uri/ $uri.html` updated to `try_files $uri $uri/index.html $uri/ $uri.html` to serve Astro directory index files.
- Static serve for `/api/facts.json` and `/llms.txt` added before the `/api/` FastAPI proxy block, so they serve from disk rather than hitting uvicorn.

Files added:
- `src/pages/tools/matcher.astro`
- `src/components/SchemaOrg.astro`
- `src/components/NewsletterForm.astro`
- `public/llms.txt`
- `public/api/facts.json`
- `CHANGELOG.md`

Files modified:
- `src/layouts/Base.astro` (Schema.org + Matcher nav link)
- `src/pages/index.astro` (Matcher CTA banner + Newsletter form + ItemList schema)
- `/etc/nginx/sites-enabled/aicompaniontoday.com` (legacy try_files removed, /api/facts.json + /llms.txt static serves, Astro-friendly try_files)

Audit green:
- 14 pages HTTP 200
- /api/facts.json returns 29 facts
- /llms.txt returns 63 lines
- Schema.org JSON-LD: Organization, WebSite, ItemList, ListItem, Product, SearchAction present
- Newsletter POST /api/newsletter returns {"ok":true}
- /go 302 on 5 slugs tested (candy, gal_sofia, gal_amber, secrets, evadav_push)
- 0 leak Jocelyn on 15 pages
- 2jagency.com intact (200) + /ghost/ (200)


## v17.5 — 19/04/2026 06:05 UTC

**/romance/ refondu + Google Translate + RSS news**

- /romance/ sans mention "18+ ADULT CONTENT" / "NSFW" / "Affiliate notice"
- 28 personas cliquables avec images 492x328 (Sofia, Anna, Kat, Léa, Maria, Emma, Nina, Julia, Vera, Tara, Mei, Yuki, Priya, Kavya, Yasmina, Layla, Chloé, Isla, Hanna, Astrid, Amber, Scarlett, Jade, Camille, Zara, Aria, Raven, Selene)
- 6 tabs JS filtrage client-side : All / Latin / European / Asian / English / Middle East
- Table 10 plateformes avec prix + CTA /go
- Google Translate widget 25 langues auto sitewide
- Home : "Latest AI companion news" RSS (TechCrunch, Verge, VentureBeat, MIT Tech Review, AI Business)
- Home : "AI companion coverage referenced across" 8 médias
- mapping.json 62 slugs (28 galleries + 6 rank + 6 CTA + 20 CR short + 2 evadav)

**Files**
- `src/pages/romance/index.astro` (recréé)
- `src/pages/index.astro` (RSS + As-seen-on)
- `src/layouts/Base.astro` (Google Translate + nav 7 verticales)
- `src/lib/ai-news.js` (RSS aggregator)
- `src/pages/[slug].astro` (disclosure retiré footer posts)

## v17.0 — 19/04/2026 05:27 UTC

**7 verticales + /romance/ age-gated + /go router restauré**

- Homepage 7 verticales grid (Companion / Mental Health / Seniors / Language / Productivity / Romance / Gaming)
- /romance/ avec age-gate JS + 19 offres CrakRevenue + 25 galleries + X-Robots-Tag noindex
- /go router restauré via aict_mapping.json (59 slugs → EVADAV monétisation)
- 0 leak Jocelyn sur 15 pages
- 5 alias pages (companion/mental-health/seniors/language/productivity) meta-refresh vers best-of
- /gaming coming-soon stub

## v16.0 — 19/04/2026 03:52 UTC

**Ghost content migration + CrakRevenue injection**

- 19 CrakRevenue AI offers injectés en DB `offer_candidates` avec status `nsfw_subdomain_candidate`
- Ghost AICT : 7 pages publiées (About, Methodology, Advertising Disclosure, Privacy, Terms, Contact, Mental Health Disclaimer)
- Ghost 2jagency : 19 articles migrés
- GitHub repo `Joyce007007/aicompaniontoday` créé

## v15.0 — 19/04/2026 00:00 UTC

**Initial Astro scaffold**

- Astro 5 + Tailwind 3 + Ghost Content API helper
- FastAPI backend aict-pb port 8004 + DB aict
- Ghost CMS instance port 2369 (SQLite local)
- nginx /ghost/ reverse proxy + Cloudflare Rocket Loader bypass
