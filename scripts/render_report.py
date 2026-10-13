#!/usr/bin/env python3
"""metrics.json / history.json으로 주간 보고서와 README 요약을 만든다."""
import json
import os
import re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

DATA_DIR = Path(os.environ.get("OUT_DIR", "docs/data"))
REPORT_DIR = Path("reports/weekly")
README = Path("README.md")
KST = timezone(timedelta(hours=9))
START, END = "<!-- DORA:START -->", "<!-- DORA:END -->"


def duration(h):
    if h is None:
        return "—"
    if h < 1:
        return f"{h * 60:.0f}분"
    if h < 48:
        return f"{h:.1f}시간"
    return f"{h / 24:.1f}일"


def change(now, before, unit="", lower_is_better=True):
    """전주 대비 변화. 좋아졌으면 ▼/▲ 뒤에 (개선), 나빠졌으면 (악화)를 붙인다."""
    if now is None or before is None:
        return "—"
    diff = now - before
    if abs(diff) < 1e-9:
        return "변화 없음"
    better = (diff < 0) == lower_is_better
    text = duration(abs(diff)) if unit == "h" else f"{abs(diff):g}{unit}"
    return f"{'▲' if diff > 0 else '▼'} {text} ({'개선' if better else '악화'})"


def kst(ts):
    return datetime.fromisoformat(ts).astimezone(KST).strftime("%m-%d %H:%M")


def main():
    result = json.loads((DATA_DIR / "metrics.json").read_text())
    history = json.loads((DATA_DIR / "history.json").read_text())
    m = result["metrics"]
    df, lt, mttr, cfr = m["deployment_frequency"], m["lead_time"], m["mttr"], m["change_failure_rate"]
    repo = result["repository"]
    owner, name = repo.split("/")
    today = date.fromisoformat(result["window"]["to"])
    year, week, _ = today.isocalendar()

    # 비교 기준: 이번 주 이전에 수집된 가장 최근 스냅샷
    earlier = [h for h in history if date.fromisoformat(h["date"]).isocalendar()[:2] < (year, week)]
    prev = earlier[-1] if earlier else {}

    cfr_text = "—" if cfr["percent"] is None else f"{cfr['percent']:g}% ({cfr['failed']}/{cfr['total']})"
    rows = [
        ("Deployment Frequency", f"주 {df['per_week']:g}회 (기간 내 {df['count']}회)", df["level"],
         change(df["per_week"], prev.get("deployments_per_week"), "회/주", lower_is_better=False)),
        ("Lead Time for Changes", f"{duration(lt['median_hours'])} (중앙값, 커밋 {lt['commits']}개)", lt["level"],
         change(lt["median_hours"], prev.get("lead_time_hours"), "h")),
        ("MTTR", f"{duration(mttr['mean_hours'])} (해결 {mttr['resolved']}건, 미해결 {mttr['open']}건)", mttr["level"],
         change(mttr["mean_hours"], prev.get("mttr_hours"), "h")),
        ("Change Failure Rate", cfr_text, cfr["level"],
         change(cfr["percent"], prev.get("change_failure_rate"), "%p")),
    ]
    table = ["| 지표 | 값 | 등급 | 전주 대비 |", "|---|---|---|---|"]
    table += [f"| {a} | {b} | {c or '—'} | {d} |" for a, b, c, d in rows]

    lines = [
        f"# 주간 DORA 보고서 — {year}년 {week}주차",
        "",
        f"- 저장소: [{repo}](https://github.com/{repo})",
        f"- 집계 기간: {result['window']['from']} ~ {result['window']['to']} (최근 {result['window']['days']}일)",
        f"- 생성 시각: {datetime.fromisoformat(result['generated_at']).astimezone(KST):%Y-%m-%d %H:%M} KST",
        f"- 비교 기준: {prev['date'] + ' 스냅샷' if prev else '이전 주 데이터 없음'}",
        "",
        "## 요약",
        "",
        *table,
        "",
        "## 배포 내역",
        "",
    ]
    if result["deployments"]:
        lines += ["| 완료 시각 (KST) | 커밋 | 결과 | 포함 커밋 수 | Lead Time | 연결된 장애 |", "|---|---|---|---|---|---|"]
        for d in reversed(result["deployments"]):
            incident = f"#{d['incident']}" if d["incident"] else ""
            ok = "성공" if d["status"] == "success" else "실패"
            lines.append(f"| {kst(d['finished_at'])} | `{d['sha']}` | {ok} | {d['commits']} | "
                         f"{duration(d['lead_time_hours'])} | {incident} |")
    else:
        lines.append("기간 내 배포가 없습니다.")
    lines += ["", "## 장애 내역", ""]
    if result["incidents"]:
        lines += ["| 이슈 | 발생 (KST) | 복구까지 | 원인 배포 |", "|---|---|---|---|"]
        for i in result["incidents"]:
            restore = duration(i["hours_to_restore"]) if i["closed_at"] else "미해결"
            lines.append(f"| [#{i['number']}]({i['url']}) {i['title']} | {kst(i['created_at'])} | "
                         f"{restore} | `{i['deployment_sha'] or '—'}` |")
    else:
        lines.append("기간 내 장애(`incident` 라벨 이슈)가 없습니다.")
    lines.append("")

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report = REPORT_DIR / f"{year}-W{week:02d}.md"
    report.write_text("\n".join(lines))

    block = "\n".join([
        START,
        f"_{result['window']['from']} ~ {result['window']['to']} 기준, 자동 생성됨 · "
        f"[대시보드](https://{owner}.github.io/{name}/) · [이번 주 보고서]({report.as_posix()})_",
        "",
        *table,
        END,
    ])
    text = README.read_text()
    if START in text:
        text = re.sub(f"{re.escape(START)}.*?{re.escape(END)}", lambda _: block, text, flags=re.S)
        README.write_text(text)
    print(f"보고서 생성: {report}")


if __name__ == "__main__":
    main()
