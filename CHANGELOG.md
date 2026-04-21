
## v21.0 — 21/04/2026 15:50 UTC

**M
## v22.1 — 21/04/2026 16:20 UTC

**Patches finaux: silos mapping + FAQ schema auto + Amazon component**

2jagency mapping extension:
- 21 new slugs for silo products: Jumia (5 geos), Mercado Libre (4 geos), Brasil iGaming (7 casas SECAP), hide-mn-vpn, secure-my-email, witopia, abelssoft, abelssoft-utilities
- Total mapping: 44 slugs (up from 23)
- Backup: go_mapping.json.bak-v22
- 2jagency-go.service disabled (obsolete, twoj-pb port 8003 handles all /go)

AICT patches:
- AmazonBox Astro component ready for when Joyce signs up Amazon Associates
- FAQPage Schema.org auto-detection on [slug].astro (parses Q/A from HTML)
- _classify_source helper in aict_pb.py (classifies revenue by Amazon/Gumroad/EVADAV/Sponsored/Direct/Reddit/Quora/Pinterest/Google Ads/CrakRevenue/Other)


## v22.0 — 21/04/2026 15:50 UTC

**Mode exécution full: 6 silos 2jagency + AICT monétisation bundle + article factory cron**

2jagency pivot 6 silos SEO:
- /security/ (Privacy+VPN), /wellness/ (Supplements), /africa/ (Jumia), /latam/ (Mercado Libre), /brasil/ (iGaming 18+), /tools/ (SaaS B2B)
- Chaque silo: landing page SEO complète avec Schema ItemList+BreadcrumbList, 3-7 products featured, CTA /go tracked
- Homepage refondue avec nav 6-silo
- Sitemap régénéré 33 URLs

AICT monétisation bundle:
- /premium-guide/ landing €19 Gumroad-ready
- Push notifications EVADAV injectées Base.astro
- /partner/ upgradé avec pricing public (€200/€500/€2000 par placement)
- Outreach templates direct deals (Kindroid, Nomi, Candy, Replika) dans /root/outreach/
- Article factory auto-publish Ghost: 20 money-keywords queue, cron daily 09:00 UTC
- 1ère auto-publication OK: candy-ai-honest-review-2026 live

Backup:
- Tag v21.1 pre-v22 checkpoint
- /var/backups/aict/v21.1/ snapshot
- /var/backups/twoj/pre-silos-<ts>/ snapshot
- Restic hors-cycle tag pre-v22-2026-04-21

Crons new:
- 0 9 * * * aict_article_factory.py (publish 1 post/day)

Pending Joyce action:
- Google Workspace sur 2jagency.com (AICT_WORKSPACE_SETUP.txt on desktop)
- Signup 7 networks (AICT_SIGNUP_TEMPLATE.txt on desktop)
- Gumroad signup pour activer /premium-guide/
- Reddit/Quora comptes dédiés (requires phone verif)

ode adaptatif : execution autonome vers revenu**

Content explosion:
- 11 new AICT posts published via Ghost Admin API. Total posts Ghost: 17. Total Astro pages: 35.
- Posts: replika-alternatives, candy-vs-secrets, best-ai-girlfriend-free, is-companion-addictive, nomi-vs-kindroid, privacy-compared, for-anxiety, voice-chat-guide, pricing-guide, best-ai-boyfriend, trust-safety.
- All 1500+ words, money-keywords, YMYL disclaimers, /go tracked CTAs.

Monetization infrastructure:
- Live dashboard /admin/ops/ Basic Auth. Clicks/conversions/revenue/sources.
- PDF lead magnet /downloads/state-of-ai-companion-2026.pdf.
- Monitor /root/scripts/aict_monitor.sh cron 15min with Telegram alerts.

DB cleanup: removed 2 test conversions.

Files: build_lead_magnet_pdf.sh, aict_monitor.sh, admin_ops patch, 11 Ghost posts, PDF.

