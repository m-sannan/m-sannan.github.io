"""
zepto_ps5_checker.py
====================
Checks PS5 availability across Bangalore on Zepto.
Scans 66 locations (broad city + dense Whitefield/ITPL belt).

HOW TO USE:
  1. Create a file called cookie.txt in the same folder as this script
  2. Paste your Zepto Cookie header from a product-page Network request
     (see README — do NOT use the javascript: bookmarklet or Partytown curls)
  3. Run: python3 zepto_ps5_checker.py --probe
  4. Then: python3 zepto_ps5_checker.py --test
  5. Then: python3 zepto_ps5_checker.py

FLAGS:
  --probe   One diagnostic request (status, headers, body snippet)
  --test    Runs on Paper Boat instead of PS5 (validates your setup)
  --debug   Shows which signal string triggered each result
"""

import json
import sys
import time
import random
import os
import urllib.parse
from datetime import datetime

DEBUG   = "--debug" in sys.argv
RUNTEST = "--test"  in sys.argv
PROBE   = "--probe" in sys.argv

# Prefer curl_cffi (Chrome TLS fingerprint). Fall back to requests with a clear warning.
try:
    from curl_cffi import requests as http
    HTTP_BACKEND = "curl_cffi"
    IMPERSONATE = "chrome"
except ImportError:
    import requests as http
    HTTP_BACKEND = "requests"
    IMPERSONATE = None

# ─────────────────────────────────────────────────────────────────────────────
# LOAD COOKIE FROM FILE
# Never hardcode your cookie here — put it in cookie.txt instead
# ─────────────────────────────────────────────────────────────────────────────

COOKIE_FILE = os.path.join(os.path.dirname(__file__), "cookie.txt")

if not os.path.exists(COOKIE_FILE):
    print("""
─────────────────────────────────────────────────────────
  ❌  cookie.txt not found.

  Create a file called cookie.txt in the same folder
  as this script, then paste your Zepto Cookie header
  from a product-page Network request (pn/ or pvid).
  See README.md — do not use the javascript bookmarklet
  or a ~partytown/proxytown curl.
─────────────────────────────────────────────────────────
""")
    sys.exit(1)

with open(COOKIE_FILE, "r") as f:
    COOKIE_STRING = f.read().strip()

# Allow pasting a full "Cookie: ..." line from Copy as cURL / DevTools
if COOKIE_STRING.lower().startswith("cookie:"):
    COOKIE_STRING = COOKIE_STRING.split(":", 1)[1].strip()

if len(COOKIE_STRING) < 50:
    print("❌  cookie.txt looks empty or incomplete. Please re-paste your cookie.")
    sys.exit(1)

# ─────────────────────────────────────────────────────────────────────────────
# PRODUCT URLS
# ─────────────────────────────────────────────────────────────────────────────
PS5_URL        = "https://www.zepto.com/pn/playstation-5-console-slim-playstation-5-console-e-chasis-slim/pvid/ad968d7d-c5d8-415e-b7d4-58f84ff13076"
PAPER_BOAT_URL = "https://www.zepto.com/pn/paper-boat-zero-sparkling-coffee/pvid/b5db7153-f83d-4b7a-9fe0-3899caaae95e"

PRODUCT_URL = PAPER_BOAT_URL if RUNTEST else PS5_URL

# ─────────────────────────────────────────────────────────────────────────────
# HEADERS
# ─────────────────────────────────────────────────────────────────────────────
BASE_HEADERS = {
    "accept": "*/*",
    "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
    "referer": "https://www.zepto.com/",
    "sec-ch-ua": '"Chromium";v="149", "Not)A;Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "rsc": "1",
    "priority": "u=1, i",
}

# ─────────────────────────────────────────────────────────────────────────────
# LOCATIONS — 40 broad Bangalore + 26 Whitefield/Phoenix belt
# ─────────────────────────────────────────────────────────────────────────────
GROUP_A = [
    ("Koramangala",        12.9352, 77.6245),
    ("Indiranagar",        12.9784, 77.6408),
    ("Whitefield",         12.9698, 77.7499),
    ("Marathahalli",       12.9556, 77.7023),
    ("HSR Layout",         12.9116, 77.6389),
    ("BTM Layout",         12.9166, 77.6101),
    ("Jayanagar",          12.9308, 77.5831),
    ("JP Nagar",           12.9089, 77.5849),
    ("Banashankari",       12.9259, 77.5494),
    ("Rajajinagar",        12.9937, 77.5517),
    ("Malleswaram",        13.0034, 77.5642),
    ("Yeshwantpur",        13.0266, 77.5499),
    ("Hebbal",             13.0450, 77.5970),
    ("Yelahanka",          13.1005, 77.5963),
    ("Electronic City",    12.8399, 77.6770),
    ("Bellandur",          12.9253, 77.6795),
    ("Sarjapur Road",      12.8686, 77.7868),
    ("Bannerghatta Road",  12.8643, 77.5832),
    ("MG Road",            12.9754, 77.6087),
    ("Vijayanagar",        12.9706, 77.5250),
    ("Nagarbhavi",         12.9542, 77.5132),
    ("KR Puram",           13.0030, 77.6900),
    ("Mahadevapura",       12.9882, 77.7081),
    ("Domlur",             12.9601, 77.6347),
    ("Silk Board",         12.9172, 77.6232),
    ("Basavanagudi",       12.9430, 77.5750),
    ("RT Nagar",           13.0218, 77.5990),
    ("Banaswadi",          13.0070, 77.6530),
    ("Peenya",             13.0305, 77.5150),
    ("RR Nagar",           12.9241, 77.5059),
    ("Kengeri",            12.8987, 77.4848),
    ("Hennur",             13.0450, 77.6390),
    ("Frazer Town",        12.9885, 77.6190),
    ("Devanahalli",        13.2467, 77.7116),
    ("Jalahalli",          13.0420, 77.5350),
    ("Cox Town",           12.9946, 77.6198),
    ("Mathikere",          13.0200, 77.5600),
    ("Old Airport Road",   12.9630, 77.6390),
    ("Ulsoor",             12.9760, 77.6200),
    ("Cunningham Road",    12.9924, 77.5979),
]

GROUP_B = [
    ("Phoenix Market City",           12.9983, 77.6965),
    ("Whitefield Main Rd",            12.9859, 77.7310),
    ("ITPL Main Gate",                12.9863, 77.7143),
    ("Brookefield",                   12.9800, 77.7050),
    ("Hoodi",                         12.9964, 77.7003),
    ("Thubarahalli",                  12.9742, 77.7103),
    ("Kundalahalli",                  12.9767, 77.7000),
    ("Nallurhalli",                   12.9745, 77.7285),
    ("Borewell Road",                 12.9900, 77.7200),
    ("AECS Layout",                   12.9932, 77.7180),
    ("Siddapura",                     12.9805, 77.7398),
    ("Hope Farm Junction",            12.9800, 77.7600),
    ("Kadugodi",                      12.9931, 77.7637),
    ("Varthur",                       12.9402, 77.7473),
    ("Ramagondanahalli",              13.0050, 77.7400),
    ("Channasandra",                  13.0035, 77.7267),
    ("Whitefield Station",            12.9710, 77.7500),
    ("Karthik Nagar Whitefield",      12.9750, 77.7350),
    ("Sri Sathya Sai Layout",         12.9900, 77.7480),
    ("Nagondanahalli",                13.0100, 77.7550),
    ("Panathur",                      12.9325, 77.7035),
    ("Kadubeesanahalli",              12.9456, 77.7100),
    ("Outer Ring Rd Marathahalli Jn", 12.9584, 77.7062),
    ("Ramamurthy Nagar",              13.0100, 77.6700),
    ("Tin Factory",                   13.0017, 77.6760),
    ("Nalluhalli",                    12.9600, 77.7300),
]

ALL_LOCATIONS = GROUP_A + GROUP_B

CHALLENGE_MARKERS = (
    "awswaf",
    "aws-waf",
    "challenge.js",
    "challenge-platform",
    "cf-chl",
    "cf-mitigated",
    "just a moment",
    "attention required",
    "captcha",
    "access denied",
    "bot management",
)

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def parse_cookies(raw):
    out = {}
    # Support both "; " and ";" separators from DevTools / cURL
    normalized = raw.replace("\n", "").strip()
    for part in normalized.split(";"):
        part = part.strip()
        if "=" in part:
            k, _, v = part.partition("=")
            out[k.strip()] = v.strip()
    return out

def patch_location(base, lat, lng):
    c = base.copy()
    c["latitude"] = str(lat)
    c["longitude"] = str(lng)
    c["user_position"] = urllib.parse.quote(json.dumps({"latitude": lat, "longitude": lng}))
    c.pop("serviceability", None)
    return c

def detect_challenge(status_code, body):
    """Return vendor/hint string if response looks like a bot wall, else None."""
    lower = (body or "").lower()
    for marker in CHALLENGE_MARKERS:
        if marker in lower:
            return marker
    if status_code == 202:
        return "http_202"
    return None

def http_get(url, cookies):
    kwargs = {
        "headers": BASE_HEADERS,
        "cookies": cookies,
        "timeout": 15,
        "allow_redirects": True,
    }
    if HTTP_BACKEND == "curl_cffi":
        kwargs["impersonate"] = IMPERSONATE
    return http.get(url, **kwargs)

def classify_response(r):
    """Return (status_label, signal) from an HTTP response."""
    if r.status_code == 401:
        return "AUTH_EXPIRED", None
    if r.status_code == 429:
        return "RATE_LIMITED", None

    body = r.text or ""
    challenge = detect_challenge(r.status_code, body)
    if challenge:
        if challenge == "http_202":
            return "BOT_CHALLENGE", "HTTP 202 — likely WAF/bot wall or bad session; refresh product-page cookie"
        return "BOT_CHALLENGE", f"challenge marker: {challenge}"

    if r.status_code != 200:
        return f"HTTP_{r.status_code}", None

    if "maxAllowedQuantity" not in body:
        return "UNKNOWN", "no product block — page may not have loaded"

    if '"outOfStock":true' in body:
        return "OOS", '"outOfStock":true found'
    return "IN_STOCK", '"outOfStock":true absent'

def check_stock(cookies):
    try:
        r = http_get(PRODUCT_URL, cookies)
        return classify_response(r)
    except Exception as e:
        name = type(e).__name__
        if "Timeout" in name or "timeout" in str(e).lower():
            return "TIMEOUT", None
        return f"ERR:{e}", None

def run_probe(base_cookies):
    """Single diagnostic request — helps debug HTTP 202 / bad cookies."""
    # Use first Bangalore pin so location cookies are realistic
    area, lat, lng = GROUP_A[0]
    cookies = patch_location(base_cookies, lat, lng)

    print(f"\n{'─'*62}")
    print("  PROBE MODE — one product-page request")
    print(f"  Backend: {HTTP_BACKEND}" + (f" (impersonate={IMPERSONATE})" if IMPERSONATE else ""))
    print(f"  URL: {PRODUCT_URL}")
    print(f"  Location cookies: {area} ({lat}, {lng})")
    print(f"  Cookie keys loaded: {len(base_cookies)}")
    if HTTP_BACKEND == "requests":
        print("  ⚠️  curl_cffi not installed — Zepto often returns HTTP 202")
        print("     Fix: pip3 install curl_cffi")
    print(f"{'─'*62}\n")

    try:
        r = http_get(PRODUCT_URL, cookies)
    except Exception as e:
        print(f"❌  Request failed: {e}")
        sys.exit(1)

    body = r.text or ""
    ctype = r.headers.get("content-type", "(none)")
    challenge = detect_challenge(r.status_code, body)
    status, signal = classify_response(r)

    print(f"  HTTP status:     {r.status_code}")
    print(f"  Content-Type:    {ctype}")
    print(f"  Body length:     {len(body)} chars")
    print(f"  Classification:  {status}")
    if signal:
        print(f"  Signal:          {signal}")
    if challenge:
        print(f"  Challenge hint:  {challenge}")

    snippet = body[:300].replace("\n", "\\n")
    print(f"\n  Body snippet (first 300 chars):\n  {snippet}\n")

    if status == "BOT_CHALLENGE" or r.status_code == 202:
        print("  🛑  Blocked or challenged.")
        print("     1. pip3 install curl_cffi")
        print("     2. Chrome → product page (pn/.../pvid/...) → Network")
        print("     3. Copy Cookie header into cookie.txt (not Partytown)")
        print("     4. Re-run: python3 zepto_ps5_checker.py --probe\n")
        sys.exit(2)

    if status in ("IN_STOCK", "OOS"):
        print("  ✅  Probe OK — cookie and client look good. Next: --test or full scan.\n")
        sys.exit(0)

    if status == "AUTH_EXPIRED":
        print("  ⚠️  Cookie expired — refresh cookie.txt from a product-page request.\n")
        sys.exit(2)

    print("  ⚠️  Unexpected response — see snippet above. Refresh cookie if unsure.\n")
    sys.exit(1)

def mac_notify(area):
    """Trigger Mac notification + sound when PS5 is found"""
    try:
        os.system(
            f'osascript -e \'display notification "PS5 in stock at {area}! Open Zepto now." '
            f'with title "🔥 Zepto PS5 Alert" sound name "Glass"\''
        )
    except Exception:
        pass

# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    base_cookies = parse_cookies(COOKIE_STRING)

    if PROBE:
        run_probe(base_cookies)
        return

    found = []
    total = len(ALL_LOCATIONS)

    print(f"\n{'─'*62}")
    if RUNTEST:
        print("  TEST MODE — Paper Boat (should show IN STOCK in most areas)")
    else:
        print("  Zepto PS5 Scanner  v5")
    print(f"  {datetime.now().strftime('%d %b %Y  %H:%M')}")
    print(f"  {len(GROUP_A)} broad + {len(GROUP_B)} Whitefield/Phoenix belt = {total} locations")
    print(f"  HTTP backend: {HTTP_BACKEND}" + (f" / {IMPERSONATE}" if IMPERSONATE else ""))
    if HTTP_BACKEND == "requests":
        print("  ⚠️  Install curl_cffi to reduce HTTP 202 bot walls: pip3 install curl_cffi")
    if DEBUG:
        print("  DEBUG ON")
    print(f"{'─'*62}\n")

    for i, (area, lat, lng) in enumerate(ALL_LOCATIONS):

        if i == len(GROUP_A):
            print("\n  ── Whitefield / Phoenix Market City belt ──\n")

        label = f"[{i+1:02}/{total}]  {area:<40}"
        print(f"{label}", end="", flush=True)

        cookies = patch_location(base_cookies, lat, lng)
        status, signal = check_stock(cookies)

        if status == "IN_STOCK":
            debug_str = f"  ← {signal}" if DEBUG else ""
            print(f"🔥  IN STOCK!{debug_str}")
            found.append((area, lat, lng))
            if not RUNTEST:
                mac_notify(area)
        elif status == "AUTH_EXPIRED":
            print("⚠️  Cookie expired — refresh cookie.txt and restart")
            break
        elif status == "BOT_CHALLENGE":
            print("🛑  BOT_CHALLENGE / blocked — refresh cookie from a product-page Network request")
            if DEBUG and signal:
                print(f"         ← {signal}")
            print("\n  Stopping early so we do not hammer 66 locations while blocked.")
            print("  Run: python3 zepto_ps5_checker.py --probe\n")
            break
        elif status == "RATE_LIMITED":
            print("⏳  rate limited — sleeping 45s...")
            time.sleep(45)
        else:
            debug_str = f"  ← {signal}" if (DEBUG and signal) else ""
            print(f"{status}{debug_str}")

        pause = random.uniform(10, 18) if (i + 1) % 8 == 0 else random.uniform(3, 6)
        if (i + 1) % 8 == 0:
            print(f"\n  ↻  pause ({pause:.0f}s)...\n")
        time.sleep(pause)

    print(f"\n{'─'*62}")
    if found:
        print(f"\n  ✅  {'PAPER BOAT' if RUNTEST else 'PS5'} IN STOCK at {len(found)} location(s):\n")
        for area, lat, lng in found:
            print(f"      📍  {area}  ({lat}, {lng})")
        if not RUNTEST:
            print("\n  👉  Change your Zepto address to that area and order!")
    else:
        print("  ❌  Not found at any checked location.")
    print(f"{'─'*62}\n")

if __name__ == "__main__":
    main()
