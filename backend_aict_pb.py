"""aicompaniontoday.com tracking backend.
Endpoints:
 - POST /pv              pageview ping (called from every page via JS beacon)
 - GET  /go              click tracking + affiliate redirect
 - GET/POST /pb          postback receiver (CJ/ClickBank server-to-server conversion notif)
 - POST /api/newsletter  newsletter subscribe
 - GET  /api/stats       admin stats (basic auth)
 - GET  /admin           admin dashboard HTML (basic auth)
 - GET  /api/admin/export/{clicks|conversions|subscribers|pageviews}.csv

Env: AICT_DB, ADMIN_USER, ADMIN_PASS, POSTBACK_SECRET, GO_MAPPING_PATH
"""
import os
import json
import secrets
from html import escape as h
from typing import Optional, List

AICT_PREFIX = "[AICT] "

import asyncpg
from fastapi import FastAPI, Request, Depends, HTTPException, Form
from fastapi.responses import RedirectResponse, PlainTextResponse, HTMLResponse, Response
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, EmailStr
import io
import csv

DB_DSN = os.environ.get("AICT_DB", "postgresql://aict_app:aict_9m8k2jL3pQ5rN@127.0.0.1:5432/aict")
ADMIN_USER = os.environ.get("ADMIN_USER", "joyce")
ADMIN_PASS = os.environ.get("ADMIN_PASS", "change_me")
POSTBACK_SECRET = os.environ.get("POSTBACK_SECRET", "aict_pb_secret_change_me")
GO_MAPPING_PATH = os.environ.get("GO_MAPPING_PATH", "/var/www/aicompaniontoday.com/aict_mapping.json")
BEST_MATRIX_PATH = os.environ.get("BEST_MATRIX_PATH", "/var/www/aicompaniontoday.com/best_offer_matrix.json")

app = FastAPI(title="aict tracking")
security = HTTPBasic()
pool: Optional[asyncpg.Pool] = None
go_mapping_cache = {"mtime": 0.0, "data": {}}
best_matrix_cache = {"mtime": 0.0, "data": {}}


def load_best_matrix():
    try:
        mtime = os.path.getmtime(BEST_MATRIX_PATH)
        if mtime > best_matrix_cache["mtime"]:
            with open(BEST_MATRIX_PATH) as f:
                best_matrix_cache["data"] = json.load(f)
            best_matrix_cache["mtime"] = mtime
    except Exception:
        pass
    return best_matrix_cache["data"]


def pick_best_offer(vertical: str, country: str, is_mobile: bool) -> str:
    matrix = load_best_matrix()
    mapping = load_mapping()
    v_entry = matrix.get(vertical) if vertical else None
    if v_entry:
        by_country = v_entry.get("by_country") or {}
        by_device = v_entry.get("by_device") or {}
        device_key = "mobile" if is_mobile else "desktop"
        offer = by_country.get(country) or by_device.get(device_key) or v_entry.get("default")
        if offer and offer in mapping:
            return offer
    global_default = matrix.get("_global", {}).get("default")
    if global_default and global_default in mapping:
        return global_default
    return next(iter(mapping), "nordvpn")


def check_admin(creds: HTTPBasicCredentials = Depends(security)):
    ok_u = secrets.compare_digest(creds.username, ADMIN_USER)
    ok_p = secrets.compare_digest(creds.password, ADMIN_PASS)
    if not (ok_u and ok_p):
        raise HTTPException(status_code=401, headers={"WWW-Authenticate": "Basic"})
    return creds.username


def load_mapping():
    try:
        mtime = os.path.getmtime(GO_MAPPING_PATH)
        if mtime > go_mapping_cache["mtime"]:
            with open(GO_MAPPING_PATH) as f:
                go_mapping_cache["data"] = json.load(f)
            go_mapping_cache["mtime"] = mtime
    except Exception:
        pass
    return go_mapping_cache["data"]


def get_country(request: Request) -> str:
    cf = request.headers.get("cf-ipcountry", "")
    return (cf or "").upper()[:4] or "XX"


def real_ip(request: Request) -> str:
    xff = request.headers.get("cf-connecting-ip") or request.headers.get("x-real-ip") or ""
    return xff or (request.client.host if request.client else "")


@app.on_event("startup")
async def startup():
    global pool
    pool = await asyncpg.create_pool(DB_DSN, min_size=1, max_size=8)


@app.on_event("shutdown")
async def shutdown():
    if pool:
        await pool.close()


@app.get("/healthz", response_class=PlainTextResponse)
async def healthz():
    return "ok"


class PageviewIn(BaseModel):
    sid: Optional[str] = None
    path: Optional[str] = None
    referrer: Optional[str] = None
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None


@app.post("/pv")
async def pageview(payload: PageviewIn, request: Request):
    sid = (payload.sid or "no_sid")[:200]
    path = (payload.path or "/")[:500]
    referrer = (payload.referrer or "")[:1000]
    ip = real_ip(request)
    country = get_country(request)
    ua = (request.headers.get("user-agent") or "")[:500]
    async with pool.acquire() as con:
        await con.execute(
            """INSERT INTO pageviews (sid, path, referrer, ip, country, user_agent, utm_source, utm_medium, utm_campaign)
               VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)""",
            sid, path, referrer, ip, country, ua, payload.utm_source, payload.utm_medium, payload.utm_campaign,
        )
    return {"ok": True}


@app.api_route("/best", methods=["GET", "HEAD"])
async def best_redirect(request: Request,
                         vertical: str = "",
                         utm_source: str = "",
                         utm_campaign: str = ""):
    if request.method == "HEAD":
        return Response(status_code=200, headers={"X-Robots-Tag": "noindex, nofollow"})
    country = (request.headers.get("cf-ipcountry") or "").upper()[:2]
    ua = request.headers.get("user-agent", "")
    is_mobile = any(m in ua for m in ("Android", "iPhone", "iPad", "Mobile"))
    offer = pick_best_offer(vertical, country, is_mobile)
    sid_parts = ["best", vertical or "all", country or "XX", utm_source or "org"]
    sid = "_".join(p for p in sid_parts if p)[:200]
    target = f"/go?offer={offer}&sid={sid}"
    if utm_campaign:
        target += f"&utm_campaign={utm_campaign}"
    return RedirectResponse(target, status_code=302, headers={"X-Robots-Tag": "noindex, nofollow"})


@app.api_route("/go/{slug}", methods=["GET", "HEAD"])
async def go_slug(request: Request, slug: str, sid: str = "no_sid"):
    return await go_redirect(request=request, offer=slug, sid=sid)


@app.api_route("/go", methods=["GET", "HEAD"])
async def go_redirect(request: Request, offer: str = "", sid: str = "no_sid"):
    if request.method == "HEAD":
        return Response(status_code=200, headers={"X-Robots-Tag": "noindex, nofollow"})
    mapping = load_mapping()
    entry = mapping.get(offer)
    if not entry:
        return RedirectResponse("https://aicompaniontoday.com/", status_code=302)
    target = entry.get("affiliate_url") or entry.get("url") or "https://aicompaniontoday.com/"
    if not target or (isinstance(target, str) and target.startswith("PLACE")):
        target = entry.get("url") or "https://aicompaniontoday.com/"
    ip = real_ip(request)
    country = get_country(request)
    ua = (request.headers.get("user-agent") or "")[:500]
    referrer = (request.headers.get("referer") or "")[:1000]
    qs = dict(request.query_params)
    try:
        async with pool.acquire() as con:
            await con.execute(
                """INSERT INTO clicks (sid, offer, ip, country, user_agent, referrer,
                   utm_source, utm_medium, utm_campaign, target_url)
                   VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)""",
                sid[:200], offer[:64], ip, country, ua, referrer,
                qs.get("utm_source"), qs.get("utm_medium"), qs.get("utm_campaign"),
                target[:2000],
            )
    except Exception:
        pass
    return RedirectResponse(target, status_code=302)


@app.api_route("/pb", methods=["GET", "POST"])
async def postback(request: Request):
    qs = dict(request.query_params)
    sid = (qs.get("sid") or qs.get("aff_sub") or "")[:200]
    provided_secret = qs.get("secret") or ""
    secret_ok = bool(POSTBACK_SECRET) and secrets.compare_digest(provided_secret, POSTBACK_SECRET)
    if not secret_ok:
        if not sid:
            raise HTTPException(status_code=401, detail="missing secret or sid")
        async with pool.acquire() as con:
            exists = await con.fetchval("SELECT 1 FROM clicks WHERE sid=$1 LIMIT 1", sid)
        if not exists:
            raise HTTPException(status_code=403, detail="unknown sid")
    if not sid:
        sid = "no_sid"
    offer = (qs.get("offer") or qs.get("vendor") or "")[:64]
    try:
        payout = float(qs.get("payout") or qs.get("amount") or 0)
    except Exception:
        payout = 0.0
    conv_id = (qs.get("conv_id") or qs.get("cid") or qs.get("hopId") or "")[:128]
    network = "CJ" if qs.get("aff_sub") else ("ClickBank" if qs.get("hopId") else "unknown")
    async with pool.acquire() as con:
        try:
            await con.execute(
                """INSERT INTO conversions (sid, payout, offer, conv_id, network, status, raw)
                   VALUES ($1,$2,$3,$4,$5,'confirmed',$6)
                   ON CONFLICT (conv_id) DO UPDATE SET payout=EXCLUDED.payout, status='confirmed'""",
                sid, payout, offer, conv_id, network, json.dumps(qs),
            )
        except Exception as e:
            return {"ok": False, "error": str(e)[:200]}
    return {"ok": True, "sid": sid, "offer": offer, "payout": payout}


class NewsletterIn(BaseModel):
    email: EmailStr
    source_page: Optional[str] = None


def _client_ip(request: Request) -> str:
    return (request.headers.get("cf-connecting-ip")
            or request.headers.get("x-forwarded-for", "").split(",")[0].strip()
            or (request.client.host if request.client else "unknown"))[:64]


@app.post("/api/newsletter")
async def newsletter_subscribe(payload: NewsletterIn, request: Request):
    ip = _client_ip(request)
    country = get_country(request)
    async with pool.acquire() as con:
        recent = await con.fetchval(
            "SELECT COUNT(*) FROM newsletter_subscribers WHERE ip=$1 AND created_at > NOW() - INTERVAL '1 hour'",
            ip,
        )
        if recent and recent >= 5:
            raise HTTPException(status_code=429, detail="rate limit")
        try:
            await con.execute(
                """INSERT INTO newsletter_subscribers (email, source_page, ip, country) VALUES ($1,$2,$3,$4)
                   ON CONFLICT (email) DO NOTHING""",
                str(payload.email)[:255], (payload.source_page or "")[:200], ip, country,
            )
        except Exception:
            pass
    return {"ok": True}


async def _gather_stats():
    mapping = load_mapping()
    async with pool.acquire() as con:
        pv_today = await con.fetchval("SELECT COUNT(*) FROM pageviews WHERE created_at > NOW() - INTERVAL '1 day'")
        pv_7d = await con.fetchval("SELECT COUNT(*) FROM pageviews WHERE created_at > NOW() - INTERVAL '7 days'")
        clicks_today = await con.fetchval("SELECT COUNT(*) FROM clicks WHERE created_at > NOW() - INTERVAL '1 day'")
        clicks_7d = await con.fetchval("SELECT COUNT(*) FROM clicks WHERE created_at > NOW() - INTERVAL '7 days'")
        conv_today = await con.fetchval("SELECT COUNT(*) FROM conversions WHERE created_at > NOW() - INTERVAL '1 day'")
        conv_total = await con.fetchval("SELECT COUNT(*) FROM conversions")
        revenue_7d = float(await con.fetchval("SELECT COALESCE(SUM(payout),0) FROM conversions WHERE created_at > NOW() - INTERVAL '7 days'") or 0)
        newsletter = await con.fetchval("SELECT COUNT(*) FROM newsletter_subscribers")
        top_offers = await con.fetch(
            """SELECT offer, COUNT(*) AS c FROM clicks
               WHERE created_at > NOW() - INTERVAL '7 days'
               GROUP BY offer ORDER BY c DESC LIMIT 10"""
        )
        top_sources = await con.fetch(
            """SELECT COALESCE(utm_source, 'direct') AS s, COUNT(*) AS c FROM pageviews
               WHERE created_at > NOW() - INTERVAL '7 days'
               GROUP BY s ORDER BY c DESC LIMIT 10"""
        )
        top_countries = await con.fetch(
            """SELECT country, COUNT(*) AS c FROM clicks
               WHERE created_at > NOW() - INTERVAL '7 days'
               GROUP BY country ORDER BY c DESC LIMIT 10"""
        )
    return {
        "pv_today": pv_today, "pv_7d": pv_7d,
        "clicks_today": clicks_today, "clicks_7d": clicks_7d,
        "conv_today": conv_today, "conv_total": conv_total, "revenue_7d": revenue_7d,
        "newsletter": newsletter, "offers_mapped": len(mapping),
        "top_offers": [(r["offer"], r["c"]) for r in top_offers],
        "top_sources": [(r["s"], r["c"]) for r in top_sources],
        "top_countries": [(r["country"], r["c"]) for r in top_countries],
    }


@app.post("/api/contact")
async def api_contact(request: Request):
    form = await request.form()
    email = (form.get("email") or "").strip()[:200]
    subject = (form.get("subject") or "").strip()[:200]
    body_msg = (form.get("body") or "").strip()[:4000]
    honeypot = (form.get("website") or "").strip()
    ip = request.headers.get("cf-connecting-ip") or (request.client.host if request.client else "")
    if honeypot:
        return HTMLResponse("<h1>Thanks</h1><p>Got it.</p>")
    if not email or "@" not in email or not subject or not body_msg:
        raise HTTPException(status_code=400, detail="missing required fields")
    try:
        async with pool.acquire() as con:
            recent = await con.fetchval(
                "SELECT COUNT(*) FROM public.contact_messages WHERE ip=$1 AND created_at > NOW() - INTERVAL '1 hour'",
                ip,
            )
            if recent and recent >= 5:
                raise HTTPException(status_code=429, detail="rate limit")
            await con.execute(
                "INSERT INTO public.contact_messages (email, subject, body, ip) VALUES ($1, $2, $3, $4)",
                email, subject, body_msg, ip,
            )
    except HTTPException:
        raise
    except Exception as e:
        print(f"contact insert err: {e}")
        raise HTTPException(status_code=500, detail="internal error")
    return HTMLResponse("<!doctype html><meta charset=utf-8><title>Message sent</title><body style='font-family:system-ui;max-width:600px;margin:80px auto;padding:0 20px'><h1>Thanks!</h1><p>We received your message and will reply to the email you provided.</p><p><a href='/'>&larr; Back to AI Companion Today</a></p></body>")


@app.get("/review/{slug}", response_class=HTMLResponse)
async def review_prelander(slug: str):
    import re as _re
    if not _re.match(r"^[a-z0-9]{2,30}$", slug):
        raise HTTPException(status_code=404, detail="invalid slug")
    async with pool.acquire() as con:
        row = await con.fetchrow(
            "SELECT html FROM public.review_cache WHERE slug=$1", slug
        )
    if row and row["html"]:
        return HTMLResponse(row["html"])
    # Fallback: minimal placeholder redirecting to /go/ — do not generate AI content
    import json as _json
    try:
        with open("/var/www/aicompaniontoday.com/aict_mapping.json", encoding="utf-8") as f:
            mp = _json.load(f)
    except Exception:
        mp = {}
    entry = mp.get(slug)
    if not entry:
        raise HTTPException(status_code=404, detail="offer not found")
    name = entry.get("name") or slug
    return HTMLResponse(
        f'<!doctype html><meta charset=utf-8><title>{name} - AI Companion Today</title>'
        f'<meta name="robots" content="noindex">'
        f'<body style="font-family:system-ui;max-width:600px;margin:80px auto;padding:0 20px;text-align:center">'
        f'<h1>{name}</h1>'
        f'<p>News refresh in progress. Get the current deal:</p>'
        f'<p><a href="/go/{slug}" rel="sponsored nofollow" '
        f'style="display:inline-block;background:#ff6b35;color:#fff;padding:14px 30px;'
        f'border-radius:8px;font-weight:700;text-decoration:none">Get {name} deal &rarr;</a></p>'
        f'<p style="margin-top:30px;font-size:0.85em;color:#888"><a href="/">Back to AI Companion Today</a></p>'
        f'</body>'
    )


def _render_review_page(slug: str, entry: dict) -> str:
    import json as _json
    import datetime as _dt
    name = entry.get("name") or slug
    vertical = entry.get("vertical") or ""
    network = entry.get("network") or ""
    merchant_url = entry.get("url") or ""
    vert_label = _VERT_LABELS.get(vertical, vertical.title() or "Partner")
    intro = f"{name} is listed on aicompaniontoday.com under the {vert_label} category. It is a {network}-tracked affiliate partner we have verified as actively redirecting visitors to the vendor sales page with commission tracking intact."
    methodology = "We list a partner only after verifying the tracking link returns a working redirect to the vendor, and the vendor's public page is accessible. We do not publish fabricated ratings or testimonials; when we cite a rating, we cite the source."
    what_to_check = [
        f"Go to the vendor's page ({merchant_url or 'linked below'}) and read the feature list before committing.",
        "Check the refund or money-back policy on the vendor's own page (ClickBank products have a 60-day refund; CJ partners vary).",
        "Verify current pricing - promotional pricing changes frequently.",
        "Look up the vendor on Trustpilot or App Store to see independent review volume.",
    ]
    faq = [
        ("Is this an affiliate link?", "Yes. aicompaniontoday.com earns a commission if you buy or sign up via our tracking link, at no extra cost to you. See our <a href=\"/disclosure\">Affiliate Disclosure</a>."),
        ("How do I get the actual deal?", f"Click the CTA below. You will be redirected to the current {name} vendor page with our tracking parameters attached."),
        ("Who writes these reviews?", "Reviews are published under the editorial byline <a href=\"/about#editorial\">The AICT Editorial Team</a>, which is the editorial pen name used by the AI Companion Today team."),
    ]
    what_to_check_html = "".join(f"<li>{item}</li>" for item in what_to_check)
    faq_html = "".join(f"<details style='margin:8px 0;padding:10px 14px;background:#f8f9fa;border-radius:6px'><summary style='cursor:pointer;font-weight:600'>{q}</summary><div style='margin-top:8px;color:#444'>{a}</div></details>" for q, a in faq)
    cta_url = f"/go/{slug}"
    today = _dt.datetime.utcnow().strftime("%Y-%m-%d")
    today_human = _dt.datetime.utcnow().strftime("%B %d, %Y")
    schemas = [
        {
            "@context": "https://schema.org",
            "@type": "Review",
            "itemReviewed": {"@type": "Product", "name": name},
            "author": {"@id": "https://aicompaniontoday.com/about#editorial"},
            "datePublished": today,
            "reviewBody": intro,
            "url": f"https://aicompaniontoday.com/review/{slug}",
        },
        {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq],
        },
    ]
    schema_tags = "".join(f'<script type="application/ld+json">{_json.dumps(sc, ensure_ascii=False)}</script>' for sc in schemas)
    css = "body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;color:#1a1a2e;line-height:1.65;margin:0;background:#fafbff}.wrap{max-width:780px;margin:40px auto;padding:0 24px}h1{font-size:1.9em;margin-bottom:10px;letter-spacing:-0.5px}h2{font-size:1.25em;margin:30px 0 10px;color:#2d1b69}.tag{display:inline-block;background:#ff6b35;color:#fff;padding:3px 10px;border-radius:20px;font-size:0.8em;font-weight:600;letter-spacing:0.3px}.badge{display:flex;align-items:center;gap:12px;padding:14px 18px;background:#fff;border-left:3px solid #2d1b69;margin:20px 0;border-radius:6px;box-shadow:0 1px 3px rgba(0,0,0,0.05)}.avatar{display:inline-block;width:38px;height:38px;border-radius:50%;background:#2d1b69;color:#fff;text-align:center;line-height:38px;font-weight:700;font-size:0.9em}.disclosure{font-size:0.85em;color:#666;background:#fff;padding:12px 16px;border-radius:6px;margin:18px 0;border-left:3px solid #ffd166}.cta-wrap{margin:28px 0;text-align:center}.cta{display:inline-block;background:#ff6b35;color:#fff;padding:18px 38px;border-radius:8px;font-weight:700;font-size:1.1em;text-decoration:none;box-shadow:0 4px 14px rgba(255,107,53,0.35)}.cta:hover{transform:translateY(-2px);box-shadow:0 8px 22px rgba(255,107,53,0.5);text-decoration:none}ul{padding-left:22px}li{margin:8px 0}.back{margin-top:30px;color:#666;font-size:0.9em}.back a{color:#2d1b69;text-decoration:none}"
    return (
        '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        + f'<title>{name} Review - AI Companion Today</title>\n'
        + f'<meta name="description" content="Independent take on {name} - what it is, who it is for, and how to check the offer before you buy.">\n'
        + '<meta name="robots" content="index,follow">\n'
        + f'<link rel="canonical" href="https://aicompaniontoday.com/review/{slug}">\n'
        + schema_tags + '\n'
        + f'<style>{css}</style>\n'
        + '</head>\n<body>\n<section class="wrap">\n'
        + f'<span class="tag">{vert_label}</span>\n'
        + f'<h1>{name} - Independent Review & Deal Check</h1>\n'
        + '<div class="badge">\n<span class="avatar">CB</span>\n'
        + f'<span>Reviewed by <a href="/about#editorial" style="color:#2d1b69;font-weight:600">The AICT Editorial Team</a> &middot; {today_human}</span>\n'
        + '</div>\n'
        + f'<p style="font-size:1.05em">{intro}</p>\n'
        + '<div class="disclosure">This page contains a tracked affiliate link. If you click through and complete a purchase, AI Companion Today may earn a commission at no extra cost to you. See our <a href="/disclosure">Affiliate Disclosure</a>.</div>\n'
        + f'<h2>How we pick partners</h2>\n<p>{methodology}</p>\n'
        + '<h2>Before you click through</h2>\n<ul>\n' + what_to_check_html + '\n</ul>\n'
        + '<div class="cta-wrap">\n'
        + f'<a class="cta" href="{cta_url}" rel="sponsored nofollow noopener">Get {name} deal &rarr;</a>\n'
        + '</div>\n'
        + '<h2>FAQ</h2>\n' + faq_html + '\n'
        + '<p class="back"><a href="/">&larr; Back to AI Companion Today</a></p>\n'
        + '<div id="google_translate_element" style="display:none"></div>\n<script>function googleTranslateElementInit(){new google.translate.TranslateElement({pageLanguage:"en",layout:google.translate.TranslateElement.InlineLayout.SIMPLE,autoDisplay:false},"google_translate_element");setTimeout(function(){try{var lang=(navigator.language||navigator.userLanguage||"en").toLowerCase().split("-")[0];var supp=["es","de","fr","it","pt","nl","pl","ru","tr","zh","ja","ko","ar","hi","id","sv","cs","ro"];if(lang!=="en"&&supp.indexOf(lang)>-1){var sel=document.querySelector(".goog-te-combo");if(sel){sel.value=lang;sel.dispatchEvent(new Event("change"));}}}catch(e){}},1200);}</script>\n<script src="//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit" async defer></script>\n<style>.goog-te-banner-frame,.skiptranslate{display:none!important}body{top:0!important}</style>\n</section>\n</body>\n</html>'
    )


@app.get("/api/stats")
async def api_stats(_: str = Depends(check_admin)):
    s = await _gather_stats()
    return {
        "pageviews": {"today": s["pv_today"], "7d": s["pv_7d"]},
        "clicks": {"today": s["clicks_today"], "7d": s["clicks_7d"]},
        "conversions": {"today": s["conv_today"], "total": s["conv_total"], "revenue_7d": s["revenue_7d"]},
        "newsletter_subscribers": s["newsletter"],
        "offers_mapped": s["offers_mapped"],
        "top_offers_7d": [{"offer": o, "clicks": c} for o, c in s["top_offers"]],
        "top_sources_7d": [{"source": o, "views": c} for o, c in s["top_sources"]],
        "top_countries_7d": [{"country": o, "clicks": c} for o, c in s["top_countries"]],
    }


def _rows_html(rows: List, headers: List[str]) -> str:
    if not rows:
        return '<p style="color:#999;font-style:italic">No data yet.</p>'
    thead = "".join(f"<th>{h(x)}</th>" for x in headers)
    body = "".join(
        "<tr>" + "".join(f"<td>{h(str(c))}</td>" for c in row) + "</tr>"
        for row in rows
    )
    return f'<table><thead><tr>{thead}</tr></thead><tbody>{body}</tbody></table>'


@app.get("/admin", response_class=HTMLResponse)
@app.get("/admin/", response_class=HTMLResponse)
async def admin_dashboard(_: str = Depends(check_admin)):
    s = await _gather_stats()
    fmt = lambda n: "-" if n is None else f"{n:,}".replace(",", " ")
    top_offers = _rows_html(s["top_offers"], ["Offer", "Clicks"])
    top_sources = _rows_html(s["top_sources"], ["Source", "Views"])
    top_countries = _rows_html([(c or "-", n) for c, n in s["top_countries"]], ["Country", "Clicks"])

    html_doc = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<title>AICT Admin</title><style>
*{{box-sizing:border-box;font-family:-apple-system,Segoe UI,Roboto,sans-serif}}
body{{margin:0;background:#f5f7fa;color:#1a1a2e}}
header{{background:linear-gradient(135deg,#0a1628,#2d1b69);color:#fff;padding:20px}}
header h1{{margin:0;font-size:1.4em}}
.wrap{{max-width:1200px;margin:20px auto;padding:0 20px}}
.row{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px;margin-bottom:20px}}
.card{{background:#fff;border-radius:12px;padding:20px;box-shadow:0 2px 10px rgba(0,0,0,0.04)}}
.card .label{{font-size:0.82em;color:#777;text-transform:uppercase;letter-spacing:0.5px}}
.card .val{{font-size:2em;font-weight:700;color:#2d1b69;margin-top:6px}}
.card .sub{{font-size:0.82em;color:#999;margin-top:4px}}
.section{{background:#fff;border-radius:12px;padding:22px;margin-bottom:18px;box-shadow:0 2px 10px rgba(0,0,0,0.04)}}
.section h2{{margin-top:0;color:#333;font-size:1.1em}}
table{{width:100%;border-collapse:collapse;font-size:0.92em}}
th{{text-align:left;color:#666;font-weight:600;padding:8px 4px;border-bottom:1px solid #eee}}
td{{padding:10px 4px;border-bottom:1px solid #f5f5f5}}
.exports{{display:flex;gap:10px;flex-wrap:wrap}}
.exports a{{padding:8px 16px;background:#2d1b69;color:#fff;border-radius:6px;text-decoration:none;font-size:0.88em}}
</style></head><body>
<header><h1>AI Companion Today &middot; Admin Dashboard</h1></header>
<div class="wrap">
<div class="row">
<div class="card"><div class="label">Pageviews Today</div><div class="val">{fmt(s["pv_today"])}</div><div class="sub">{fmt(s["pv_7d"])} last 7d</div></div>
<div class="card"><div class="label">Clicks Today</div><div class="val">{fmt(s["clicks_today"])}</div><div class="sub">{fmt(s["clicks_7d"])} last 7d</div></div>
<div class="card"><div class="label">Conversions</div><div class="val">{fmt(s["conv_today"])}</div><div class="sub">{fmt(s["conv_total"])} all time</div></div>
<div class="card"><div class="label">Revenue 7d</div><div class="val">${s["revenue_7d"]:.2f}</div><div class="sub">verified payouts</div></div>
<div class="card"><div class="label">Newsletter</div><div class="val">{fmt(s["newsletter"])}</div><div class="sub">subscribers</div></div>
<div class="card"><div class="label">Offers Mapped</div><div class="val">{fmt(s["offers_mapped"])}</div><div class="sub">in /go router</div></div>
</div>
<div class="section"><h2>Top Offers (clicks, 7 days)</h2>{top_offers}</div>
<div class="section"><h2>Traffic Sources (pageviews, 7 days)</h2>{top_sources}</div>
<div class="section"><h2>Top Click Countries (7 days)</h2>{top_countries}</div>
<div class="section"><h2>Exports (CSV)</h2>
<div class="exports">
<a href="/api/admin/export/clicks.csv">Clicks</a>
<a href="/api/admin/export/conversions.csv">Conversions</a>
<a href="/api/admin/export/subscribers.csv">Newsletter</a>
<a href="/api/admin/export/pageviews.csv">Pageviews</a>
</div>
</div>
</div></body></html>"""
    return HTMLResponse(html_doc)


def _rows_to_csv(rows, fieldnames):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fieldnames)
    w.writeheader()
    for r in rows:
        w.writerow({k: ("" if r[k] is None else r[k]) for k in fieldnames})
    buf.seek(0)
    return buf.getvalue()



@app.get("/admin/cro", response_class=HTMLResponse)
@app.get("/admin/cro/", response_class=HTMLResponse)
async def cro_dashboard(_: str = Depends(check_admin)):
    async with pool.acquire() as con:
        pv_7d = await con.fetchval("SELECT COUNT(*) FROM pageviews WHERE created_at > NOW() - INTERVAL '7 days'") or 0
        clicks_7d = await con.fetchval("SELECT COUNT(*) FROM clicks WHERE created_at > NOW() - INTERVAL '7 days'") or 0
        by_offer = await con.fetch(
            """SELECT offer, COUNT(*) AS c FROM clicks
               WHERE created_at > NOW() - INTERVAL '7 days'
               GROUP BY offer ORDER BY c DESC LIMIT 20"""
        )
        by_sid = await con.fetch(
            """SELECT sid, COUNT(*) AS c FROM clicks
               WHERE created_at > NOW() - INTERVAL '7 days' AND sid != 'no_sid'
               GROUP BY sid ORDER BY c DESC LIMIT 20"""
        )
        best_clicks = await con.fetch(
            """SELECT sid, COUNT(*) AS c FROM clicks
               WHERE created_at > NOW() - INTERVAL '7 days' AND sid LIKE 'best_%'
               GROUP BY sid ORDER BY c DESC LIMIT 15"""
        )
        by_country = await con.fetch(
            """SELECT COALESCE(country,'??') AS country, COUNT(*) AS c FROM clicks
               WHERE created_at > NOW() - INTERVAL '7 days'
               GROUP BY country ORDER BY c DESC LIMIT 15"""
        )
    ctr = f"{(clicks_7d / pv_7d * 100):.2f}%" if pv_7d else "-"

    def table_(rows, col1, col2):
        if not rows:
            return "<p><em>no data</em></p>"
        html = f"<table><tr><th>{col1}</th><th>{col2}</th></tr>"
        for r in rows:
            html += f"<tr><td>{h(str(r[0]))}</td><td>{r[1]}</td></tr>"
        html += "</table>"
        return html

    html_doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>CRO Dashboard</title>
<style>
body{{font-family:system-ui,sans-serif;background:#0a1628;color:#e8e8ea;margin:0;padding:30px}}
h1{{font-size:1.8em;margin-bottom:6px}}
.kpis{{display:flex;gap:16px;flex-wrap:wrap;margin:22px 0}}
.kpi{{background:#14233d;padding:18px 22px;border-radius:10px;min-width:160px}}
.kpi .v{{font-size:2em;font-weight:700;color:#ff6b35}}
.kpi .l{{color:#aaa;font-size:0.85em;margin-top:4px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:18px}}
.panel{{background:#14233d;padding:18px;border-radius:10px}}
.panel h2{{font-size:1.1em;margin-bottom:12px;color:#ff6b35}}
table{{width:100%;border-collapse:collapse;font-size:0.9em}}
th,td{{padding:6px 8px;border-bottom:1px solid #223855;text-align:left}}
th{{color:#aaa;font-weight:600}}
a{{color:#ec4899}}
</style></head><body>
<h1>CRO Dashboard &mdash; 7 days</h1>
<p><a href="/admin">&larr; Main admin</a></p>
<div class="kpis">
  <div class="kpi"><div class="v">{pv_7d:,}</div><div class="l">Pageviews (7d)</div></div>
  <div class="kpi"><div class="v">{clicks_7d:,}</div><div class="l">Affiliate clicks (7d)</div></div>
  <div class="kpi"><div class="v">{ctr}</div><div class="l">CTR (7d)</div></div>
</div>
<div class="grid">
  <div class="panel"><h2>Clicks by offer</h2>{table_(by_offer, "Offer", "Clicks")}</div>
  <div class="panel"><h2>Clicks by SID (position)</h2>{table_(by_sid, "SID", "Clicks")}</div>
  <div class="panel"><h2>SMART /best routing</h2>{table_(best_clicks, "Best SID", "Clicks")}</div>
  <div class="panel"><h2>Clicks by country</h2>{table_(by_country, "Country", "Clicks")}</div>
</div>
</body></html>"""
    return HTMLResponse(html_doc)

@app.get('/admin/offer-queue', response_class=HTMLResponse)
@app.get('/admin/offer-queue/', response_class=HTMLResponse)
async def offer_queue(_: str = Depends(check_admin)):
    async with pool.acquire() as con:
        rows = await con.fetch("""
            SELECT id, network, vendor, name, category, hoplink, status, fetched_at
            FROM public.offer_candidates
            ORDER BY (status='pending_review') DESC, fetched_at DESC
            LIMIT 300
        """)
    body = []
    body.append('<table style="width:100%;border-collapse:collapse;background:#14233d">')
    body.append('<tr><th>ID</th><th>Network</th><th>Vendor</th><th>Name</th><th>Category</th><th>Hoplink</th><th>Status</th><th>Actions</th></tr>')
    for r in rows:
        colors = {'pending_review':'#ff6b35','approved':'#49c5b1','rejected':'#888','deferred':'#aaa'}
        sc = colors.get(r['status'], '#aaa')
        actions = ''
        if r['status'] == 'pending_review':
            actions = (
                '<form method=post action=/admin/offer-queue/action style="display:inline">'
                '<input type=hidden name=id value="' + str(r['id']) + '">'
                '<button name=action value=approve style="background:#49c5b1;color:#fff;border:0;padding:6px 12px;border-radius:4px;cursor:pointer;margin-right:4px">Approve</button>'
                '<button name=action value=reject style="background:#888;color:#fff;border:0;padding:6px 12px;border-radius:4px;cursor:pointer">Reject</button>'
                '</form>'
            )
        hoplink = (r['hoplink'] or '')[:70]
        body.append(
            '<tr style="border-bottom:1px solid #223855">'
            '<td style="padding:8px">' + str(r['id']) + '</td>'
            '<td>' + h(r['network']) + '</td>'
            '<td style="font-family:monospace;font-size:0.85em">' + h(r['vendor']) + '</td>'
            '<td><strong>' + h(r['name'] or '') + '</strong></td>'
            '<td style="font-size:0.85em">' + h(r['category'] or '') + '</td>'
            '<td style="font-size:0.75em"><a href="' + h(r['hoplink'] or '') + '" target=_blank style="color:#ec4899">' + h(hoplink) + '...</a></td>'
            '<td><span style="color:' + sc + ';font-weight:600">' + r['status'] + '</span></td>'
            '<td>' + actions + '</td>'
            '</tr>'
        )
    body.append('</table>')
    html_doc = (
        '<!doctype html><html><head><meta charset=utf-8><title>Offer Queue</title>'
        '<style>body{font-family:system-ui,sans-serif;background:#0a1628;color:#e8e8ea;margin:0;padding:30px}'
        'h1{font-size:1.8em;color:#fff}th,td{padding:10px;text-align:left;vertical-align:top}'
        'th{background:#0a1628;color:#aaa;font-size:0.85em;font-weight:600}a{color:#ec4899}</style></head><body>'
        '<h1>Offer Queue</h1><p><a href=/admin>Main admin</a> &middot; Total: ' + str(len(rows)) + ' candidates</p>'
        + ''.join(body) +
        '</body></html>'
    )
    return HTMLResponse(html_doc)


CJ_DEV_KEY = os.environ.get("CJ_DEV_KEY", "BAYbixqH1JcYG1Vz6_l7LUpaxw")
CJ_PID = "101714924"
GO_MAPPING_PATH = "/var/www/aicompaniontoday.com/aict_mapping.json"
BUILD_SCRIPT = "/root/build_aict_v1.py"

CATEGORY_TO_VERTICAL_AR = {
    "VPN": "vpn-security", "Cybersecurity": "vpn-security", "Privacy": "vpn-security",
    "Computer SW": "saas", "Software": "saas", "Email Marketing": "saas", "CRM": "saas",
    "Weight": "health-weight", "Diet": "health-weight", "Dietary": "health-weight",
    "Dental": "health-dental", "Mens Health": "mens-wellness", "Men's Health": "mens-wellness",
    "Hearing": "hearing-health",
    "Department Stores": "ecommerce", "Virtual Malls": "ecommerce", "E-commerce": "ecommerce",
    "Fashion": "ecommerce", "Jewelry": "ecommerce", "Eyewear": "ecommerce",
    "Sunglasses": "ecommerce", "Toys": "ecommerce",
    "Garden": "home-garden", "Home": "home-garden",
}


def _map_vert(cj_cat):
    s = (cj_cat or "").lower()
    for k, v in CATEGORY_TO_VERTICAL_AR.items():
        if k.lower() in s: return v
    return "saas"


def _slug_from_name(name):
    import re as _re
    s = _re.sub(r"[^a-z0-9]+", "", (name or "").lower())
    return s[:20] or "merchant"


def _fetch_cj_click_url(adv_id: str):
    import requests as _req, xml.etree.ElementTree as _ET
    try:
        r = _req.get(
            "https://linksearch.api.cj.com/v3/link-search",
            params={"website-id": CJ_PID, "advertiser-ids": str(adv_id), "records-per-page": 20},
            headers={"Authorization": f"Bearer {CJ_DEV_KEY}"}, timeout=15
        )
        if r.status_code != 200: return None, None
        root = _ET.fromstring(r.text)
        best_click, best_dest = None, None
        for link in root.iter():
            if not link.tag.endswith("link"): continue
            click = (link.findtext("clickUrl") or "").strip()
            dest = (link.findtext("destination") or "").strip()
            lt = (link.findtext("link-type") or "").strip()
            if not click: continue
            if best_click is None:
                best_click, best_dest = click, dest
            if lt == "Text Link":
                return click, dest
        return best_click, best_dest
    except Exception as e:
        print(f"fetch_cj_click_url err: {e}"); return None, None


def _add_to_go_mapping(slug, name, vertical, merchant_url, affiliate_url, network):
    import json as _json, os as _os
    with open(GO_MAPPING_PATH, encoding="utf-8") as f:
        mp = _json.load(f)
    if slug in mp:
        return False
    mp[slug] = {
        "name": name, "vertical": vertical,
        "url": merchant_url or f"https://{slug}.com",
        "affiliate_url": affiliate_url, "network": network,
    }
    tmp = GO_MAPPING_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        lines = ["{"]
        items = list(mp.items())
        for i, (k, v) in enumerate(items):
            comma = "," if i < len(items) - 1 else ""
            lines.append('  "' + k + '": ' + _json.dumps(v, ensure_ascii=False) + comma)
        lines.append("}")
        f.write(chr(10).join(lines) + chr(10))
    _os.rename(tmp, GO_MAPPING_PATH)
    return True


def _rebuild_site():
    import subprocess as _sp
    try:
        _sp.run(["python3", BUILD_SCRIPT], capture_output=True, text=True, timeout=90)
    except Exception as e:
        print(f"rebuild err: {e}")


def _notify_ntfy(msg, title="2JAGENCY approve"):
    import requests as _req
    try:
        _req.post("https://ntfy.sh/operateur30-aict-alerts",
                  data=msg, headers={"Title": title, "Tags": "moneybag"}, timeout=5)
    except Exception: pass


@app.post('/admin/offer-queue/action')
async def offer_queue_action(action: str = Form(...), id: int = Form(...), _: str = Depends(check_admin)):
    if action not in ('approve', 'reject', 'defer'):
        raise HTTPException(status_code=400, detail='invalid action')
    new_status = {'approve':'approved','reject':'rejected','defer':'deferred'}[action]
    row = None
    async with pool.acquire() as con:
        await con.execute(
            'UPDATE public.offer_candidates SET status=$1, reviewed_at=NOW(), reviewed_by=$2 WHERE id=$3',
            new_status, 'joyce', id,
        )
        if action == 'approve':
            row = await con.fetchrow(
                'SELECT network, vendor, name, category, hoplink FROM public.offer_candidates WHERE id=$1', id
            )
    if action == 'approve' and row:
        slug = _slug_from_name(row['name'])
        network = row['network']
        name = row['name']
        category = row['category'] or ''
        vertical = _map_vert(category)
        merchant_url = ''
        affiliate_url = row['hoplink'] or ''
        if network == 'CJ':
            click, dest = _fetch_cj_click_url(row['vendor'])
            if click:
                affiliate_url = click
                merchant_url = dest or ''
        elif network == 'ClickBank':
            affiliate_url = f"https://hop.clickbank.net/?affiliate=agent2j&vendor={row['vendor']}"
        if affiliate_url:
            added = _add_to_go_mapping(slug, name, vertical, merchant_url, affiliate_url, network)
            if added:
                _rebuild_site()
                # Queue Pinterest pin
                try:
                    async with pool.acquire() as pc:
                        await pc.execute('''
                            INSERT INTO public.pinterest_queue (offer_slug, title, description, target_url, image_url, status)
                            VALUES ($1, $2, $3, $4, $5, 'pending')
                        ''',
                        slug,
                        (name + ' | Verified Affiliate Partner')[:100],
                        f"Discover {name} with our comparison at aicompaniontoday.com - verified affiliate partnership.",
                        f"https://aicompaniontoday.com/go/{slug}",
                        f"https://aicompaniontoday.com/images/{vertical}.webp"
                        )
                except Exception as _pe:
                    print(f"pinterest queue err: {_pe}")
                _notify_ntfy(f"Approved: {name} ({slug}) added to go_mapping and site rebuilt")
    return RedirectResponse('/admin/offer-queue/', status_code=303)



@app.get("/api/admin/export/clicks.csv")
async def export_clicks(_: str = Depends(check_admin)):
    async with pool.acquire() as con:
        rows = await con.fetch("SELECT id, sid, offer, ip, country, utm_source, utm_medium, utm_campaign, referrer, target_url, created_at FROM clicks ORDER BY id DESC LIMIT 10000")
    data = _rows_to_csv(rows, ["id","sid","offer","ip","country","utm_source","utm_medium","utm_campaign","referrer","target_url","created_at"])
    return Response(data, media_type="text/csv", headers={"Content-Disposition": 'attachment; filename="clicks.csv"'})


@app.get("/api/admin/export/conversions.csv")
async def export_conversions(_: str = Depends(check_admin)):
    async with pool.acquire() as con:
        rows = await con.fetch("SELECT id, sid, offer, network, payout, conv_id, status, created_at FROM conversions ORDER BY id DESC LIMIT 10000")
    data = _rows_to_csv(rows, ["id","sid","offer","network","payout","conv_id","status","created_at"])
    return Response(data, media_type="text/csv", headers={"Content-Disposition": 'attachment; filename="conversions.csv"'})


@app.get("/api/admin/export/subscribers.csv")
async def export_subs(_: str = Depends(check_admin)):
    async with pool.acquire() as con:
        rows = await con.fetch("SELECT id, email, source_page, confirmed, created_at FROM newsletter_subscribers ORDER BY id DESC LIMIT 10000")
    data = _rows_to_csv(rows, ["id","email","source_page","confirmed","created_at"])
    return Response(data, media_type="text/csv", headers={"Content-Disposition": 'attachment; filename="subscribers.csv"'})


@app.get("/api/admin/export/pageviews.csv")
async def export_pageviews(_: str = Depends(check_admin)):
    async with pool.acquire() as con:
        rows = await con.fetch("SELECT id, sid, path, referrer, country, utm_source, utm_medium, utm_campaign, created_at FROM pageviews ORDER BY id DESC LIMIT 10000")
    data = _rows_to_csv(rows, ["id","sid","path","referrer","country","utm_source","utm_medium","utm_campaign","created_at"])
    return Response(data, media_type="text/csv", headers={"Content-Disposition": 'attachment; filename="pageviews.csv"'})
