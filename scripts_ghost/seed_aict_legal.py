#!/usr/bin/env python3
"""Seed AICT legal pages via Ghost Admin API (as Pages, not Posts)."""
import os, sys, time
import jwt, requests

GHOST_URL = "https://aicompaniontoday.com"
KEY = os.environ.get("GHOST_ADMIN_KEY_AICT", "")
if not KEY: sys.exit("Set GHOST_ADMIN_KEY_AICT")

def tok():
    kid, s = KEY.split(":")
    p = {"iat": int(time.time()), "exp": int(time.time())+300, "aud":"/admin/"}
    return jwt.encode(p, bytes.fromhex(s), algorithm="HS256", headers={"kid":kid,"alg":"HS256","typ":"JWT"})

def page(title, slug, html):
    body = {"pages":[{"title":title,"slug":slug,"html":html,"status":"published"}]}
    r = requests.post(f"{GHOST_URL}/ghost/api/admin/pages/?source=html",
                      headers={"Authorization":f"Ghost {tok()}","Accept-Version":"v6"},
                      json=body, timeout=30)
    print(f"  {r.status_code} {slug}")

PAGES = [
    ("About", "about",
     """<h1>About AI Companion Today</h1>
     <p>AI Companion Today is an independent editorial guide to AI companion apps across 7 verticals: companion, mental health, seniors, language, productivity, romance and gaming.</p>
     <h2>Our editorial team</h2>
     <p>Reviews and guides are published under the byline <strong>The AICT Editorial Team</strong> — a collective editorial voice. We do not assign individual author attribution.</p>
     <h2>How we make money</h2>
     <p>Affiliate commissions paid by partner platforms when a visitor subscribes via our tracked links. Commissions never influence rankings. See <a href="/advertising-disclosure">disclosure</a>.</p>"""),

    ("Methodology", "methodology",
     """<h1>Methodology</h1>
     <p>How we test and rank AI companion apps.</p>
     <h2>Our 6 pillars</h2>
     <ol>
     <li><strong>Hands-on testing 14-30 days</strong> — each app is tested daily by our team for 2-4 weeks before upgrade from "guide" to "review"</li>
     <li><strong>Standardised scoring</strong> — 12-criteria grid covering conversation, memory, pricing, safety, privacy, voice, image gen, free tier, support, app quality, UX, editor's choice</li>
     <li><strong>Privacy and safety audit</strong> — terms of service, data retention, HIPAA status for YMYL apps</li>
     <li><strong>Real-money spend</strong> — we pay for each app at the tier we recommend</li>
     <li><strong>Monthly re-test</strong> — top picks re-tested monthly to catch regressions</li>
     <li><strong>Transparent affiliate</strong> — full disclosure; rankings are independent of commission size</li>
     </ol>"""),

    ("Advertising Disclosure", "advertising-disclosure",
     """<h1>Advertising Disclosure</h1>
     <p>Last updated: April 2026</p>
     <p>Some links on AI Companion Today are affiliate links. When you sign up for a service via one of our tracked links, we may earn a commission at no additional cost to you.</p>
     <h2>Networks we use</h2>
     <p>Commission Junction, Impact, CrakRevenue (age-gated section only), FirstPromoter, direct programs.</p>
     <h2>Editorial independence</h2>
     <p>Commissions never influence our rankings. FTC 16 CFR Part 255 compliant.</p>"""),

    ("Privacy Policy", "privacy",
     """<h1>Privacy Policy</h1>
     <p>Last updated: April 2026</p>
     <h2>Data we collect</h2>
     <p>Pageviews (anonymous), newsletter subscribers (email only), comments (optional name/email).</p>
     <h2>Your rights (GDPR)</h2>
     <p>Access, rectification, erasure, portability. Contact privacy@aicompaniontoday.com.</p>
     <h2>Cookies</h2>
     <p>Strictly necessary (session), analytics (optional consent).</p>"""),

    ("Terms of Service", "terms",
     """<h1>Terms of Service</h1>
     <p>Editorial content provided as-is. Affiliate links clearly disclosed. Use at your own discretion.</p>"""),

    ("Contact", "contact",
     """<h1>Contact Us</h1>
     <p>Email: contact@aicompaniontoday.com</p>
     <p>Press: press@aicompaniontoday.com</p>
     <p>Editorial feedback and factual corrections welcomed.</p>"""),

    ("Mental Health Disclaimer", "disclaimer-mental-health",
     """<div style="padding:20px;background:#fee;border:2px solid #dc2626;border-radius:8px">
     <h2 style="margin-top:0;color:#dc2626">In crisis? Get help now.</h2>
     <p><strong>United States:</strong> Call or text <a href="tel:988">988</a> (Suicide & Crisis Lifeline).</p>
     <p><strong>France:</strong> Call <a href="tel:3114">3114</a> (24/7 free national prevention line).</p>
     <p><strong>UK:</strong> Samaritans <a href="tel:116123">116 123</a>.</p>
     </div>
     <h1>Mental Health Content Disclaimer</h1>
     <p><strong>This content is for informational purposes only and does not constitute medical or psychiatric advice.</strong> AI chatbots are not substitutes for licensed mental health professionals.</p>
     <p>If you are experiencing a mental health crisis, please contact emergency services or a crisis helpline immediately.</p>
     <p>Our AI mental-health content is reviewed for general accuracy but does not replace personalised clinical consultation. Consult a licensed mental health professional for diagnosis or treatment.</p>"""),
]

for p in PAGES:
    page(*p); time.sleep(0.5)
print("Legal pages created as published Ghost Pages")
