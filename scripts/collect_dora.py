"""GitHub API로 DORA 4대 지표를 계산해 docs/data/metrics.json에 저장한다."""
import json
import os
import statistics
import urllib.request
from datetime import datetime, timedelta, timezone

REPO = os.environ["GITHUB_REPOSITORY"]  # 예: ljh3534/OSS_ljh
TOKEN = os.environ.get("GITHUB_TOKEN", "")
DAYS = int(os.environ.get("WINDOW_DAYS", "28"))  # 최근 며칠을 집계할지


def get(path):
    """GitHub API를 호출해 응답 JSON을 돌려준다."""
    req = urllib.request.Request("https://api.github.com" + path)
    req.add_header("Accept", "application/vnd.github+json")
    if TOKEN:
        req.add_header("Authorization", "Bearer " + TOKEN)
    with urllib.request.urlopen(req) as res:
        return json.load(res)


def to_time(text):
    """'2026-10-13T06:16:32Z' 같은 문자열을 datetime으로 바꾼다."""
    return datetime.fromisoformat(text.replace("Z", "+00:00"))


def hours_between(start, end):
    return round((end - start).total_seconds() / 3600, 3)


now = datetime.now(timezone.utc)
since = now - timedelta(days=DAYS)

def level(value, elite, high, medium):
    """강의자료의 DORA 성과 수준표로 등급을 매긴다. (값이 작을수록 좋은 지표용)"""
    if value is None:
        return None
    if value < elite:
        return "Elite"
    if value < high:
        return "High"
    if value < medium:
        return "Medium"
    return "Low"


# 1. 배포 목록 (GitHub Pages에 배포될 때마다 하나씩 생긴다)
#    상태가 success면 성공한 배포, failure/error면 실패한 배포
deployments = []
failed_deployments = []
for d in get(f"/repos/{REPO}/deployments?environment=github-pages&per_page=100"):
    statuses = get(f"/repos/{REPO}/deployments/{d['id']}/statuses")
    success = [s for s in statuses if s["state"] == "success"]
    failure = [s for s in statuses if s["state"] in ("failure", "error")]
    if success:
        deployments.append({"sha": d["sha"], "time": to_time(success[-1]["created_at"])})
    elif failure:
        failed_deployments.append(to_time(failure[0]["created_at"]))
deployments.sort(key=lambda d: d["time"])  # 오래된 배포부터

# 2. Lead Time: 직전 배포 이후 새로 들어간 커밋들이, 커밋된 시각부터 배포될 때까지 걸린 시간
#    (첫 배포는 비교할 직전 배포가 없어서 계산하지 않는다)
lead_times = []
for prev, cur in zip(deployments, deployments[1:]):
    cur["lead_times"] = []
    if cur["time"] < since:
        continue
    for c in get(f"/repos/{REPO}/compare/{prev['sha']}...{cur['sha']}")["commits"]:
        if "[bot]" in c["commit"]["author"]["name"]:
            continue  # 지표를 갱신하는 봇 커밋은 코드 변경이 아니므로 제외
        committed = to_time(c["commit"]["committer"]["date"])
        cur["lead_times"].append(hours_between(committed, cur["time"]))
    lead_times += cur["lead_times"]

recent = [d for d in deployments if d["time"] >= since]
recent_failed = [t for t in failed_deployments if t >= since]

# 3. 장애: incident 라벨이 붙은 이슈. 이슈가 열린 시각 → 닫힌 시각을 복구 시간으로 본다
incidents = []
for issue in get(f"/repos/{REPO}/issues?labels=incident&state=all&per_page=100"):
    opened = to_time(issue["created_at"])
    if opened < since:
        continue
    closed = to_time(issue["closed_at"]) if issue["closed_at"] else None
    incidents.append({
        "number": issue["number"],
        "title": issue["title"],
        "opened": opened.isoformat(),
        "hours_to_restore": hours_between(opened, closed) if closed else None,
    })
restore_times = [i["hours_to_restore"] for i in incidents if i["hours_to_restore"] is not None]

# 4. 계산
#    변경 실패율 = (실패한 배포 + 장애를 일으킨 배포) ÷ 전체 배포 × 100
total_deployments = len(recent) + len(recent_failed)
per_week = round(len(recent) / (DAYS / 7), 2)
lead_time = statistics.median(lead_times) if lead_times else None
mttr = round(statistics.mean(restore_times), 3) if restore_times else None
cfr = round((len(recent_failed) + len(incidents)) / total_deployments * 100, 1) if total_deployments else None

# 5. 결과 저장
result = {
    "repository": REPO,
    "generated_at": now.isoformat(timespec="seconds"),
    "days": DAYS,
    "deployments_per_week": per_week,
    "failed_deployments": len(recent_failed),
    "lead_time_hours": lead_time,
    "mttr_hours": mttr,
    "change_failure_rate": cfr,
    # 강의자료의 성과 수준표 기준 (시간 단위: 1시간, 1일=24, 1주=168, 1개월=720)
    "levels": {
        # 배포 빈도는 클수록 좋으므로 "배포 간격(일)"으로 바꿔 비교: 하루 여러 번 / 주 1회 / 월 1회
        "deployment_frequency": level(7 / per_week if per_week else None, 1, 7, 30) if recent else None,
        "lead_time": level(lead_time, 1, 168, 720),
        "mttr": level(mttr, 1, 24, 168),
        "change_failure_rate": level(cfr, 16, 31, 46),
    },
    "deployments": [
        {
            "sha": d["sha"][:7],
            "time": d["time"].isoformat(),
            "commits": len(d.get("lead_times", [])),
            "lead_time_hours": statistics.median(d["lead_times"]) if d.get("lead_times") else None,
        }
        for d in recent
    ],
    "incidents": incidents,
}
os.makedirs("docs/data", exist_ok=True)
with open("docs/data/metrics.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"배포 {len(recent)}회, 주당 {result['deployments_per_week']}회")
print(f"Lead Time 중앙값 {result['lead_time_hours']}시간, MTTR {result['mttr_hours']}시간")
print(f"변경 실패율 {result['change_failure_rate']}%")
