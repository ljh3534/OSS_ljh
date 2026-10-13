# 2주차 — DORA 메트릭 수집 자동화

GitHub Actions로 이 저장소의 DORA 4대 지표를 자동 수집하고, Chart.js 대시보드와 주간 보고서로 보여 줍니다.

- 대시보드: <https://ljh3534.github.io/OSS_ljh/>
- 워크플로우 실행 기록: <https://github.com/ljh3534/OSS_ljh/actions/workflows/dora-metrics.yml>
- 주간 보고서: [reports/weekly](../reports/weekly)

![DORA Lens 대시보드](../docs/assets/dashboard.png)

## 구성

```
push (main) ──▶ Deploy 워크플로우 ──▶ GitHub Pages 배포 (github-pages 환경에 Deployment 기록)
                      │
                      ▼ 완료되면 실행 (+ 매주 월요일 09:00 KST, 수동 실행)
               DORA Metrics 워크플로우
                 1. scripts/collect_dora.py   → docs/data/metrics.json, history.json
                 2. scripts/render_report.py  → reports/weekly/YYYY-Www.md, README 요약 표
                 3. JSON·보고서를 아티팩트로 업로드 (90일 보관)
                 4. 변경된 파일을 main에 커밋
```

| 파일 | 역할 |
|---|---|
| [.github/workflows/deploy.yml](../.github/workflows/deploy.yml) | `docs/`를 GitHub Pages로 배포 |
| [.github/workflows/dora-metrics.yml](../.github/workflows/dora-metrics.yml) | 지표 수집, 아티팩트 저장, 보고서 생성·커밋 |
| [scripts/collect_dora.py](../scripts/collect_dora.py) | GitHub REST API로 4대 지표 계산 (Python 표준 라이브러리만 사용) |
| [scripts/render_report.py](../scripts/render_report.py) | 주간 보고서와 README 요약 표 생성 |
| [docs/index.html](../docs/index.html) | Chart.js 대시보드 |

## 지표 정의

집계 기간은 최근 28일입니다(수동 실행 시 변경 가능).

| 지표 | 이 저장소에서의 정의 | 데이터 원천 |
|---|---|---|
| Deployment Frequency | `github-pages` 환경에 성공한 배포 횟수 ÷ 기간(주) | Deployments API |
| Lead Time for Changes | 커밋 시각 → 그 커밋이 처음 포함된 배포의 완료 시각. 커밋별 값의 중앙값 | Deployments, Compare API |
| MTTR | `incident` 라벨 이슈의 생성 → 종료 시간 평균 | Issues API |
| Change Failure Rate | (실패한 배포 + 장애를 일으킨 배포) ÷ 전체 배포 | Deployments, Issues API |

세부 규칙:

- 배포에 포함된 커밋은 직전 성공 배포와의 차이(compare)로 구합니다. 수집 워크플로우가 올리는 봇 커밋은 변경으로 세지 않습니다.
- 장애는 발생 시각 직전에 완료된 배포가 원인이라고 봅니다.
- 등급(Elite/High/Medium/Low)은 DORA 보고서의 기준을 단순화해 적용했습니다.

| 등급 | Deployment Frequency | Lead Time | MTTR | Change Failure Rate |
|---|---|---|---|---|
| Elite | 주 7회 이상 | 1일 이하 | 1시간 이하 | 15% 이하 |
| High | 주 1회 이상 | 1주 이하 | 1일 이하 | 30% 이하 |
| Medium | 월 1회 이상 | 1개월 이하 | 1주 이하 | 45% 이하 |
| Low | 그 미만 | 그 초과 | 그 초과 | 그 초과 |

## (선택과제) JSON 아티팩트와 주간 보고서

- 워크플로우 실행마다 `dora-metrics-<실행 번호>` 아티팩트에 `metrics.json`, `history.json`, 주간 보고서가 저장됩니다.
- `reports/weekly/YYYY-Www.md`가 자동 생성·커밋되며, 이전 주 스냅샷이 있으면 전주 대비 변화를 함께 표시합니다.
- 같은 내용이 워크플로우 실행 화면의 Summary와 저장소 [README](../README.md)의 "DORA 지표 현황" 표에도 반영됩니다.

## 참고: 현재 데이터에 대해

- 저장소를 만든 직후라 배포·커밋이 하루에 몰려 있습니다. Lead Time이 분 단위로 짧게 나오는 것은 커밋 직후 바로 배포했기 때문입니다.
- MTTR과 Change Failure Rate가 계산되는지 확인하려고 장애 대응 훈련 이슈([#17](https://github.com/ljh3534/OSS_ljh/issues/17))를 등록했습니다. 실제 장애가 아니며, 이슈에서 `incident` 라벨을 떼면 지표에서 제외됩니다.

## 로컬 실행

```bash
export GITHUB_REPOSITORY=ljh3534/OSS_ljh
export GITHUB_TOKEN=$(gh auth token)
python3 scripts/collect_dora.py && python3 scripts/render_report.py
python3 -m http.server -d docs 8000   # http://localhost:8000
```
