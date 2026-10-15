# 2주차 — DORA 메트릭 수집 자동화

GitHub Actions로 이 저장소(TimeFit 개발 저장소)의 DORA 4대 지표를 자동 수집하고, Chart.js 대시보드와 주간 보고서로 보여 줍니다.

- 대시보드: <https://ljh3534.github.io/OSS_ljh/>
- 워크플로우 실행 기록: <https://github.com/ljh3534/OSS_ljh/actions/workflows/metrics.yml>
- 주간 보고서: [reports/weekly](../reports/weekly)

![DORA 대시보드](../docs/assets/dashboard.png)

## 동작 순서

1. `main` 브랜치에 푸시하면 **Deploy** 워크플로우가 `docs/` 폴더를 GitHub Pages에 배포합니다. 이때 GitHub에 배포 기록(Deployment)이 하나 남습니다.
2. Deploy가 끝나면 **DORA Metrics** 워크플로우(`metrics.yml`)가 이어서 실행됩니다. Pull Request가 main에 병합될 때, 매주 월요일 오전 9시, Actions 탭에서 수동 실행할 때도 실행됩니다.
3. `scripts/collect_dora.py`가 GitHub API로 배포·커밋·이슈를 읽어 지표를 계산하고 `docs/data/metrics.json`에 저장합니다.
4. `scripts/render_report.py`가 주간 보고서(`reports/weekly/YYYY-Www.md`)를 만들고 README의 요약 표를 갱신합니다.
5. 결과 파일을 아티팩트로 올리고, 저장소에 커밋합니다. 월요일 정기 실행(또는 수동 실행) 때는 주간 보고서를 `report` 라벨 Issue로도 등록합니다.
6. 대시보드(`docs/index.html`)는 저장소의 최신 `metrics.json`을 읽어 화면에 그립니다.

| 파일 | 역할 |
|---|---|
| [.github/workflows/deploy.yml](../.github/workflows/deploy.yml) | `docs/`를 GitHub Pages로 배포 |
| [.github/workflows/metrics.yml](../.github/workflows/metrics.yml) | 지표 수집 → 보고서 생성 → 아티팩트 업로드 → 보고서 Issue 등록 → 커밋 |
| [scripts/collect_dora.py](../scripts/collect_dora.py) | GitHub API로 4대 지표 계산 (Python 표준 라이브러리만 사용) |
| [scripts/render_report.py](../scripts/render_report.py) | 주간 보고서와 README 요약 표 생성 |
| [docs/index.html](../docs/index.html) | Chart.js 대시보드 |

## 지표 정의

최근 28일 동안의 데이터로 계산합니다.

| 지표 | 계산 방법 | 사용한 API |
|---|---|---|
| Deployment Frequency | 성공한 GitHub Pages 배포 횟수 ÷ 4주 | Deployments |
| Lead Time for Changes | 배포마다 직전 배포 이후 새로 들어간 커밋을 찾고, 커밋 시각부터 배포 완료까지 걸린 시간의 중앙값 | Deployments, Compare |
| MTTR | `incident` 라벨이 붙은 이슈가 열린 시각부터 닫힌 시각까지의 평균 | Issues |
| Change Failure Rate | (실패한 배포 + 장애를 일으킨 배포) ÷ 전체 배포 × 100. 장애는 `incident` 라벨 이슈로 센다 | Deployments, Issues |

- 첫 배포는 비교할 직전 배포가 없어서 Lead Time을 계산하지 않습니다.
- 지표 갱신 워크플로우가 올리는 봇 커밋은 코드 변경이 아니므로 Lead Time에서 뺍니다.

### 성과 수준

강의자료의 DORA 성과 수준표로 등급을 매겨 대시보드와 보고서에 함께 표시합니다.

| 수준 | Deployment Frequency | Lead Time | MTTR | Change Failure Rate |
|---|---|---|---|---|
| Elite | 하루에 여러 번 | 1시간 미만 | 1시간 미만 | 0~15% |
| High | 주 1회 ~ 일 1회 | 1주 미만 | 1일 미만 | 16~30% |
| Medium | 월 1회 ~ 주 1회 | 1개월 미만 | 1주 미만 | 31~45% |
| Low | 월 1회 미만 | 1개월 이상 | 1주 이상 | 46% 이상 |

## (선택과제) JSON 아티팩트와 주간 보고서

- 워크플로우를 실행할 때마다 `dora-metrics-<실행 번호>` 아티팩트로 `metrics.json`과 주간 보고서가 저장됩니다 (90일 보관).
- 매주 월요일에는 같은 보고서가 [`report` 라벨 Issue](https://github.com/ljh3534/OSS_ljh/issues?q=label%3Areport)로 등록됩니다. 같은 주에 다시 실행되면 새로 만들지 않고 내용만 갱신합니다.
- `reports/weekly/YYYY-Www.md` 보고서가 자동으로 만들어져 커밋되고, 저장소 [README](../README.md)의 "DORA 지표 현황" 표도 함께 바뀝니다.

## 현재 데이터에 대해

- 저장소를 만든 직후라 배포와 커밋이 며칠에 몰려 있습니다. Lead Time이 초 단위로 짧은 것은 커밋하자마자 바로 푸시해 배포했기 때문입니다.
- 아직 장애(`incident` 라벨 이슈)가 없어서 MTTR은 `—`, Change Failure Rate는 0%로 나옵니다. 장애가 생기면 Bug 템플릿으로 이슈를 만들고 `incident` 라벨을 붙이면 다음 수집 때 반영됩니다.

## 로컬에서 실행하기

```bash
export GITHUB_REPOSITORY=ljh3534/OSS_ljh
export GITHUB_TOKEN=$(gh auth token)
python3 scripts/collect_dora.py
python3 scripts/render_report.py
python3 -m http.server -d docs 8000
```

마지막 명령을 실행한 뒤 브라우저에서 <http://localhost:8000>을 열면 대시보드를 볼 수 있습니다.
