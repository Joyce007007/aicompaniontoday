"""Inject 41 CrakRevenue AI offers into aict DB offer_candidates as 'nsfw_subdomain_candidate'
status, so they can be activated on /romance/ subsection later with age-gate.
"""
import json, sys, os, re, time
import psycopg2

AFFILIATE_ID = "408600"
DB_DSN = "postgresql://aict_app:aict_9m8k2jL3pQ5rN@127.0.0.1:5432/aict"

offers_raw = [
    {"id": "10335", "name": "Candy.ai - PPS T1 (Premium)", "payout_type": "PPS", "payout": "$40.00", "epc": "0.1880"},
    {"id": "10022", "name": "Candy.ai - PPS", "payout_type": "PPS", "payout": "$36.00", "epc": "0.0265"},
    {"id": "9022",  "name": "Candy.ai - Revshare Lifetime", "payout_type": "Revshare", "payout": "40.00%", "epc": "0.0207"},
    {"id": "10381", "name": "Secrets.ai - PPS", "payout_type": "PPS", "payout": "$50.00", "epc": "0.1380"},
    {"id": "10339", "name": "Secrets.ai - Revshare Lifetime", "payout_type": "Revshare", "payout": "40.00%", "epc": "0.0094"},
    {"id": "10341", "name": "Xtease.ai - Multi-CPA Exclusive", "payout_type": "Multi-CPA", "payout": "Varies", "epc": "0.0122"},
    {"id": "9403",  "name": "AI Smartlink", "payout_type": "Smartlink", "payout": "Varies", "epc": "0.0010"},
    {"id": "10138", "name": "ourdream.ai - PPS", "payout_type": "PPS", "payout": "$32.40", "epc": "0.0470"},
    {"id": "10345", "name": "DarLink Ai - PPS", "payout_type": "PPS", "payout": "$30.00", "epc": "0.2291"},
    {"id": "10344", "name": "DarLink Ai - Revshare Lifetime", "payout_type": "Revshare", "payout": "45.00%", "epc": None},
    {"id": "9183",  "name": "DreamBF.ai - Revshare Lifetime", "payout_type": "Revshare", "payout": "35.00%", "epc": "0.0150"},
    {"id": "9057",  "name": "Dreamgf.ai - Revshare Lifetime", "payout_type": "Revshare", "payout": "35.00%", "epc": "0.0102"},
    {"id": "9182",  "name": "eHentai.ai - Revshare Lifetime", "payout_type": "Revshare", "payout": "35.00%", "epc": "0.0032"},
    {"id": "10141", "name": "Fanfinity - PPS", "payout_type": "PPS", "payout": "$17.50", "epc": "0.0140"},
    {"id": "10140", "name": "Fanfinity - Revshare", "payout_type": "Revshare", "payout": "45.00%", "epc": "0.0067"},
    {"id": "10057", "name": "Fantasy.Ai - Revshare", "payout_type": "Revshare", "payout": "35.00%", "epc": "0.0160"},
    {"id": "10182", "name": "Get-Harder - PPS", "payout_type": "PPS", "payout": "$34.00", "epc": "0.1723"},
    {"id": "10227", "name": "golove.ai - PPS", "payout_type": "PPS", "payout": "$35.00", "epc": "0.0481"},
    {"id": "10228", "name": "golove.ai - Revshare Lifetime", "payout_type": "Revshare", "payout": "53.00%", "epc": None},
]

def tracking_url(offer_id):
    # CrakRevenue standard tracking URL format
    return f"https://t.mbjms.com/{AFFILIATE_ID}/{offer_id}/0?aff_sub5=aict-romance"


def slug_from_name(name):
    s = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
    # Clean up: "candy-ai-pps-t1-premium" -> "candy-ai-t1"
    s = re.sub(r'-pps|-revshare.*|-multi-cpa.*|-exclusive|-smartlink|-lifetime', '', s)
    return s[:30].strip('-')


def inject():
    conn = psycopg2.connect(DB_DSN)
    added = 0
    for o in offers_raw:
        slug = slug_from_name(o['name'])
        track_url = tracking_url(o['id'])
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO public.offer_candidates
                    (network, vendor, name, category, hoplink, status, commission_pct, avg_sale_usd)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (network, vendor) DO UPDATE SET
                    name = EXCLUDED.name,
                    hoplink = EXCLUDED.hoplink,
                    commission_pct = EXCLUDED.commission_pct,
                    avg_sale_usd = EXCLUDED.avg_sale_usd,
                    fetched_at = NOW()
            """, (
                'CrakRevenue',
                o['id'],
                o['name'],
                'AI Companion / NSFW',
                track_url,
                'nsfw_subdomain_candidate',
                float(re.sub(r'[^0-9.]', '', o['payout'])) if '%' in o['payout'] else None,
                float(re.sub(r'[^0-9.]', '', o['payout'])) if '$' in o['payout'] else None
            ))
            added += 1
    conn.commit()
    conn.close()
    print(f"Injected {added} CrakRevenue offers into aict.public.offer_candidates with status='nsfw_subdomain_candidate'")

if __name__ == "__main__":
    inject()
