# AI Companion Today — Operations Manual (Exit-ready)

**For non-dev operators.** Run aicompaniontoday.com without writing code.

## Quick reference

| What | Where |
|---|---|
| Public site | https://aicompaniontoday.com |
| Admin CMS (Ghost) | https://admin.aicompaniontoday.com |
| Click tracker (FastAPI) | https://aicompaniontoday.com/go/{slug} |
| Admin stats | https://aicompaniontoday.com/_aict-k3n8q7-panel/ |
| Repo source | https://github.com/Joyce007007/aicompaniontoday |

## 1. Publish a new review or guide

1. Open **https://admin.aicompaniontoday.com**
2. New Post
3. Select template: `guide` (not tested yet) or `review` (tested 14-30d)
4. Tag vertical: `companion`, `mental-health`, `seniors`, `language`, `productivity`, `gaming`, or `romance`
5. For **mental-health** tag: Crisis banner auto-added, disclaimer pre-filled
6. For **romance** tag: Age-gate auto-added, page set to `noindex`
7. Attribution: **always "The AICT Editorial Team"** (collective byline). Never an individual name.
8. Publish → auto-rebuild in 3 min

## 2. Upgrade a guide to a review

- After 14-30 days of real testing, edit the post
- Change tag from `guide` to `review`
- Replace "preliminary" notation with actual test data
- Publish → auto-rebuild

## 3. Approve AI companion app as partner

1. `/admin/offer-queue/` on FastAPI admin
2. Review pending CrakRevenue / Impact offers
3. **Romance/NSFW offers** are flagged `nsfw_subdomain_candidate` — approve only for `/romance/` section
4. **Cap rule**: never more than 15% of total offers in romance vertical
5. Approve → appears in vertical listing within 5 min

## 4. Publish a /news/ study

Studies are the flagship PR play. Each = potential 30-50 backlinks.

1. In Ghost: new post, tag `study` + `news`
2. Include: methodology, n, dates, 8-12 custom visuals
3. Expert quote (mental-health studies require psychiatrist/psychologist quote)
4. Distribute via PRNewswire + pitch 150-300 journalists

## 5. Mental-health content rules (YMYL)

- **Every mental-health page** auto-includes crisis banner (988 US / 3114 France)
- **Every mental-health page** includes "This is not medical advice" disclaimer
- Reviews of mental-health apps must be **reviewed by a licensed professional** (quoted or authoring)
- Never claim an app treats, diagnoses, or cures a condition

## 6. /romance/ section rules

- **Age-gate** interstitial on entry (18+ confirm)
- **Robots noindex** on all /romance/* pages
- **No homepage link** to romance
- **Content cap**: max 15% of total published articles
- **Budget cap**: max 15% of paid traffic budget

## 7. Backup and restore

Identical to 2J Agency — see its OPERATIONS.md.

## 8. Weekly ops

- **Mon**: offer queue review
- **Wed**: publish 2-3 articles
- **Fri**: newsletter
- **Sun 18h UTC**: auto-report on Telegram `[AICT]`

## 9. Stack summary

- **Frontend** : Astro 5.x SSG in `/root/aict-astro/`
- **CMS** : Ghost 6.x at `admin.aicompaniontoday.com:2369`, DB MariaDB `aict_ghost`
- **API / tracker** : FastAPI `/root/aict-pb/`. Service: `aict-pb.service`. Port 8004. DB Postgres `aict`.
