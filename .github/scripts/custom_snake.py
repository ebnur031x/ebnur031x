import json, os, urllib.request
from datetime import date, timedelta

TOKEN = os.environ['GH_TOKEN']
USER = os.environ.get('GITHUB_USER', 'ebnur031x')

query = '''query($login:String!){ user(login:$login){ contributionsCollection { contributionCalendar { totalContributions weeks { contributionDays { contributionCount date } } } } } }'''
data = json.dumps({'query': query, 'variables': {'login': USER}}).encode()
req = urllib.request.Request('https://api.github.com/graphql', data=data, headers={'Authorization': f'bearer {TOKEN}', 'Content-Type':'application/json', 'User-Agent':'profile-snake'})
with urllib.request.urlopen(req) as r:
    payload = json.load(r)
cal = payload['data']['user']['contributionsCollection']['contributionCalendar']
days = [d for w in cal['weeks'] for d in w['contributionDays']]
counts = [d['contributionCount'] for d in days]

best = cur = 0
for n in counts:
    if n > 0:
        cur += 1; best = max(best, cur)
    else:
        cur = 0

# Grid: 53 weeks x 7 days. Draw the real contribution cells.
W, H, CELL, GAP = 53, 7, 13, 3
left, top = 24, 28
width = left*2 + W*(CELL+GAP)-GAP
height = 170
palette = ['#161b22','#0e4429','#006d32','#26a641','#39d353']

def level(n):
    if n <= 0: return 0
    if n == 1: return 1
    if n <= 3: return 2
    if n <= 6: return 3
    return 4

cells=[]
for i,d in enumerate(days):
    x=i//7; y=i%7
    cells.append((x,y,d['contributionCount']))

# A serpentine route through the real contribution grid.
pts=[]
for x in range(W):
    ys=range(H) if x%2==0 else range(H-1,-1,-1)
    for y in ys:
        pts.append((left+x*(CELL+GAP)+CELL/2, top+y*(CELL+GAP)+CELL/2))
path_d='M '+' '.join((f'{x:.1f},{y:.1f}' if j==0 else f'L {x:.1f},{y:.1f}') for j,(x,y) in enumerate(pts))

svg=[]
svg.append(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
<rect width="100%" height="100%" rx="14" fill="#05080d"/>
<style>
.cell{{stroke:#0b1118;stroke-width:1}}
.snake{{stroke:#36d15b;stroke-width:12;stroke-linecap:round;stroke-linejoin:round;fill:none;stroke-dasharray:20 14;animation:move 9s linear infinite}}
.head{{fill:#36d15b;animation:wiggle .55s ease-in-out infinite alternate}}
.eye{{fill:#07120a}}
.apple{{animation:bob 1s ease-in-out infinite alternate}}
@keyframes move{{to{{stroke-dashoffset:-680}}}}
@keyframes wiggle{{to{{transform:translateY(2px)}}}}
@keyframes bob{{to{{transform:translateY(-4px)}}}}
</style>''')
svg.append(f'<text x="24" y="18" fill="#9be9a8" font-family="system-ui, sans-serif" font-size="11" font-weight="700">FEED THE SNAKE WITH CONTRIBUTIONS 🐍</text>')
for x,y,n in cells:
    px=left+x*(CELL+GAP); py=top+y*(CELL+GAP)
    svg.append(f'<rect class="cell" x="{px}" y="{py}" width="{CELL}" height="{CELL}" rx="3" fill="{palette[level(n)]}"/>')
svg.append(f'<path id="snakepath" d="{path_d}" class="snake" opacity=".96"/>')
# Animated head follows the route.
svg.append(f'''<g>
<circle r="9" class="head"><animateMotion dur="9s" repeatCount="indefinite" rotate="auto"><mpath href="#snakepath"/></animateMotion></circle>
<circle r="2.3" class="eye"><animateMotion dur="9s" repeatCount="indefinite" rotate="auto" additive="sum"><mpath href="#snakepath"/></animateMotion></circle>
</g>''')
# Apple at the final grid cell.
ax, ay = pts[-1]
svg.append(f'<g class="apple" transform="translate({ax-5},{ay-20})"><circle cx="5" cy="9" r="8" fill="#ff3b30"/><path d="M5 1 Q7 -5 11 -6" stroke="#35c759" stroke-width="2" fill="none"/><ellipse cx="9" cy="-4" rx="4" ry="2" fill="#30d158" transform="rotate(-25 9 -4)"/></g>')
svg.append(f'<text x="{width/2:.0f}" y="150" text-anchor="middle" fill="#e6edf3" font-family="system-ui, sans-serif" font-size="14">✨ Longest streak: <tspan fill="#39d353" font-weight="800">{best} days</tspan></text>')
svg.append('</svg>')

os.makedirs('dist', exist_ok=True)
open('dist/custom-snake.svg','w').write(''.join(svg))
