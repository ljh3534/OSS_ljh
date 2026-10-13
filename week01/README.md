# 1주차 — 개발 환경 설정 및 프로젝트 제안

## 1. Git/GitHub 개발 환경

| 항목 | 내용 |
|---|---|
| GitHub 계정 | [ljh3534](https://github.com/ljh3534) |
| Git 버전 | `git version 2.50.1 (Apple Git-155)` (macOS) |
| 사용자 설정 | `git config --global user.name` / `user.email` 설정 완료 |
| SSH 키 | RSA 4096bit 키(`~/.ssh/id_rsa`)를 GitHub 계정에 등록 |
| 테스트 저장소 | [ljh3534/OSS_ljh](https://github.com/ljh3534/OSS_ljh) |

### SSH 연결 확인

```console
$ ssh -T git@github.com
Hi ljh3534! You've successfully authenticated, but GitHub does not provide shell access.
```

### 첫 커밋 / 푸시

원격 저장소는 SSH 주소로 연결했습니다.

```console
$ git init -b main
$ git add .
$ git commit -m "docs: 1주차 개발 환경 설정 기록 및 프로젝트 제안서 추가"
$ git remote add origin git@github.com:ljh3534/OSS_ljh.git
$ git push -u origin main
```

첫 커밋은 [커밋 기록](https://github.com/ljh3534/OSS_ljh/commits/main)의 가장 아래에서 확인할 수 있습니다.

## 2. 프로젝트 제안서

[PROPOSAL.md](PROPOSAL.md) — 프로젝트명, 문제정의, 핵심 기능 3개, 기술 스택, 16주 마일스톤 초안.
