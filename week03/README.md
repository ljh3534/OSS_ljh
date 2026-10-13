# 3주차 — GitHub Projects 계획·추적 체계

학기 프로젝트(DORA Lens)의 백로그를 GitHub Issues·Milestones·Projects로 구성했습니다.

## 칸반 보드

GitHub Project의 `Status` 필드를 다음 5개 컬럼으로 설정합니다.

| 컬럼 | 의미 | 들어오는 조건 |
|---|---|---|
| Backlog | 아직 스프린트에 넣지 않은 아이디어 | 마일스톤 없음 |
| To Do | 이번 스프린트에 하기로 한 작업 | 스프린트 마일스톤 지정 |
| In Progress | 작업 중 | 담당자가 작업을 시작함 |
| Review | 구현 완료, 확인 대기 | 커밋/PR이 올라옴 |
| Done | 완료 | 이슈 종료 |

## 이슈 템플릿

이슈는 빈 양식 없이 두 템플릿 중 하나로만 등록합니다.

- [Bug](../.github/ISSUE_TEMPLATE/bug_report.yml) — 현상, 재현 방법, 영역, 심각도, 로그
- [Feature](../.github/ISSUE_TEMPLATE/feature_request.yml) — 배경, 완료 조건(체크리스트), 영역, 예상 스토리 포인트

## 라벨 체계

| 분류 | 라벨 | 용도 |
|---|---|---|
| 유형 | `type: bug` `type: feature` `type: docs` `type: chore` | 작업의 성격 (이슈마다 하나) |
| 우선순위 | `priority: high` `priority: medium` `priority: low` | 스프린트 안에서의 처리 순서 |
| 영역 | `area: collector` `area: dashboard` `area: ci` | 어느 부분의 작업인지 |
| 스토리 포인트 | `sp: 1` `sp: 2` `sp: 3` `sp: 5` | 작업 크기 — Velocity·Burndown 계산에 사용 |
| 운영 | `incident` | 운영 장애 — 2주차의 MTTR·Change Failure Rate 계산에 사용 |

## 마일스톤 (스프린트)

| 마일스톤 | 기간 | 목표 |
|---|---|---|
| [Sprint 1 — 수집·대시보드 MVP](https://github.com/ljh3534/OSS_ljh/milestone/1) | 10/13 ~ 10/26 | 지표 자동 수집, 대시보드, 주간 보고서 |
| [Sprint 2 — 정확도·확장](https://github.com/ljh3534/OSS_ljh/milestone/2) | 10/27 ~ 11/09 | 테스트, 다중 저장소, 알림 |

## 백로그

[전체 이슈 목록](https://github.com/ljh3534/OSS_ljh/issues?q=is%3Aissue)에서 확인할 수 있습니다. 스프린트에 넣지 않은 이슈는 마일스톤 없이 Backlog에 둡니다.

## (선택과제) Cycle Time · Velocity · Burndown

[ANALYSIS.md](ANALYSIS.md) — [`scripts/sprint_metrics.py`](../scripts/sprint_metrics.py)가 이슈와 마일스톤 데이터로 계산해 자동 생성합니다. DORA 수집 워크플로우가 실행될 때마다 함께 갱신됩니다.
