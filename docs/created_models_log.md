# 생성된 모델 기록 (2026-08-19 야간)

> 콘솔: https://d1i2pk1fl8ogd9.cloudfront.net · 계정: Antony
> 공통 설정: re:Invent 2018(`reinvent_base`) · **반시계 전용** · Time trial · Camera(모노, LiDAR 없음) ·
> PPO · Batch 64 · **Epochs 3** · LR 0.0003 · Entropy 0.01 · **Discount 0.995** · Huber · Episodes 20 · 평가 5회

## 생성 완료 (8개 전부) — 전부 `Queued`

| 모델명 | 레인 | 액션 수 | 최고 속도 | 학습 | 모델 URL 경로 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `A-p1-v1` | A · 중앙선 보험 | 10 | 2.0 | 45분 | `/models/Agavv9sNqdk5nNP` |
| `B-p2-v2` | B · K1999 레이싱라인 | 10 | **2.2** | 45분 | `/models/1YzS1iuN0gR1ETE` |
| `B-p2-v1` | B · K1999 레이싱라인 | 10 | **2.4** | 60분 | `/models/F7d4tjPGfImArPn` |
| `B-p2-v3` | B · K1999 레이싱라인 | 10 | **2.6** | 45분 | `/models/0U6o4BaX8UQSND0` |
| `C-p2-v2` | C · 곡률 lookahead | 12 | **2.4** | 45분 | `/models/crMUKBr2CMAEYe3` |
| `C-p2-v1` | C · 곡률 lookahead | 12 | **2.6** | 60분 | `/models/UniYJKpn0IZ37Jn` |
| `C-p2-v3` | C · 곡률 lookahead | 12 | **2.8** | 45분 | `/models/ofuJiDCJxA2GCoM` |
| `D-p2-v1` | D · 워블 억제 | 8 | 2.0 | 60분 | `/models/7J5PBYcvK57Hx5O` |

→ **B 스윕(2.2/2.4/2.6)과 C 스윕(2.4/2.6/2.8) 모두 완성.** 각 스윕 3개는 액션 스페이스의
0° 행 속도 + Maximum speed(+ C는 보상함수 `target`)만 다르고 나머지는 완전히 동일 → 차이가 곧 속도 효과.

### C 레인 보상함수의 목표 속도 단계 (CAP별)

| 모델 | 직선(turn&lt;5°) | 완만(turn&lt;12°) | 중간(turn&lt;25°) | 급코너 |
| :--- | :--- | :--- | :--- | :--- |
| `C-p2-v2` | 2.4 | 2.1 | 1.8 | 1.4 |
| `C-p2-v1` | 2.6 | 2.2 | 1.8 | 1.4 |
| `C-p2-v3` | 2.8 | 2.3 | 1.8 | 1.4 |

## 액션 스페이스 상세

### A-p1-v1 / 10개 (max 2.0)
`-25/1.4, -15/1.6, -10/1.8, -5/2.0, 0/2.0, 5/2.0, 10/1.8, 15/1.6, 25/1.4, 0/1.6`

### B-p2-v1 / 10개 (CAP 2.4) · B-p2-v2 / 10개 (CAP 2.2)
`-24/1.3, -16/1.6, -10/1.9, -5/2.1, 0/CAP, 5/2.1, 10/1.9, 16/1.6, 24/1.3, 0/1.7`

### C-p2-v1 / 12개 (CAP 2.6)
`-28/1.3, -20/1.5, -14/1.8, -8/2.1, -4/2.4, 0/CAP, 4/2.4, 8/2.1, 14/1.8, 20/1.5, 28/1.3, 0/1.9`

### D-p2-v1 / 8개 (max 2.0, 조향 ±20° 제한)
`-20/1.2, -12/1.5, -6/1.8, 0/2.0, 6/1.8, 12/1.5, 20/1.2, 0/1.4`

## 알려진 문제

1. **큐가 진행되지 않음** — 생성 직후 5개 모두 `Queued`. 오후 3시 27분·4시 48분·4시 51분에 만들어진
   예전 테스트 모델(`TEST1`, `stable-antigravity`, `fight-antigravity`)도 여전히 `Queued`.
   → **동시 학습이 1개씩만 처리되거나 큐가 막힌 상태로 의심.** 운영진 확인 필요.
2. **콘솔 응답 불가** — 19:00경부터 페이지 로딩이 45초 이상 걸리며 응답하지 않음(공용 서비스 과부하 추정).

## 콘솔 조작 시 주의사항 (재작업용)

- **액션 스페이스 입력**: 값을 넣은 뒤 **반드시 Tab을 눌러야** React 상태에 반영된다.
  Tab 없이 연속 입력하면 이전 값이 전부 되돌아간다.
- **Discrete 선택 후 `Advanced configuration` 토글을 켜야** 행별 값을 직접 넣을 수 있다.
- **Maximum speed를 먼저** 설정해야 행별 속도가 그 값까지 입력된다.
- **보상 함수는 PEP8 검사를 통과해야 한다** — 함수 정의 앞에 **빈 줄 2개** 필수
  (`expected 2 blank lines, found 1` 오류 발생).
- 트랙 검색창은 `2018`로 검색해야 찾아진다(`re:Invent 2018`, `Invent`는 0건).
- re:Invent 2018은 **반시계 방향만 지원**(Clockwise 비활성) → 팀 전체 자동 동일.
- `Actions → Clone`은 학습이 끝난 뒤에만 활성화된다.
- `Actions → Download physical car model`로 실차용 모델 파일을 받는다.

## 활용한 공개 자료

- K1999 최적 레이싱 라인 (좌표 71점, B 레인 보상함수에 삽입 완료):
  `github.com/cdthompson/deepracer-k1999-race-lines` → `racelines/reinvent_base-400-4-2019-10-11-161903.py`
- 트랙 waypoint 원본 (119점 × 6열):
  `raw.githubusercontent.com/aws-solutions-library-samples/guidance-for-training-an-aws-deepracer-model-using-amazon-sagemaker/master/log-analysis/tracks/reinvent_base.npy`
- 참고: `reinvent_base` = re:Invent 2018, `reInvent2019_wide` = A to Z Speedway (콘솔 라디오 값으로 확인)
