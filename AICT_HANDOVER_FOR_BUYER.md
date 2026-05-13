# AI Companion Today — Buyer Handover (operational, no secrets)

Last verified: 2026-05-13 UTC

## What the buyer controls

- Public site: `https://aicompaniontoday.com/`
- Static frontend: Astro build deployed to `/var/www/aicompaniontoday.com`
- Source code: `/root/aict-astro` (same target as `/root/claude-ultime/aict-frontend`)
- GitHub remote: `git@github.com:Joyce007007/aicompaniontoday.git`
- Ghost CMS service: `aict-ghost.service`
- Ghost admin URL: `https://aicompaniontoday.com/ghost/`
- Tracking backend: `aict-pb.service` on `127.0.0.1:8004`
- Nginx config: `/etc/nginx/sites-enabled/aicompaniontoday.com`

## Services

- `nginx`: public HTTPS/static/proxy
- `aict-pb`: FastAPI tracking backend for `/go`, `/pv`, `/pb`, `/api`, `/admin`
- `aict-ghost`: Ghost CMS 6.30.0 for editor/admin and content assets
- `mariadb`, `postgresql`, `redis-server`: server data services used by wider VPS stack

## Build/deploy

```bash
cd /root/aict-astro
npm install
npm run build
rsync -a --delete dist/ /var/www/aicompaniontoday.com/
chown -R www-data:www-data /var/www/aicompaniontoday.com
nginx -t && systemctl reload nginx
```

## Live smoke checks

```bash
for u in / /romance/push/ /romance/ /best-ai-girlfriend-apps/ /ghost/ /ghost/api/admin/site/; do
  curl -k -sS -o /tmp/aict_check -w "https://aicompaniontoday.com$u %{http_code} %{time_total}s bytes:%{size_download}\n" "https://aicompaniontoday.com$u"
done
```

Expected verified state after latest deploy:

- `/`: 200
- `/romance/push/`: 200
- `/romance/`: 200
- `/best-ai-girlfriend-apps/`: 200
- `/assets/candy-ai-card.png`: 200
- `/assets/sofia-ai-companion.png`: 200
- `/ghost/`: 200 direct-origin verified
- `/ghost/api/admin/site/`: 200 direct-origin verified

## Content/visual assets added

- `public/assets/sofia-ai-companion.png`
- `public/assets/candy-ai-card.png`
- `public/assets/ourdream-ai-card.png`
- `public/assets/secrets-ai-card.png`
- `public/assets/kupid-ai-card.png`
- `public/assets/nomi-ai-card.png`
- `public/creatives_ai/banner_01_sofia.png` through persona banners

The romance and best-AI-girlfriend money pages now show non-explicit adult AI companion visuals.

## Internationalization recommendation

Do **not** auto-machine-translate the live English pages invisibly. Best solution for resale/SEO:

1. Keep English canonical pages.
2. Add real static localized folders: `/fr/`, `/es/`, `/pt-br/`, `/ja/` only for top money pages first.
3. Add `hreflang` alternates between localized pages.
4. Use Cloudflare Worker or nginx/Cloudflare country header only for a **one-time soft suggestion banner**, not forced redirect. Forced IP redirect can hurt SEO, affiliate compliance, and user trust.
5. Track locale in URL/cookie: user choice beats IP.

Current safe baseline in `Base.astro`: browser-language helper for JA/PT-BR snippets and English override. This is not a complete i18n system; it is a reversible UX layer.

## Handover/security notes

- Do not send secrets in chat/email. Transfer credentials through a password manager/vault.
- Ghost owner/admin email/password must be rotated during sale.
- GitHub repo ownership/access must be transferred or buyer added as admin.
- Domain registrar/DNS/Cloudflare must be transferred separately.
- Affiliate-network accounts/offers/postback secrets must be transferred/rotated separately.
- Before final sale, export Ghost content and database snapshot, and provide a clean `.env.example`/secret inventory without values.

## Rollback/backups

- Pre-visual-fix webroot backup: `/root/vps-fix-backups/20260513-000305-aict-before-image-visuals`
- Ghost content path: `/var/www/aict-ghost/content`
- Ghost sqlite DB path: `/var/www/aict-ghost/content/data/ghost-local.db`
