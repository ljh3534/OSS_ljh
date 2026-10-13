#!/usr/bin/env python3
"""이슈·마일스톤 데이터로 Cycle Time, Velocity, Burndown을 계산해 week03/ANALYSIS.md를 만든다.

스토리 포인트는 `sp: N` 라벨에서 읽는다. 스프린트는 직전 마일스톤 마감 다음 날(첫 스프린트는 마일스톤 생성일)에 시작해 마감일에 끝난다고 본다.
"""
import os
import statistics
from datetime import datetime, timedelta, timezone
from pathlib import Path

from collect_dora import REPO, api, parse

OUTPUT = Path("week03/ANALYSIS.md")
KST = timezone(timedelta(hours=9))


def points(issue):
    for label in issue["labels"]:
        if label["name"].startswith("sp:"):
            return int(label["name"].split(":")[1])
    return 0


def duration(h):
    if h * 60 < 1:
        return f"{h * 3600:.0f}초"
    if h < 1:
        return f"{h * 60:.0f}분"
    if h < 48:
        return f"{h:.1f}시간"
    return f"{h / 24:.1f}일"


def burndown(milestone, issues, today, start):
    """(날짜, 이상적 잔여, 실제 잔여) 목록. 실제 잔여는 그날 끝 기준이며 미래 날짜는 None."""
    end = parse(milestone["due_on"]).astimezone(KST).date()
    total = sum(points(i) for i in issues)
    days = (end - start).days
    rows = []
    for n in range(days + 1):
        day = start + timedelta(days=n)
        ideal = round(total * (1 - n / days), 1) if days else 0
        done = sum(points(i) for i in issues
                   if i["closed_at"] and parse(i["closed_at"]).astimezone(KST).date() <= day)
        rows.append((day, ideal, total - done if day <= today else None))
    return rows


def main():
    now = datetime.now(timezone.utc)
    today = now.astimezone(KST).date()
    issues = [i for i in api(f"/repos/{REPO}/issues", state="all", per_page=100) if "pull_request" not in i]
    milestones = sorted(api(f"/repos/{REPO}/milestones", state="all"), key=lambda m: m["number"])
    closed = [i for i in issues if i["closed_at"]]

    lines = [
        "# 스프린트 지표 분석",
        "",
        f"_{now.astimezone(KST):%Y-%m-%d %H:%M} KST 기준 · `scripts/sprint_metrics.py`가 자동 생성_",
        "",
        "## Cycle Time",
        "",
        "이슈 생성부터 종료까지 걸린 시간입니다. "
        "(보드의 In Progress 진입 시각은 API로 얻기 어려워 생성 시각을 시작점으로 사용)",
        "",
    ]
    if closed:
        times = sorted((parse(i["closed_at"]) - parse(i["created_at"])).total_seconds() / 3600 for i in closed)
        lines += [
            "| 완료 이슈 | 평균 | 중앙값 | 최소 | 최대 |",
            "|---|---|---|---|---|",
            f"| {len(times)}건 | {duration(statistics.mean(times))} | {duration(statistics.median(times))} | "
            f"{duration(times[0])} | {duration(times[-1])} |",
            "",
            "| 이슈 | 포인트 | Cycle Time |",
            "|---|---|---|",
        ]
        for i in sorted(closed, key=lambda i: i["number"]):
            h = (parse(i["closed_at"]) - parse(i["created_at"])).total_seconds() / 3600
            lines.append(f"| [#{i['number']}]({i['html_url']}) {i['title']} | {points(i)} | {duration(h)} |")
    else:
        lines.append("아직 완료된 이슈가 없습니다.")

    lines += ["", "## Velocity", "", "스프린트(마일스톤)별 계획·완료 스토리 포인트입니다.", "",
              "| 스프린트 | 마감 | 이슈 (완료/전체) | 계획 포인트 | 완료 포인트 | 달성률 |", "|---|---|---|---|---|---|"]
    by_sprint = {}
    for m in milestones:
        mine = [i for i in issues if i["milestone"] and i["milestone"]["number"] == m["number"]]
        by_sprint[m["number"]] = mine
        planned = sum(points(i) for i in mine)
        done = sum(points(i) for i in mine if i["closed_at"])
        rate = f"{done / planned * 100:.0f}%" if planned else "—"
        due = parse(m["due_on"]).astimezone(KST).strftime("%m-%d") if m["due_on"] else "—"
        lines.append(f"| {m['title']} | {due} | {sum(1 for i in mine if i['closed_at'])}/{len(mine)} | "
                     f"{planned} | {done} | {rate} |")

    lines += ["", "## Burndown", ""]
    previous_due = None
    for m in milestones:
        if not m["due_on"] or not by_sprint[m["number"]]:
            continue
        start = previous_due + timedelta(days=1) if previous_due else parse(m["created_at"]).astimezone(KST).date()
        previous_due = parse(m["due_on"]).astimezone(KST).date()
        rows = burndown(m, by_sprint[m["number"]], today, start)
        shown = [r for r in rows if r[2] is not None]
        lines += [f"### {m['title']}", ""]
        if len(shown) >= 2:
            labels = ", ".join(f'"{d:%m/%d}"' for d, _, _ in shown)
            lines += [
                "```mermaid",
                "xychart-beta",
                '    title "남은 스토리 포인트 (선 1: 이상적, 선 2: 실제)"',
                f"    x-axis [{labels}]",
                f'    y-axis "포인트" 0 --> {rows[0][1]:g}',
                f"    line [{', '.join(f'{ideal:g}' for _, ideal, _ in shown)}]",
                f"    line [{', '.join(str(actual) for _, _, actual in shown)}]",
                "```",
                "",
            ]
        lines += ["| 날짜 | 이상적 잔여 | 실제 잔여 |", "|---|---|---|"]
        lines += [f"| {d:%m-%d} | {ideal:g} | {'' if actual is None else actual} |" for d, ideal, actual in rows]
        lines.append("")

    OUTPUT.write_text("\n".join(lines))
    print(f"분석 생성: {OUTPUT}")


if __name__ == "__main__":
    if not REPO:
        raise SystemExit("GITHUB_REPOSITORY 환경 변수가 필요합니다")
    main()
