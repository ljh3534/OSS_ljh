# 3주차 — GitHub Projects 계획·추적 체계

학기 프로젝트 [TimeFit](../week01/PROPOSAL.md)(시간표 자동 조합 도우미)의 백로그를 GitHub Issues·Labels·Milestones·Projects로 구성했습니다.

## 1. 칸반 보드

**[TimeFit 프로젝트 보드](https://github.com/users/ljh3534/projects/1/views/3)**

| 컬럼 | 의미 | WIP 제한 |
|---|---|---|
| Backlog | 우선순위가 정렬된 전체 작업 목록 (아직 스프린트에 넣지 않음) | 없음 |
| To Do | 현재 스프린트에서 처리하기로 선정된 작업 | 없음 |
| In Progress | 지금 작업 중인 상태 | 최대 3개 |
| Review | Pull Request 생성 후 리뷰 대기 | 최대 2개 |
| Done | 완료되어 종료된 작업 | 없음 |

### 커스텀 필드

| 필드 | 형식 | 값 |
|---|---|---|
| Priority | Single select | Critical / High / Medium / Low |
| Story Points | Number | 1, 2, 3, 5, 8 (피보나치) |
| Sprint | Iteration (2주) | Sprint 1 (10/13~10/26), Sprint 2 (10/27~11/09) |

## 2. 이슈 템플릿

[`.github/ISSUE_TEMPLATE/`](../.github/ISSUE_TEMPLATE)에 두 가지 템플릿을 두었습니다. 빈 이슈는 만들 수 없게 설정했습니다(`config.yml`).

- [Bug Report](../.github/ISSUE_TEMPLATE/bug_report.md) — 버그 설명, 재현 단계, 예상 동작, 실제 동작
- [Feature Request](../.github/ISSUE_TEMPLATE/feature_request.md) — User Story(As a / I want / So that), 해결하려는 문제, 제안하는 솔루션, 완료 조건

## 3. 라벨 체계

| 분류 | 라벨 | 용도 |
|---|---|---|
| Type | `bug` `enhancement` `documentation` `maintenance` `question` | 작업의 성격 |
| Priority | `priority: critical` `priority: high` `priority: medium` `priority: low` | 처리 순서 |
| Status | `status: new` `status: investigating` `status: in-progress` `status: ready` `status: blocked` | 진행 단계 |
| Size | `size: XS`(1) `size: S`(2) `size: M`(3) `size: L`(5) `size: XL`(8) | 예상 작업량. 괄호 안 숫자를 Story Points로 사용 |
| 기타 | `incident` `report` `project-proposal` | 운영 장애(MTTR 계산), 자동 주간 보고서, 프로젝트 제안서 |

## 4. 마일스톤

| 마일스톤 | 기간 | 목표 |
|---|---|---|
| [Sprint 1 — 개발 인프라 (배포·DORA·백로그)](https://github.com/ljh3534/OSS_ljh/milestone/1) | 10/13 ~ 10/26 | 배포 파이프라인, DORA 지표 자동 수집, 이슈 템플릿·라벨 |
| [Sprint 2 — TimeFit MVP](https://github.com/ljh3534/OSS_ljh/milestone/2) | 10/27 ~ 11/09 | 과목 입력, 충돌 없는 조합 생성, 시간표 표시 |

## 5. 스프린트

### Sprint 1 — Review

- **목표**: TimeFit 개발을 시작하기 전에, 배포·지표 수집·작업 관리 환경을 갖춘다.
- **결과**: 계획한 9개 이슈(25 points)를 모두 완료했다.
  - GitHub Pages 자동 배포, DORA 지표 수집 워크플로우, 대시보드, 주간 보고서
  - 이슈 템플릿, 라벨 체계, 프로젝트 보드
- **배운 점**: 처음에는 DORA 지표 도구 자체를 학기 프로젝트로 잡았다가, 실제 사용자가 있는 TimeFit으로 주제를 바꿨다. 기존 주제의 확장 이슈(#9~#15)는 "not planned"로 닫고 보드에서 뺐다.

### Sprint 2 — Planning

- **Sprint Goal**: 과목을 입력하면 겹치지 않는 시간표 조합을 화면에서 볼 수 있다.
- **Sprint Backlog** (18 points)

| 이슈 | Points | Priority |
|---|---|---|
| #18 웹앱 기본 폴더 구조와 Pages 배포 경로 설정 | 2 | High |
| #19 과목·분반 데이터 모델 정의 | 2 | High |
| #20 충돌 없는 시간표 조합 생성 엔진 | 5 | High |
| #21 과목·분반 입력 화면 | 3 | High |
| #22 시간표 격자 표시 | 3 | High |
| #23 Jest 단위 테스트 환경과 PR 테스트 워크플로우 | 2 | Medium |
| #24 입력한 과목 목록 브라우저 저장 | 1 | Medium |

## 6. (선택과제) Cycle Time · Velocity · Burndown

[ANALYSIS.md](ANALYSIS.md) — [`scripts/sprint_metrics.py`](../scripts/sprint_metrics.py)가 이슈와 마일스톤 데이터로 계산해 자동 생성합니다. DORA 수집 워크플로우가 실행될 때마다 함께 갱신됩니다.

- **Cycle Time**: 이슈가 열린 시각부터 닫힌 시각까지
- **Velocity**: 스프린트(마일스톤)마다 완료한 Story Points 합
- **Burndown**: 스프린트 2주 동안 날마다 남은 Story Points (이상적인 감소선과 비교)
