#!/usr/bin/env python3
"""GitHub 저장소의 DORA 4대 지표를 수집해 JSON으로 저장한다.

표준 라이브러리만 사용한다. 환경 변수:
  GITHUB_REPOSITORY  owner/repo (필수)
  GITHUB_TOKEN       API 토큰 (없으면 비인증 호출)
  WINDOW_DAYS        집계 기간(일), 기본 28
  DEPLOY_ENV         배포로 간주할 Deployment 환경 이름, 기본 github-pages
  INCIDENT_LABEL     장애 이슈 라벨, 기본 incident
  OUT_DIR            출력 폴더, 기본 docs/data
"""
import json
import os
import statistics
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

API = "https://api.github.com"
REPO = os.environ.get("GITHUB_REPOSITORY", "")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
WINDOW_DAYS = int(os.environ.get("WINDOW_DAYS", "28"))
DEPLOY_ENV = os.environ.get("DEPLOY_ENV", "github-pages")
INCIDENT_LABEL = os.environ.get("INCIDENT_LABEL", "incident")
OUT_DIR = Path(os.environ.get("OUT_DIR", "docs/data"))


def api(path, **params):
    """GET 요청. 목록 응답은 Link 헤더를 따라 끝까지 읽는다."""
    url = f"{API}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    items = []
    while url:
        req = urllib.request.Request(url, headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "dora-lens",
        })
        if TOKEN:
            req.add_header("Authorization", f"Bearer {TOKEN}")
        with urllib.request.urlopen(req, timeout=30) as res:
            data = json.load(res)
            link = res.headers.get("Link", "")
        if not isinstance(data, list):
            return data
        items.extend(data)
        url = None
        for part in link.split(","):
            if 'rel="next"' in part:
                url = part[part.index("<") + 1:part.index(">")]
    return items


def parse(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def hours(delta):
    return round(delta.total_seconds() / 3600, 3)


def is_bot(commit):
    login = (commit.get("author") or {}).get("login", "")
    name = commit["commit"]["author"]["name"]
    return login.endswith("[bot]") or name.endswith("[bot]")


def fetch_deployments():
    """환경의 모든 배포를 완료 시각 오름차순으로 반환한다."""
    result = []
    for d in api(f"/repos/{REPO}/deployments", environment=DEPLOY_ENV, per_page=100):
        statuses = api(f"/repos/{REPO}/deployments/{d['id']}/statuses", per_page=100)
        success = [s for s in statuses if s["state"] == "success"]
        failed = [s for s in statuses if s["state"] in ("failure", "error")]
        if success:
            status, finished = "success", min(parse(s["created_at"]) for s in success)
        elif failed:
            status, finished = "failure", max(parse(s["created_at"]) for s in failed)
        else:
            continue  # 아직 진행 중인 배포
        result.append({"id": d["id"], "sha": d["sha"], "status": status, "finished": finished})
    return sorted(result, key=lambda d: d["finished"])


def changes_in(deploy, previous):
    """이 배포로 처음 나간 커밋(봇 커밋 제외)."""
    if previous is None:
        commits = api(f"/repos/{REPO}/commits", sha=deploy["sha"], per_page=100)
    elif previous["sha"] == deploy["sha"]:
        commits = []
    else:
        commits = api(f"/repos/{REPO}/compare/{previous['sha']}...{deploy['sha']}").get("commits", [])
    return [c for c in commits if not is_bot(c)]


def fetch_incidents():
    issues = api(f"/repos/{REPO}/issues", labels=INCIDENT_LABEL, state="all", per_page=100)
    return [i for i in issues if "pull_request" not in i]


def level(metric, value):
    """DORA 벤치마크를 단순화한 등급. 값이 작을수록 좋은 지표는 상한, 배포 빈도는 하한으로 비교한다."""
    if value is None:
        return None
    if metric == "deployment_frequency":  # 주당 배포 횟수
        bounds = [(7, "Elite"), (1, "High"), (0.25, "Medium")]
        return next((name for limit, name in bounds if value >= limit), "Low")
    bounds = {
        "lead_time": [(24, "Elite"), (24 * 7, "High"), (24 * 30, "Medium")],  # 시간
        "mttr": [(1, "Elite"), (24, "High"), (24 * 7, "Medium")],  # 시간
        "change_failure_rate": [(15, "Elite"), (30, "High"), (45, "Medium")],  # %
    }[metric]
    return next((name for limit, name in bounds if value <= limit), "Low")


def collect(now=None):
    now = now or datetime.now(timezone.utc)
    start = now - timedelta(days=WINDOW_DAYS)
    in_window = lambda t: start <= t <= now

    deployments = fetch_deployments()
    successes = [d for d in deployments if d["status"] == "success"]

    # Lead Time for Changes: 커밋 시각 → 그 커밋이 포함된 배포 완료 시각
    lead_times = []
    previous = None
    for d in successes:
        if in_window(d["finished"]):
            commits = changes_in(d, previous)
            d["lead_times"] = [
                hours(d["finished"] - parse(c["commit"]["committer"]["date"])) for c in commits
            ]
            lead_times.extend(d["lead_times"])
        previous = d

    # 장애는 발생 직전에 완료된 배포의 실패로 본다
    incidents = []
    for issue in fetch_incidents():
        created = parse(issue["created_at"])
        closed = parse(issue["closed_at"]) if issue["closed_at"] else None
        cause = next((d for d in reversed(successes) if d["finished"] <= created), None)
        if cause is not None:
            cause["incident"] = issue["number"]
        if in_window(created):
            incidents.append({
                "number": issue["number"],
                "title": issue["title"],
                "url": issue["html_url"],
                "created_at": created.isoformat(),
                "closed_at": closed.isoformat() if closed else None,
                "hours_to_restore": hours(closed - created) if closed else None,
                "deployment_sha": cause["sha"][:7] if cause else None,
            })

    window = [d for d in deployments if in_window(d["finished"])]
    window_ok = [d for d in window if d["status"] == "success"]
    failed = [d for d in window if d["status"] == "failure" or "incident" in d]
    restore = [i["hours_to_restore"] for i in incidents if i["hours_to_restore"] is not None]

    per_week = round(len(window_ok) / (WINDOW_DAYS / 7), 2)
    lead_median = round(statistics.median(lead_times), 3) if lead_times else None
    mttr = round(statistics.mean(restore), 3) if restore else None
    cfr = round(len(failed) / len(window) * 100, 1) if window else None

    daily = {(start + timedelta(days=n + 1)).date().isoformat(): 0 for n in range(WINDOW_DAYS)}
    for d in window_ok:
        key = d["finished"].date().isoformat()
        if key in daily:
            daily[key] += 1

    return {
        "repository": REPO,
        "generated_at": now.isoformat(timespec="seconds"),
        "window": {"days": WINDOW_DAYS, "from": start.date().isoformat(), "to": now.date().isoformat()},
        "environment": DEPLOY_ENV,
        "metrics": {
            "deployment_frequency": {
                "count": len(window_ok),
                "per_week": per_week,
                "level": level("deployment_frequency", per_week if window_ok else None),
            },
            "lead_time": {
                "median_hours": lead_median,
                "mean_hours": round(statistics.mean(lead_times), 3) if lead_times else None,
                "commits": len(lead_times),
                "level": level("lead_time", lead_median),
            },
            "mttr": {
                "mean_hours": mttr,
                "resolved": len(restore),
                "open": len(incidents) - len(restore),
                "level": level("mttr", mttr),
            },
            "change_failure_rate": {
                "percent": cfr,
                "failed": len(failed),
                "total": len(window),
                "level": level("change_failure_rate", cfr),
            },
        },
        "daily_deployments": [{"date": k, "count": v} for k, v in daily.items()],
        "deployments": [
            {
                "sha": d["sha"][:7],
                "finished_at": d["finished"].isoformat(),
                "status": d["status"],
                "commits": len(d.get("lead_times", [])),
                "lead_time_hours": round(statistics.median(d["lead_times"]), 3) if d.get("lead_times") else None,
                "incident": d.get("incident"),
            }
            for d in window
        ],
        "incidents": incidents,
    }


def update_history(result):
    """실행 날짜별 스냅샷을 누적한다. 같은 날 다시 실행하면 그날 값을 덮어쓴다."""
    path = OUT_DIR / "history.json"
    history = json.loads(path.read_text()) if path.exists() else []
    m = result["metrics"]
    entry = {
        "date": result["window"]["to"],
        "deployments_per_week": m["deployment_frequency"]["per_week"],
        "lead_time_hours": m["lead_time"]["median_hours"],
        "mttr_hours": m["mttr"]["mean_hours"],
        "change_failure_rate": m["change_failure_rate"]["percent"],
    }
    history = [h for h in history if h["date"] != entry["date"]] + [entry]
    history.sort(key=lambda h: h["date"])
    path.write_text(json.dumps(history, ensure_ascii=False, indent=2) + "\n")


def main():
    if not REPO:
        sys.exit("GITHUB_REPOSITORY 환경 변수가 필요합니다 (예: owner/repo)")
    try:
        result = collect()
    except urllib.error.HTTPError as e:
        sys.exit(f"GitHub API 오류 {e.code}: {e.url}\n{e.read().decode()[:300]}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "metrics.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    update_history(result)
    print(json.dumps(result["metrics"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
