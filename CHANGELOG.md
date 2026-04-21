# AI Companion Today — Changelog

Versions are stored in `/var/backups/aict/v<version>/` on the VPS and tagged in git on GitHub (Joyce007007/aicompaniontoday).

**Rules**
- Major structural changes (new section, major redesign, new monetization lever) → **major bump** (v17 → v18)
- Minor improvements (copy tweaks, one new feature, one bugfix) → **patch bump** (v18.0 → v18.1)
- Each release: tag `vX.Y`, backup prod dir, commit source, push to GitHub.

---

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
