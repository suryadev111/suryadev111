
import json
import urllib.request
from datetime import datetime, timedelta, timezone
from collections import Counter

USERNAME = "suryadev111"

TODAY = datetime.now(timezone.utc).date()
START = TODAY - timedelta(days=29)

activity = Counter()

# Fetch recent public GitHub events
for page in range(1, 4):
    url = (
        f"https://api.github.com/users/{USERNAME}"
        f"/events/public?per_page=100&page={page}"
    )

    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "GitHub-Activity-Graph"
        }
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        events = json.loads(response.read())

    if not events:
        break

    for event in events:
        event_date = datetime.fromisoformat(
            event["created_at"].replace("Z", "+00:00")
        ).date()

        if START <= event_date <= TODAY:
            count = 1

            if event["type"] == "PushEvent":
                count = max(
                    1,
                    len(event.get("payload", {}).get("commits", []))
                )

            activity[event_date] += count

    if len(events) < 100:
        break


# Prepare the last 30 days
days = [
    START + timedelta(days=i)
    for i in range(30)
]

values = [activity[day] for day in days]

# SVG dimensions
WIDTH = 1000
HEIGHT = 300

LEFT = 65
RIGHT = 25
TOP = 45
BOTTOM = 55

PLOT_W = WIDTH - LEFT - RIGHT
PLOT_H = HEIGHT - TOP - BOTTOM

maximum = max(max(values), 1)

# Calculate graph points
points = []

for i, value in enumerate(values):
    x = LEFT + i * PLOT_W / 29
    y = TOP + PLOT_H - (value / maximum) * PLOT_H
    points.append((x, y))

line = " ".join(
    f"{x:.1f},{y:.1f}"
    for x, y in points
)

area = (
    f"{LEFT},{TOP + PLOT_H} "
    + line
    + f" {LEFT + PLOT_W},{TOP + PLOT_H}"
)

# Grid lines
grid = ""

for i in range(5):
    y = TOP + i * PLOT_H / 4

    grid += (
        f'<line x1="{LEFT}" y1="{y:.1f}" '
        f'x2="{WIDTH - RIGHT}" y2="{y:.1f}" '
        'stroke="#30363d" stroke-dasharray="4 6"/>'
    )

# Date labels
labels = ""

for i in range(0, 30, 5):
    x = LEFT + i * PLOT_W / 29

    labels += (
        f'<text x="{x:.1f}" y="{HEIGHT - 20}" '
        'fill="#8b949e" font-size="12" text-anchor="middle">'
        f'{days[i].strftime("%d %b")}</text>'
    )

total = sum(values)

# Generate SVG
svg = f'''<svg xmlns="http://www.w3.org/2000/svg"
width="100%" viewBox="0 0 {WIDTH} {HEIGHT}">

<rect width="100%" height="100%" rx="14" fill="#0d1117"/>

<text x="{LEFT}" y="28"
fill="#c9d1d9"
font-size="19"
font-weight="bold">
Contribution Activity — Last 30 Days
</text>

{grid}

<polygon points="{area}"
fill="#58a6ff"
opacity="0.16"/>

<polyline points="{line}"
fill="none"
stroke="#58a6ff"
stroke-width="3"
stroke-linecap="round"
stroke-linejoin="round"/>

{labels}

<text x="{WIDTH - RIGHT}" y="28"
fill="#58a6ff"
font-size="15"
text-anchor="end">
{total} public activity points
</text>

</svg>'''

with open("activity-graph.svg", "w", encoding="utf-8") as file:
    file.write(svg)

print("Activity graph generated successfully!")
