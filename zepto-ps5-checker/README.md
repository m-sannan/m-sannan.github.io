# Zepto PS5 Stock Checker — Bangalore

Scans 66 Bangalore locations on Zepto and alerts you the moment a PS5 is in stock.

Built by u/msannan121

---

## What you need

- A Mac or Windows PC
- Python 3 installed
- A Zepto account (logged in on Chrome)

---

## Step 1 — Install Python 3

**Mac:**
Check if you already have it:
```
python3 --version
```
If not, download from: https://python.org/downloads

**Windows:**
Download from: https://python.org/downloads
During install, tick **"Add Python to PATH"**

---

## Step 2 — Install dependencies

Open Terminal (Mac) or Command Prompt (Windows) and run:
```
pip3 install requests curl_cffi
```

`curl_cffi` makes requests look like Chrome (TLS fingerprint). Plain `requests` alone often gets **HTTP 202** bot-challenge pages from Zepto.

---

## Step 3 — Get your Zepto cookie (Network tab)

This is your personal login session. **Do not share this with anyone.**

Chrome blocks `javascript:` pasted into the address bar, and `document.cookie` **misses HttpOnly auth cookies**. Do **not** use the old bookmarklet. Copy the cookie from a real **product page** request instead.

1. Open **Chrome** → go to **https://www.zepto.com** → log in
2. Set any Bangalore delivery address
3. Open a product page (PS5, or any product for a dry run). The URL should look like:
   ```
   https://www.zepto.com/pn/.../pvid/...
   ```
4. Press **F12** → **Network** tab
5. Reload the product page (or click the product again)
6. In the filter box, type `pn/` or `pvid`
7. Click the request whose URL is the **product page** (not `~partytown`, analytics, or images)
8. In **Headers** → **Request Headers**, find **`Cookie:`**
9. Copy the **entire** cookie value (everything after `Cookie: `)

**Or:** right-click that same product request → **Copy → Copy as cURL**, then paste the `-H 'Cookie: ...'` value into `cookie.txt` (cookie string only, without the `Cookie: ` label).

Wrong request (ignore these):
```
https://www.zepto.com/~partytown/proxytown   ← analytics, not stock
```

Right request:
```
https://www.zepto.com/pn/<product-slug>/pvid/<uuid>
```

---

## Step 4 — Create cookie.txt

In the same folder as `zepto_ps5_checker.py`, create a new file called:
```
cookie.txt
```
Paste your copied cookie string into it. Save. That's it.

**Your cookie stays on your machine and is never sent anywhere except Zepto's own servers.**  
Never commit `cookie.txt` to GitHub.

---

## Step 5 — Probe once, then validate

Confirm Zepto accepts your cookie before scanning 66 locations:

**Mac:**
```
python3 zepto_ps5_checker.py --probe
```
**Windows:**
```
python zepto_ps5_checker.py --probe
```

You want status **200** and a body that mentions product fields. If you see **HTTP 202** / `BOT_CHALLENGE`, refresh the cookie from a product-page request (Step 3) and try again.

Then run the Paper Boat test:

**Mac:**
```
python3 zepto_ps5_checker.py --test
```
**Windows:**
```
python zepto_ps5_checker.py --test
```

You should see `🔥 IN STOCK!` or `OOS` for areas (it's checking Paper Boat).  
If you see that — your setup is working correctly.

---

## Step 6 — Run the PS5 scan

```
python3 zepto_ps5_checker.py
```

Takes about 5–6 minutes to scan all 66 locations. Results print live.  
If PS5 is found, your Mac will also show a notification with a sound.

---

## Run it overnight (recommended)

PS5 stock appears in short windows. Running repeatedly gives you the best chance.

**Mac — keep running every 30 mins:**
```
caffeinate -i &
while true; do
    python3 zepto_ps5_checker.py
    echo "--- Waiting 30 mins before next scan ---"
    sleep 1800
done
```

**Windows — keep running every 30 mins:**
```
:loop
python zepto_ps5_checker.py
timeout /t 1800
goto loop
```

Press **Ctrl + C** to stop at any time.

---

## Cookie expires in ~1 hour

Zepto session tokens are short-lived. If you see:
```
⚠️  Cookie expired — refresh cookie.txt and restart
```
or:
```
🛑  BOT_CHALLENGE / blocked — refresh cookie from a product-page Network request
```
Just repeat Step 3, paste the new cookie into `cookie.txt`, and re-run.

---

## Flags

| Flag | What it does |
|------|-------------|
| `--probe` | One diagnostic request: status, content-type, body snippet, challenge detection |
| `--test` | Runs on Paper Boat to validate your setup |
| `--debug` | Shows the exact signal string that triggered each result |

---

## FAQ

**I get HTTP 202 / BOT_CHALLENGE**  
Zepto (or its WAF) returned a challenge page instead of product data. Install `curl_cffi`, copy a fresh **product-page** Cookie header (not Partytown), and run `--probe` again.

**Is this safe to run?**  
Yes. The script only reads Zepto's product pages — the same thing your browser does. It adds delays between requests to avoid hammering their servers.

**Will my account get banned?**  
Unlikely. The script mimics normal browser behaviour and runs slowly. That said, use it responsibly.

**Can I add more locations?**  
Yes — open the script and add entries to `GROUP_A` or `GROUP_B` in the format:
```python
("Area Name", latitude, longitude),
```

**Cookie not working?**  
Make sure you're logged in on Zepto before copying the cookie from a `pn/` / `pvid` request. Grab a fresh one and paste it into `cookie.txt`.

---

## Files

```
zepto_ps5_checker.py   ← the script
cookie.txt             ← your personal cookie (create this yourself, never share it)
README.md              ← this file
```

Proof 

<img width="451" height="193" alt="Screenshot 2026-07-01 at 10 50 19 PM" src="https://github.com/user-attachments/assets/8e048f40-b20c-4f90-9b6f-6e4f4b9de84b" />

---

<img width="357" height="73" alt="Screenshot 2026-07-01 at 10 51 21 PM" src="https://github.com/user-attachments/assets/ea5061d1-8b41-413c-8a07-92ba7075b266" />
