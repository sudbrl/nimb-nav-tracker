from playwright.sync_api import sync_playwright
import json
import sqlite3

API_URL = "https://sudipbaral.com.np"

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(API_URL, wait_until="networkidle")
    raw_text = page.inner_text("body").strip()
    browser.close()

data = json.loads(raw_text)

conn = sqlite3.connect("mutual_fund.sqlite")
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS nav_history (id INTEGER PRIMARY KEY, fund TEXT, nav REAL, as_on TEXT, UNIQUE(fund, as_on))')
cursor.execute('INSERT OR IGNORE INTO nav_history (fund, nav, as_on) VALUES (?, ?, ?)', (data['fund'], float(data['nav']), data['as_on']))
conn.commit()

rows = cursor.execute('SELECT fund, nav, as_on FROM nav_history ORDER BY id DESC').fetchall()
with open("history.json", "w") as f:
    json.dump([{"fund": r[0], "nav": r[1], "as_on": r[2]} for r in rows], f, indent=2)

conn.close()
print(f"Success! Saved NAV {data['nav']} for {data['as_on']}")
