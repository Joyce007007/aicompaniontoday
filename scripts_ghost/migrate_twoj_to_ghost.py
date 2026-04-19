#!/usr/bin/env python3
"""Migrate existing 2jagency.com HTML articles to Ghost via Admin API.

USAGE:
  1. Log in https://2jagency.com/ghost/
  2. Settings > Integrations > Add custom integration > name "migration"
  3. Copy "Admin API Key" (format id:secret)
  4. Export: GHOST_ADMIN_KEY="id:secret"
  5. Run this script
"""
import os, sys, json, glob, re, time
from pathlib import Path

try:
    import jwt  # pyjwt
    import requests
except ImportError:
    print("pip install pyjwt requests")
    sys.exit(1)

GHOST_URL = "https://2jagency.com"
KEY = os.environ.get("GHOST_ADMIN_KEY", "")
if not KEY or ":" not in KEY:
    print("Set GHOST_ADMIN_KEY=<id>:<secret> env var"); sys.exit(1)

HTML_DIR = "/root/2jagency-site/blog"
MAPPING_JSON = "/root/2jagency-site/go_mapping.json"

def admin_token():
    kid, secret = KEY.split(":")
    payload = {"iat": int(time.time()), "exp": int(time.time()) + 300,
               "aud": "/admin/"}
    return jwt.encode(payload, bytes.fromhex(secret), algorithm="HS256",
                      headers={"kid": kid, "alg": "HS256", "typ": "JWT"})

def api(path, method="GET", json_body=None):
    r = requests.request(method, f"{GHOST_URL}/ghost/api/admin{path}",
                         headers={"Authorization": f"Ghost {admin_token()}",
                                  "Accept-Version": "v6"},
                         json=json_body, timeout=30)
    return r

def html_to_post(html_path):
    """Extract title + body from existing 2jag HTML article."""
    html = Path(html_path).read_text(encoding="utf-8")
    title_m = re.search(r"<title>([^<]+)</title>", html)
    title = title_m.group(1).replace(" &mdash; 2J Agency", "").strip() if title_m else Path(html_path).stem
    desc_m = re.search(r'<meta name="description" content="([^"]+)"', html)
    excerpt = desc_m.group(1)[:300] if desc_m else ""
    # Extract the main article body (heuristic: content between last <h1> and <footer> or </main>)
    body_m = re.search(r"<h1[^>]*>.*?</h1>(.*?)(?=<footer|</main|</section>\s*<footer)", html, flags=re.DOTALL)
    body_html = body_m.group(1).strip() if body_m else "<p>Migrated from legacy HTML.</p>"
    slug = Path(html_path).stem
    return {"title": title, "slug": slug, "excerpt": excerpt, "html": body_html}

def migrate():
    articles = sorted(glob.glob(f"{HTML_DIR}/*.html"))
    articles = [a for a in articles if "index" not in Path(a).name]
    print(f"Found {len(articles)} articles to migrate")
    for art in articles:
        post = html_to_post(art)
        body = {"posts": [{
            "title": post["title"], "slug": post["slug"],
            "html": post["html"], "custom_excerpt": post["excerpt"],
            "status": "published", "tags": [{"name": "review"}, {"name": "migrated-legacy"}]
        }]}
        r = api("/posts/?source=html", "POST", body)
        if r.status_code in (201, 200):
            print(f"  OK {post['slug']}")
        else:
            print(f"  FAIL {post['slug']}: {r.status_code} {r.text[:200]}")
        time.sleep(0.5)

if __name__ == "__main__":
    migrate()
