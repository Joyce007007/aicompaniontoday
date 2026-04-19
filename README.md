# AI Companion Today

Independent editorial guide to AI companion apps across 7 verticals: companion, mental-health, seniors, language, productivity, romance (age-gated), and gaming.

## Stack

- **Frontend**: Astro 5.x SSG (this repo `/src`)
- **CMS admin**: Ghost 6.x at https://aicompaniontoday.com/ghost/
- **Click tracker / API**: FastAPI on port 8004, DB Postgres `aict`
- **Host**: VPS IONOS 88.208.255.123

## Build

```
npm install --legacy-peer-deps
npm run build   # output in dist/
```

## Deploy

```
rsync -av --delete dist/ /var/www/aicompaniontoday.com/
```

## Operations

See [OPERATIONS.md](./OPERATIONS.md) for non-dev operator instructions (how to publish, backup, troubleshoot).
