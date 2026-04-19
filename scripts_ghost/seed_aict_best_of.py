#!/usr/bin/env python3
"""Seed AICT Ghost with 5 best-of + 5 comparatifs (EN + FR) via Admin API.

USAGE:
  1. Log in https://aicompaniontoday.com/ghost/
  2. Settings > Integrations > Add custom > "seed"
  3. Copy Admin API Key
  4. Export: GHOST_ADMIN_KEY_AICT="id:secret"
  5. Run this script
"""
import os, sys, time
try:
    import jwt, requests
except ImportError:
    print("pip install pyjwt requests"); sys.exit(1)

GHOST_URL = "https://aicompaniontoday.com"
KEY = os.environ.get("GHOST_ADMIN_KEY_AICT", "")
if not KEY or ":" not in KEY:
    print("Set GHOST_ADMIN_KEY_AICT=<id>:<secret>"); sys.exit(1)

def tok():
    kid, s = KEY.split(":")
    p = {"iat": int(time.time()), "exp": int(time.time())+300, "aud":"/admin/"}
    return jwt.encode(p, bytes.fromhex(s), algorithm="HS256", headers={"kid":kid,"alg":"HS256","typ":"JWT"})

def post(title, slug, excerpt, html_body, tags):
    body = {"posts":[{"title":title,"slug":slug,"custom_excerpt":excerpt,
                      "html":html_body,"status":"draft",
                      "tags":[{"name":t} for t in tags]}]}
    r = requests.post(f"{GHOST_URL}/ghost/api/admin/posts/?source=html",
                      headers={"Authorization":f"Ghost {tok()}","Accept-Version":"v6"},
                      json=body, timeout=30)
    print(f"  {r.status_code} {slug}")

# ======================== 5 BEST-OF EN ========================
BEST_OF = [
    ("Best AI Companion Apps 2026: Independent Guide", "best-ai-companion-apps-2026",
     "Independent 2026 guide to the top AI companion apps, compared on features, pricing, memory and safety.",
     """<p>Our 2026 guide to the best AI companion apps, ranked by feature depth, memory quality, pricing and safety posture. Each pick is based on public documentation, community reports and hands-on testing where available.</p>
     <h2>Top picks at a glance</h2>
     <ol><li><strong>NordVPN-like for companionship: Nomi</strong> — best memory system</li>
     <li><strong>Category leader: Character.AI</strong> — biggest roster</li>
     <li><strong>Polish: Replika</strong> — longest-running, most mainstream</li>
     <li><strong>Customisation: Kindroid</strong> — opt-in uncensored</li>
     <li><strong>Simple: Pi</strong> — emotionally supportive, free</li></ol>
     <h2>How we test</h2>
     <p>See our <a href="/methodology">methodology</a>. Reviews published as guides until 14-30 days of testing complete.</p>""",
     ["best-of", "companion"]),

    ("Best AI Language Tutor Apps 2026", "best-ai-language-tutor-2026",
     "The top AI language tutor apps in 2026, tested on speaking practice, curriculum and pricing.",
     """<p>Best AI language tutors in 2026. Focus: conversation-first practice rather than gamified streaks.</p>
     <ol><li><strong>Talkpal</strong> — strongest speaking focus, 50+ languages</li>
     <li><strong>Duolingo Max</strong> — polished gamification + AI roleplay</li>
     <li><strong>Babbel</strong> — tighter curriculum, conversation-ready</li>
     <li><strong>Preply</strong> — human tutors with AI practice (hybrid)</li></ol>""",
     ["best-of", "language"]),

    ("Best AI Mental Health Apps 2026 (Not Medical Advice)", "best-ai-mental-health-2026",
     "AI mental health apps in 2026: CBT-inspired, mood tracking, crisis support. Not a substitute for professional care.",
     """<div style="padding:16px;background:#fee;border:1px solid #f99;border-radius:6px;margin:16px 0">
     <strong>Crisis support:</strong> Call 988 (US) or 3114 (France). This article is informational only, not medical advice.
     </div>
     <p>Our picks for AI mental health support apps in 2026. All are adjuncts to professional care, not replacements.</p>
     <ol><li><strong>Woebot</strong> — CBT-focused, clinician-reviewed</li>
     <li><strong>Wysa</strong> — anonymous, HIPAA option</li>
     <li><strong>Youper</strong> — structured CBT exercises</li>
     <li><strong>Headspace Ebb</strong> — mindfulness + AI chat</li>
     <li><strong>Calm</strong> — sleep and anxiety, AI guided</li></ol>""",
     ["best-of", "mental-health", "ymyl"]),

    ("Best AI Companion Apps for Seniors 2026", "best-ai-companion-seniors-2026",
     "AI companions and voice assistants designed for adults 65+ to reduce isolation.",
     """<p>AI companionship for seniors combats isolation, which doubles dementia risk per JAMA research.</p>
     <ol><li><strong>ElliQ</strong> — table-top social robot (deployed by NY State)</li>
     <li><strong>inTouch Family</strong> — family check-in + voice</li></ol>""",
     ["best-of", "seniors"]),

    ("Best AI Writing Assistant 2026", "best-ai-writing-assistant-2026",
     "Professional AI writing tools compared on output quality, pricing and integrations.",
     """<p>Best AI writing assistants in 2026 for professionals.</p>
     <ol><li><strong>Jasper</strong> — marketing content platform</li>
     <li><strong>Copy.ai</strong> — sales + marketing copy</li>
     <li><strong>Writesonic</strong> — SEO-focused</li>
     <li><strong>Notion AI</strong> — integrated in Notion workspace</li></ol>""",
     ["best-of", "productivity"]),
]

# ======================== 5 COMPARATIFS ========================
COMPARE = [
    ("Replika vs Character.AI (2026 Comparison)", "replika-vs-character-ai-2026",
     "Replika vs Character.AI compared: memory, roleplay, pricing, safety in 2026.",
     """<p>Replika offers a single persistent companion; Character.AI gives access to millions of community-created personas. Both are category leaders with different philosophies.</p>
     <h2>Pick Replika if</h2><ul><li>You want one deep long-term relationship</li><li>Voice calls matter</li></ul>
     <h2>Pick Character.AI if</h2><ul><li>You want variety in roleplay</li><li>You prefer free</li></ul>""",
     ["compare", "companion"]),

    ("Nomi vs Kindroid (2026)", "nomi-vs-kindroid-2026",
     "Nomi vs Kindroid: memory-first vs customisation-first AI companions compared.",
     """<p>Both target power users rejecting Replika restrictions. Nomi wins memory, Kindroid wins visual customisation.</p>""",
     ["compare", "companion"]),

    ("Talkpal vs Duolingo Max (2026)", "talkpal-vs-duolingo-max-2026",
     "Talkpal vs Duolingo Max: conversation-first AI tutor vs gamified curriculum.",
     """<p>Talkpal wins for speaking practice, Duolingo Max wins for daily-habit retention.</p>""",
     ["compare", "language"]),

    ("Jasper vs Copy.ai (2026)", "jasper-vs-copyai-2026",
     "Jasper vs Copy.ai: AI writing platforms compared on quality, pricing, team features.",
     """<p>Jasper is enterprise-friendly with marketing focus. Copy.ai is more flexible for solo creators.</p>""",
     ["compare", "productivity"]),

    ("Woebot vs Wysa (2026, Not Medical Advice)", "woebot-vs-wysa-2026",
     "Two AI mental-health chatbots compared: Woebot (CBT-focused) vs Wysa (anonymous, HIPAA).",
     """<div style="padding:12px;background:#fee;border:1px solid #f99;border-radius:6px"><strong>Not medical advice.</strong> Crisis: 988 (US) / 3114 (FR).</div>
     <p>Woebot leans clinically vetted CBT; Wysa adds anonymity and an optional HIPAA-compliant version for enterprise.</p>""",
     ["compare", "mental-health", "ymyl"]),
]

# ======================== RUN ========================
print("Seeding 5 best-of (drafts)...")
for p in BEST_OF:
    post(*p); time.sleep(0.5)
print("Seeding 5 comparatifs (drafts)...")
for p in COMPARE:
    post(*p); time.sleep(0.5)
print("Done. 10 drafts created in AICT Ghost. Log in at https://aicompaniontoday.com/ghost/ to review and publish.")
