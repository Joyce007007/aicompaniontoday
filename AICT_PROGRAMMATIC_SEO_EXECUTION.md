# AICT Programmatic SEO + Automation Execution Report

Date: 2026-05-13 UTC

## What was executed

### 1. Structured app database

Created:

```txt
/root/aict-astro/src/data/apps.json
```

Current tracked apps:

1. Candy AI
2. OurDream AI
3. Nomi AI
4. Kupid AI
5. DreamGF AI
6. Kindroid
7. Replika
8. Character.AI
9. JanitorAI
10. CrushOn AI

Each record contains:

- name
- slug
- official URL
- category
- best-for positioning
- pricing notes
- free trial notes
- affiliate offer key when AICT has one
- affiliate network / commission evidence
- traffic proof
- revenue proof
- country proof when available
- feature list
- risk list
- alternatives

## 2. Programmatic pages generated

Generated 50 SEO money/support pages plus one index page:

```txt
/apps/[slug]/
/alternatives/[slug]/
/pricing/[slug]/
/privacy/[slug]/
/free-trials/[slug]/
/apps/
```

For 10 apps, that creates:

- 10 app review pages
- 10 alternatives pages
- 10 pricing pages
- 10 privacy pages
- 10 free-trial pages
- 1 database index

Live examples:

- https://aicompaniontoday.com/apps/candy-ai/
- https://aicompaniontoday.com/alternatives/candy-ai/
- https://aicompaniontoday.com/pricing/candy-ai/
- https://aicompaniontoday.com/privacy/candy-ai/
- https://aicompaniontoday.com/free-trials/candy-ai/

## 3. Affiliate CTA logic

If an app has `affiliateOffer`, generated pages use:

```txt
/go?offer=OFFER&sid=CONTEXT
```

If no verified affiliate path exists, the page uses the official product URL and labels evidence as unknown rather than inventing commissions.

## 4. Automatic news rebuild cron

Installed:

```txt
/root/scripts/aict_rebuild_news.sh
```

Cron:

```cron
17 */6 * * * /root/scripts/aict_rebuild_news.sh
```

Effect:

- every 6 hours
- rebuilds Astro
- refreshes RSS news captured at build time
- deploys `/dist/` to `/var/www/aicompaniontoday.com/`
- runs `nginx -t`
- reloads nginx
- writes logs to `/var/log/aict_rebuild_news.log`

## 5. Ghost rebuild webhook

Installed service:

```txt
aict-ghost-webhook.service
```

Script:

```txt
/root/scripts/aict_ghost_rebuild_webhook.py
```

Public endpoint:

```txt
POST https://aicompaniontoday.com/hooks/ghost-rebuild
```

Security:

- secret stored in `/root/.joyce-vault.json`
- endpoint rejects unauthenticated requests with `401`
- secret is not committed to GitHub

Ghost DB webhooks configured for:

- `post.published`
- `post.edited`
- `page.published`
- `page.edited`

When Ghost triggers these events, the webhook queues `/root/scripts/aict_rebuild_news.sh`.

## 6. Verification

Verified:

- `npm run build` successful
- 123 pages built
- 51 new programmatic routes checked live
- 0 live HTTP errors among generated pages
- `nginx -t` successful
- services active:
  - nginx
  - aict-pb
  - aict-ghost
  - aict-ghost-webhook
- unauthenticated webhook returns 401
- authenticated webhook test returned 202 and rebuilt successfully

## 7. Important limitation

This creates the SEO structure. It does not magically create authority or revenue.

Revenue still requires:

1. indexed pages
2. backlinks / placements
3. affiliate approvals
4. traffic
5. verified paid conversions / payouts

Do not count clicks as revenue.
