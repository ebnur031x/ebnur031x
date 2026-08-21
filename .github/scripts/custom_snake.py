import json, os, urllib.request

TOKEN = os.environ['GH_TOKEN']
USER = os.environ.get('GITHUB_USER', 'ebnur031x')

query = '''query($login:String!){ user(login:$login){ contributionsCollection { contributionCalendar { weeks { contributionDays { contributionCount date } } } } } }'''
data = json.dumps({'query': query, 'variables': {'login': USER}}).encode()
req = urllib.request.Request(
    'https://api.github.com/graphql', data=data,
    headers={'Authorization': f'bearer {TOKEN}', 'Content-Type':'application/json', 'User-Agent':'profile-snake'}
)
with urllib.request.urlopen(req) as r:
    payload = json.load(r)

cal = payload['data']['user']['contributionsCollection']['contributionCalendar']
days = [d for w in cal['weeks'] for d in w['contributionDays']]

# Real longest consecutive-day contribution streak.
best = cur = 0
for d in days:
    if d['contributionCount'] > 0:
        cur += 1
        best = max(best, cur)
    else:
        cur = 0

W, H = 53, 7
CELL, GAP = 12, 4
LEFT, TOP = 28, 30
width = LEFT * 2 + W * (CELL + GAP) - GAP
height = 170
palette = ['#111820', '#0e4429', '#16823b', '#26a641', '#39d353']

def level(n):
    if n <= 0: return 0
    if n == 1: return 1
    if n <= 3: return 2
    if n <= 6: return 3
    return 4

cells = []
active = []
for i, d in enumerate(days):
    x, y = i // 7, i % 7
    px = LEFT + x * (CELL + GAP)
    py = TOP + y * (CELL + GAP)
    cells.append((px, py, d['contributionCount']))
    if d['contributionCount'] > 0:
        active.append((x, y, px + CELL / 2, py + CELL / 2))

# Draw the snake ONLY through adjacent contribution cells. This prevents
# long green lines from jumping across empty parts of the contribution graph.
runs = []
run = []
for item in active:
    x, y, cx, cy = item
    if not run:
        run = [item]
        continue
    px, py, _, _ = run[-1]
    if abs(x - px) + abs(y - py) <= 1:
        run.append(item)
    else:
        runs.append(run)
        run = [item]
if run:
    runs.append(run)

# Keep only useful connected runs; single contribution cells remain visible
# as the original contribution square, rather than becoming giant lines.
paths = []
for run in runs:
    if len(run) >= 2:
        pts = [(a[2], a[3]) for a in run]
        d = 'M ' + ' '.join(
            (f'{x:.1f},{y:.1f}' if i == 0 else f'L {x:.1f},{y:.1f}')
            for i, (x, y) in enumerate(pts)
        )
        paths.append(d)

# The latest real contribution is the snake head / apple position.
if active:
    hx, hy, head_x, head_y = active[-1]
else:
    hx = hy = 0
    head_x, head_y = LEFT + CELL / 2, TOP + CELL / 2

svg = [f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
<rect width="100%" height="100%" rx="14" fill="#05080d"/>
<style>
.cell {{ stroke:#0b1118; stroke-width:1; }}
.snake {{ fill:none; stroke:#39d353; stroke-width:8; stroke-linecap:round; stroke-linejoin:round; stroke-dasharray:13 8; animation:slither 7s linear infinite; }}
.head {{ fill:#39d353; }}
.eye {{ fill:#07120a; }}
.apple {{ animation:bob 1s ease-in-out infinite alternate; transform-box:fill-box; transform-origin:center; }}
@keyframes slither {{ to {{ stroke-dashoffset:-210; }} }}
@keyframes bob {{ to {{ transform:translateY(-3px); }} }}
</style>
<text x="28" y="19" fill="#9be9a8" font-family="system-ui,sans-serif" font-size="11" font-weight="700">FEED THE SNAKE WITH CONTRIBUTIONS 🐍</text>''']

# The real contribution calendar.
for px, py, n in cells:
    svg.append(f'<rect class="cell" x="{px}" y="{py}" width="{CELL}" height="{CELL}" rx="3" fill="{palette[level(n)]}"/>')

# Snake body only follows connected real contribution cells.
for path in paths:
    svg.append(f'<path d="{path}" class="snake"/>')

# Head and eyes at the latest contribution.
svg.append(f'''<g transform="translate({head_x},{head_y})">
  <circle r="7.5" class="head"/>
  <circle cx="-2.5" cy="-2" r="1.8" class="eye"/>
  <circle cx="2.5" cy="-2" r="1.8" class="eye"/>
</g>''')

# Apple near the latest contribution, like the reference design.
svg.append(f'''<g class="apple" transform="translate({head_x-5},{head_y-19})">
  <circle cx="5" cy="9" r="7.5" fill="#ff3b30"/>
  <path d="M5 2 Q6 -4 10 -6" stroke="#35c759" stroke-width="2" fill="none"/>
  <ellipse cx="9" cy="-4" rx="4" ry="2" fill="#30d158" transform="rotate(-25 9 -4)"/>
</g>''')

svg.append(f'<text x="{width/2:.0f}" y="151" text-anchor="middle" fill="#e6edf3" font-family="system-ui,sans-serif" font-size="14">✨ Longest streak: <tspan fill="#39d353" font-weight="800">{best} days</tspan></text>')
svg.append('</svg>')

os.makedirs('dist', exist_ok=True)
with open('dist/custom-snake.svg', 'w', encoding='utf-8') as f:
    f.write(''.join(svg))
