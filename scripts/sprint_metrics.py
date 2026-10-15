"""이슈와 마일스톤으로 Cycle Time, Velocity, Burndown을 계산해 week03/ANALYSIS.md를 만든다.

스토리 포인트는 'sp: 3' 같은 라벨에서 읽고, 스프린트는 마감일까지 2주(14일)라고 본다.
"""
import json
import os
import urllib.request
from datetime import datetime, timedelta, timezone

REPO = os.environ["GITHUB_REPOSITORY"]
TOKEN = os.environ.get("GITHUB_TOKEN", "")
KST = timezone(timedelta(hours=9))


def get(path):
    req = urllib.request.Request("https://api.github.com" + path)
    req.add_header("Accept", "application/vnd.github+json")
    if TOKEN:
        req.add_header("Authorization", "Bearer " + TOKEN)
    with urllib.request.urlopen(req) as res:
        return json.load(res)


def to_time(text):
    return datetime.fromisoformat(text.replace("Z", "+00:00"))


def points(issue):
    """'sp: 3' 라벨이 있으면 3, 없으면 0"""
    for label in issue["labels"]:
        if label["name"].startswith("sp:"):
            return int(label["name"].split(":")[1])
    return 0


def is_done(issue):
    return issue["state"] == "closed"


# PR과, 하지 않기로 하고 닫은(not planned) 이슈는 뺀다
issues = [i for i in get(f"/repos/{REPO}/issues?state=all&per_page=100")
          if "pull_request" not in i and i["state_reason"] != "not_planned"]
milestones = get(f"/repos/{REPO}/milestones?state=all")
today = datetime.now(KST).date()

lines = ["# 스프린트 지표 분석", "", f"_{datetime.now(KST):%Y-%m-%d %H:%M} KST 자동 생성_", ""]

# 1. Cycle Time: 이슈가 열린 뒤 닫힐 때까지 걸린 시간
lines += ["## Cycle Time", "", "| 이슈 | 포인트 | Cycle Time |", "|---|---|---|"]
cycle_hours = []
for i in sorted(filter(is_done, issues), key=lambda i: i["number"]):
    hours = (to_time(i["closed_at"]) - to_time(i["created_at"])).total_seconds() / 3600
    cycle_hours.append(hours)
    lines.append(f"| #{i['number']} {i['title']} | {points(i)} | {hours:.1f}시간 |")
if cycle_hours:
    lines += ["", f"평균 Cycle Time: **{sum(cycle_hours) / len(cycle_hours):.1f}시간** ({len(cycle_hours)}건)"]

# 2. Velocity: 스프린트마다 계획한 포인트와 완료한 포인트
lines += ["", "## Velocity", "", "| 스프린트 | 계획 포인트 | 완료 포인트 |", "|---|---|---|"]
for ms in milestones:
    mine = [i for i in issues if i["milestone"] and i["milestone"]["number"] == ms["number"]]
    planned = sum(points(i) for i in mine)
    done = sum(points(i) for i in mine if is_done(i))
    lines.append(f"| {ms['title']} | {planned} | {done} |")

# 3. Burndown: 스프린트 동안 날마다 남은 포인트
lines += ["", "## Burndown"]
for ms in milestones:
    mine = [i for i in issues if i["milestone"] and i["milestone"]["number"] == ms["number"]]
    total = sum(points(i) for i in mine)
    end = to_time(ms["due_on"]).astimezone(KST).date()
    start = end - timedelta(days=13)
    lines += ["", f"### {ms['title']}", "", "| 날짜 | 이상적으로 남은 포인트 | 실제로 남은 포인트 |", "|---|---|---|"]
    for n in range(14):
        day = start + timedelta(days=n)
        ideal = round(total * (13 - n) / 13, 1)
        actual = ""
        if day <= today:
            finished = sum(points(i) for i in mine
                           if is_done(i) and to_time(i["closed_at"]).astimezone(KST).date() <= day)
            actual = total - finished
        lines.append(f"| {day:%m-%d} | {ideal} | {actual} |")

with open("week03/ANALYSIS.md", "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
print("분석 생성: week03/ANALYSIS.md")
