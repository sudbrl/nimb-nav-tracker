import urllib.request
import json
import sqlite3

API_URL = "https://sudipbaral.com.np"

# Fetch API data
req = urllib.request.Request(API_URL, headers={'User-Agent': 'Mozilla/5.0'})
data = json.loads(urllib.request.urlopen(req, timeout=15).read().decode('utf-8'))

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

