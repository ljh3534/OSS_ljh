# 3주차 — GitHub Projects 계획·추적 체계

학기 프로젝트 [TimeFit](../week01/PROPOSAL.md)(시간표 자동 조합 도우미)의 백로그를 GitHub Issues·Milestones·Projects로 구성했습니다.

## 칸반 보드

**[TimeFit 프로젝트 보드](https://github.com/users/ljh3534/projects/1)**

GitHub Project의 `Status` 필드를 다음 5개 컬럼으로 설정했습니다.

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
| 영역 | `area: app` `area: ci` `area: collector` `area: dashboard` | 어느 부분의 작업인지 (앱, 워크플로우, DORA 수집기, DORA 대시보드) |
| 스토리 포인트 | `sp: 1` `sp: 2` `sp: 3` `sp: 5` | 작업 크기 — Velocity·Burndown 계산에 사용 |
| 운영 | `incident` | 운영 장애 — 2주차의 MTTR·Change Failure Rate 계산에 사용 |

## 마일스톤 (스프린트)

| 마일스톤 | 기간 | 목표 |
|---|---|---|
| [Sprint 1 — 개발 인프라 (배포·DORA·백로그)](https://github.com/ljh3534/OSS_ljh/milestone/1) | 10/13 ~ 10/26 | 배포 파이프라인, DORA 지표 자동 수집, 이슈 템플릿·라벨 |
| [Sprint 2 — TimeFit MVP](https://github.com/ljh3534/OSS_ljh/milestone/2) | 10/27 ~ 11/09 | 과목 입력, 충돌 없는 조합 생성, 시간표 표시 |

## 백로그

[전체 이슈 목록](https://github.com/ljh3534/OSS_ljh/issues?q=is%3Aissue)에서 확인할 수 있습니다. 스프린트에 넣지 않은 이슈는 마일스톤 없이 Backlog에 둡니다.

처음에는 DORA 지표 도구를 학기 프로젝트로 제안했다가 TimeFit으로 주제를 바꿨습니다. 그래서 기존 주제의 확장 이슈(#9~#15)는 "not planned"로 닫고 보드에서 뺐으며, 이미 완료한 개발 인프라 작업(#1~#8)은 Sprint 1로 남겼습니다.

## (선택과제) Cycle Time · Velocity · Burndown

[ANALYSIS.md](ANALYSIS.md) — [`scripts/sprint_metrics.py`](../scripts/sprint_metrics.py)가 이슈와 마일스톤 데이터로 계산해 자동 생성합니다. DORA 수집 워크플로우가 실행될 때마다 함께 갱신됩니다.
