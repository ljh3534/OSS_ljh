"""metrics.json을 읽어 주간 보고서(reports/weekly)를 만들고 README의 요약 표를 바꾼다."""
import json
import os
from datetime import datetime, timedelta, timezone

KST = timezone(timedelta(hours=9))


def duration(hours):
    """시간(소수)을 '29초', '3분', '1.5시간', '2.0일'처럼 읽기 쉬운 글자로 바꾼다."""
    if hours is None:
        return "—"
    if hours * 60 < 1:
        return f"{hours * 3600:.0f}초"
    if hours < 1:
        return f"{hours * 60:.0f}분"
    if hours < 48:
        return f"{hours:.1f}시간"
    return f"{hours / 24:.1f}일"


with open("docs/data/metrics.json", encoding="utf-8") as f:
    m = json.load(f)

made = datetime.fromisoformat(m["generated_at"]).astimezone(KST)
year, week, _ = made.isocalendar()
cfr = "—" if m["change_failure_rate"] is None else f"{m['change_failure_rate']}%"

summary = [
    "| 지표 | 값 |",
    "|---|---|",
    f"| Deployment Frequency | 주 {m['deployments_per_week']}회 (최근 {m['days']}일 동안 {len(m['deployments'])}회) |",
    f"| Lead Time for Changes | {duration(m['lead_time_hours'])} (중앙값) |",
    f"| MTTR | {duration(m['mttr_hours'])} (장애 {len(m['incidents'])}건) |",
    f"| Change Failure Rate | {cfr} |",
]

report = [f"# 주간 DORA 보고서 — {year}년 {week}주차", "",
          f"{made:%Y-%m-%d %H:%M} KST 기준, 최근 {m['days']}일", "", "## 요약", "", *summary, "",
          "## 배포 내역", "", "| 배포 시각 (KST) | 커밋 | 새 커밋 수 | Lead Time |", "|---|---|---|---|"]
for d in reversed(m["deployments"]):
    time = datetime.fromisoformat(d["time"]).astimezone(KST)
    report.append(f"| {time:%m-%d %H:%M} | `{d['sha']}` | {d['commits']} | {duration(d['lead_time_hours'])} |")
report += ["", "## 장애 내역", ""]
if m["incidents"]:
    report += ["| 이슈 | 복구까지 |", "|---|---|"]
    for i in m["incidents"]:
        report.append(f"| #{i['number']} {i['title']} | {duration(i['hours_to_restore'])} |")
else:
    report.append("장애(`incident` 라벨 이슈)가 없습니다.")

os.makedirs("reports/weekly", exist_ok=True)
path = f"reports/weekly/{year}-W{week:02d}.md"
with open(path, "w", encoding="utf-8") as f:
    f.write("\n".join(report) + "\n")

# README.md의 <!-- DORA:START --> 와 <!-- DORA:END --> 사이를 새 표로 바꾼다
with open("README.md", encoding="utf-8") as f:
    readme = f.read()
start = readme.index("<!-- DORA:START -->") + len("<!-- DORA:START -->")
end = readme.index("<!-- DORA:END -->")
block = f"\n_{made:%Y-%m-%d %H:%M} KST 자동 갱신 · [이번 주 보고서]({path})_\n\n" + "\n".join(summary) + "\n"
with open("README.md", "w", encoding="utf-8") as f:
    f.write(readme[:start] + block + readme[end:])

print("보고서 생성:", path)
