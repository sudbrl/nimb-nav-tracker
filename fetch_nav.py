import urllib.request
import json
import sqlite3
import sys

API_URL = "https://sudipbaral.com.np"

# Mimic a real web browser to bypass basic bot blocks
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'Accept': 'application/json,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive'
}

req = urllib.request.Request(API_URL, headers=headers)

try:
    with urllib.request.urlopen(req, timeout=20) as response:
        raw_text = response.read().decode('utf-8').strip()
except Exception as e:
    print(f"Connection failed: {e}")
    sys.exit(1)

# Check if the server returned empty text or HTML instead of JSON
if not raw_text:
    print("Error: Server returned a completely empty response (likely blocking GitHub's IP).")
    sys.exit(1)

try:
    data = json.loads(raw_text)
except json.JSONDecodeError:
    print("Error: Server did not return valid JSON. Here is what it sent instead:")
    print(raw_text[:500])
    sys.exit(1)

# Save to SQLite database
conn = sqlite3.connect("mutual_fund.sqlite")
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS nav_history (id INTEGER PRIMARY KEY, fund TEXT, nav REAL, as_on TEXT, UNIQUE(fund, as_on))')
cursor.execute('INSERT OR IGNORE INTO nav_history (fund, nav, as_on) VALUES (?, ?, ?)', (data['fund'], float(data['nav']), data['as_on']))
conn.commit()

# Export to JSON data source
rows = cursor.execute('SELECT fund, nav, as_on FROM nav_history ORDER BY id DESC').fetchall()
with open("history.json", "w") as f:
    json.dump([{"fund": r[0], "nav": r[1], "as_on": r[2]} for r in rows], f, indent=2)

conn.close()
print(f"Success! Saved NAV {data['nav']} for {data['as_on']}")
