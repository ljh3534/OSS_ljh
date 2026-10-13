# OSS_ljh

오픈소스SW 수업 과제 저장소입니다. 1~3주차 과제를 하나의 학기 프로젝트(**DORA Lens** — GitHub 저장소의 DORA 지표를 자동 수집·시각화하는 도구)로 이어서 진행합니다.

| 주차 | 과제 | 결과물 |
|---|---|---|
| 1주차 | 개발 환경 설정 및 프로젝트 제안 | [환경 설정 기록](week01/README.md) · [프로젝트 제안서](week01/PROPOSAL.md) |
| 2주차 | DORA 메트릭 수집 자동화 | [설명](week02/README.md) · [워크플로우](.github/workflows/dora-metrics.yml) · [대시보드](https://ljh3534.github.io/OSS_ljh/) · [주간 보고서](reports/weekly) |
| 3주차 | GitHub Projects 계획·추적 체계 | [설명](week03/README.md) · [이슈](https://github.com/ljh3534/OSS_ljh/issues?q=is%3Aissue) · [마일스톤](https://github.com/ljh3534/OSS_ljh/milestones) |

## DORA 지표 현황

<!-- DORA:START -->
_2026-09-15 ~ 2026-10-13 기준, 자동 생성됨 · [대시보드](https://ljh3534.github.io/OSS_ljh/) · [이번 주 보고서](reports/weekly/2026-W42.md)_

| 지표 | 값 | 등급 | 전주 대비 |
|---|---|---|---|
| Deployment Frequency | 주 0.5회 (기간 내 2회) | Medium | — |
| Lead Time for Changes | 29초 (중앙값, 커밋 7개) | Elite | — |
| MTTR | — (해결 0건, 미해결 0건) | — | — |
| Change Failure Rate | 0% (0/2) | Elite | — |
<!-- DORA:END -->

## 저장소 구조

```
.github/
  ISSUE_TEMPLATE/      Bug / Feature 이슈 템플릿
  workflows/           배포(deploy.yml), DORA 수집(dora-metrics.yml)
docs/                  Chart.js 대시보드 (GitHub Pages로 배포)
reports/weekly/        자동 생성되는 주간 DORA 보고서
scripts/               지표 수집·분석 스크립트 (Python 표준 라이브러리만 사용)
week01/ week02/ week03/  주차별 과제 설명
```
