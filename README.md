# 경북대 × 전남대 Physical AI 경진대회 (AWS DeepRacer)

> 2026.08.19(수) ~ 08.21(금) · 라한 셀렉트 카펠라홀 · 10팀 × 4인
> 본선: 8/21(금) 10:00–12:00 · 대상 200만원

---

## 지금 가장 먼저 볼 것

**[plans/atoz_design.md](plans/atoz_design.md)** — **2026-08-19 밤 설계 개정.**
트랙이 **A to Z Speedway**로 확정되고 채점이 **2개 모델 평균 시간**으로 바뀌었다.
아래 내용 중 승리 공식과 레인 캡은 이 문서가 우선한다.

**[plans/day2_plan.md](plans/day2_plan.md)** — 당일 진행 순서 (판정 절차는 그대로 유효).

---

## 핵심 전략 한 장 요약

### 승리 공식 (2026-08-19 개정)

```
성적 = (모델1 시간 + 모델2 시간) / 2       ※ Best Lap 아님. 평균이다
모델 시간 = Lap Time + (Off-Track 횟수 × 1.0s)   ※ 리셋 중 시계 정지
```

**평균 채점이므로 분산이 적군이다.** 버릴 수 있는 주행이 없으니 두 모델 모두
기대값 최적점(캡 2.4~2.6)에 놓아야 한다. 자세한 계산은
[plans/atoz_design.md](plans/atoz_design.md) 참조.

탈선 실비용은 페널티 1초 + 재가속 약 1초 = **약 2초**다. 아래 표는 Best Lap 규칙 시절의
것으로, **극공격이 유리하다는 결론은 이제 성립하지 않는다** — 기록으로만 남긴다.

| 설정 | 평균 속도 | 클린 랩 | 탈선 1회 | 탈선 2회 |
| :--- | :--- | :--- | :--- | :--- |
| 보수 | 1.4 m/s | 12.6s | 14.6s | 16.6s |
| 중립 | 1.7 m/s | 10.4s | 12.4s | 14.4s |
| **공격** | 2.0 m/s | **8.8s** | 10.8s | 12.8s |
| **극공격** | 2.3 m/s | **7.7s** | 9.7s | 11.7s |

**극공격으로 두 번 탈선해도(11.7s) 보수적으로 완벽하게 완주한 것(12.6s)보다 빠르다.**
→ 목표는 "0 탈선"이 아니라 **기대 탈선 1회 이하에서 가장 빠른 설정**.

### 운영 원칙

1. **두 모델 모두 기대값 최적으로** — 평균 채점이라 보험 모델이라는 개념이 없다.
   느린 모델은 성적을 깎는 부채다. 최종 선발은 **기대 시간이 낮은 2개**.
2. **실차 기록만 신뢰** — 시뮬 완주율 100%는 실차 완주를 보증하지 않는다.
3. **45~60분 단위로 끊어 학습** — 3시간 넘기면 시뮬레이터 픽셀에 과적합되어 실차에서 무너진다.
4. **한 번에 하나만 바꾼다** — 보상 함수와 액션 스페이스를 동시에 바꾸면 무엇이 효과였는지 알 수 없다.

---

## 4레인 실험 설계

등록·업로드는 각자 하면 되는 일이라 역할 분담(직책)은 두지 않는다.
대신 **4명이 서로 다른 가설**을 맡고 실차 테스트로 승자를 고른다.

| 레인 | 검증할 가설 | 보상 함수 |
| :--- | :--- | :--- |
| **A** 보험 | 확실히 완주하는 기록을 먼저 확보한다 | [lane_a_centerline.py](reward_functions/lane_a_centerline.py) |
| **B** 본진 | 최적 궤적이 랩타임을 만든다 | [lane_b_racing_line.py](reward_functions/lane_b_racing_line.py) |
| **C** 공격 | 궤적보다 감가속 타이밍이 랩타임을 만든다 | [lane_c_speed_profile.py](reward_functions/lane_c_speed_profile.py) |
| **D** 헤지 | 시뮬 1등이 실차 1등이 아니다 | [lane_d_wobble.py](reward_functions/lane_d_wobble.py) |

> **가장 큰 낭비는 4명이 같은 보상 함수의 숫자만 조금씩 바꿔 돌리는 것이다.**
> 4배 자원을 쓰고 1인분의 정보만 남는다.

---

## 8/19 야간에 걸어둔 모델 8개

전부 `Queued` 상태. 상세 설정은 **[docs/created_models_log.md](docs/created_models_log.md)** 참조.

| 모델 | 레인 | 액션 | 최고 속도 | 학습 |
| :--- | :--- | :--- | :--- | :--- |
| `A-p1-v1` | A · 중앙선 | 10 | 2.0 | 45분 |
| `B-p2-v2` | B · 레이싱라인 | 10 | 2.2 | 45분 |
| `B-p2-v1` | B · 레이싱라인 | 10 | 2.4 | 60분 |
| `B-p2-v3` | B · 레이싱라인 | 10 | 2.6 | 45분 |
| `C-p2-v2` | C · 속도 프로파일 | 12 | 2.4 | 45분 |
| `C-p2-v1` | C · 속도 프로파일 | 12 | 2.6 | 60분 |
| `C-p2-v3` | C · 속도 프로파일 | 12 | 2.8 | 45분 |
| `D-p2-v1` | D · 워블 억제 | 8 | 2.0 | 60분 |

B·C는 각각 **최고 속도만 다른 3개 스윕**이다 → 완주율이 무너지는 속도가 곧 시뮬 상한.

### 알려진 문제

**큐가 진행되지 않는다.** 12개 모델 전부 `Queued`이고 `Training`·`Ready`가 하나도 없다.
오후 4시 48분에 만든 모델도 4시간 가까이 그대로였다.
→ 동시 학습이 1개씩만 처리되거나 큐가 막힌 상태로 의심. **운영진 확인 필요.**

---

## 확인된 사실

| 항목 | 값 |
| :--- | :--- |
| 트랙 | **A to Z Speedway** (내부명 `reInvent2019_wide`, 16.64m × 107cm) — 실측 확정 (흰선 사이 1m 초과) |
| 채점 | **2개 모델의 평균 시간** (Best Lap 아님) |
| 차량 | 모노 카메라 1대, LiDAR 없음 |
| 탈선 페널티 | 리셋 중 **시계 정지** + 1초 → 실비용 약 2초 |
| 1·2차 사이 | **모델 교체 + 스로틀 배율 조정 모두 허용** |
| Import model | 허용. 단 **공개된 학습 가중치는 없음** → 팀 4계정 간 체크포인트 공유 용도 |
| 콘솔 | https://d1i2pk1fl8ogd9.cloudfront.net |

---

## 공통 콘솔 설정 (4명 전원 동일하게)

Import로 모델을 주고받으려면 아래가 팀 전체에서 같아야 한다.
**레인별로 다른 것은 액션 스페이스와 보상 함수뿐이다.**

| 항목 | Phase 1 | Phase 2·3 (Clone) |
| :--- | :--- | :--- |
| 센서 | Camera (모노), LiDAR 해제 | 동일 |
| 알고리즘 | PPO | 동일 |
| Batch size | 64 | 64 |
| **Number of epochs** | **3** (기본값 10에서 반드시 변경) | 3 |
| Learning rate | 0.0003 | **0.0001** |
| Entropy | 0.01 | **0.005** |
| **Discount factor** | **0.995** (기본값 0.99에서 변경) | 0.99–0.995 |
| Loss type | Huber (기본값) | 동일 |
| Experience episodes | 20 | 20 |
| Evaluation trials | 5 | 5 |
| Maximum time | **45~60분** (절대 초과 금지) | 동일 |

---

## 콘솔 조작 시 함정 (실제로 겪은 것)

1. **액션 스페이스는 값 입력 후 반드시 Tab을 눌러야 반영된다.**
   Tab 없이 연속 입력하면 React가 이전 값을 전부 되돌린다.
2. **Discrete 선택 후 `Advanced configuration` 토글을 켜야** 행별 값을 직접 넣을 수 있다.
   켜지 않으면 자동 생성 격자가 **큰 조향각에 최고 속도를 붙인 채로** 학습된다 (실차 스핀의 직행 코스).
3. **Maximum speed를 먼저** 설정해야 행별 속도가 그 값까지 입력된다. 기본값 1이므로 반드시 변경.
4. **보상 함수는 PEP8 검사를 통과해야 한다** — 함수 정의 앞에 **빈 줄 2개** 필수
   (`expected 2 blank lines, found 1` 오류).
5. **트랙 검색은 `2018`로** 해야 찾아진다 (`Invent`, `re:Invent 2018`은 0건).
6. **A to Z Speedway가 잘못 선택되기 쉽다** — 그 카드 설명에 "extra wide version of re:Invent 2018"이
   들어있어 검색이 오인한다. 길이 17.6m·폭 76cm 표시를 꼭 확인할 것.
7. `Actions → Clone`은 **학습이 끝난 뒤에만** 활성화된다.
8. 실차용 파일은 `Actions → Download physical car model`.

---

## 활용한 공개 자료

| 자료 | 위치 | 용도 |
| :--- | :--- | :--- |
| **K1999 최적 레이싱 라인** (71점) | [cdthompson/deepracer-k1999-race-lines](https://github.com/cdthompson/deepracer-k1999-race-lines) → `racelines/reinvent_base-400-4-2019-10-11-161903.py` | 레인 B 보상함수에 삽입 완료 |
| 트랙 waypoint 원본 (119점 × 6열) | [reinvent_base.npy](https://raw.githubusercontent.com/aws-solutions-library-samples/guidance-for-training-an-aws-deepracer-model-using-amazon-sagemaker/master/log-analysis/tracks/reinvent_base.npy) | 레이싱 라인 재계산, 로그 분석 |
| 레이싱 라인 계산 노트북 | cdthompson → `Race-Line-Calculation.ipynb` | 더 공격적인 라인 재산출 |
| 구간별 최적 속도 · 액션 스페이스 계산 | [dgnzlz/Capstone_AWS_DeepRacer](https://github.com/dgnzlz/Capstone_AWS_DeepRacer) → `Compute_Speed_And_Actions/` | 레인 C 목표 속도를 계산값으로 교체 |
| 실차 우승 보상함수 레퍼런스 | [poponuts/aws-deepracer-model](https://github.com/poponuts/aws-deepracer-model) | 비교 기준. 최고 2.0 m/s에서 11초대 |

> **주의: 학습된 모델 가중치를 공개하는 저장소는 사실상 없다.** 우승 모델 저장소들도
> `reward_function.py`만 공개한다. Import는 **팀 계정 간 체크포인트 공유** 용도로 쓴다.

---

## 저장소 구조

```
├── README.md                        ← 이 파일
├── plans/
│   └── day2_plan.md                 ← 내일 실행 계획 (가장 먼저 볼 것)
├── reward_functions/                ← 콘솔에 복사해 붙일 수 있는 완성 코드
│   ├── lane_a_centerline.py
│   ├── lane_b_racing_line.py        ← K1999 좌표 71개 포함
│   ├── lane_c_speed_profile.py
│   └── lane_d_wobble.py
├── docs/
│   ├── created_models_log.md        ← 8개 모델의 URL·액션 스페이스 전체 기록
│   ├── competition_overview.md
│   ├── competition_knowledge.md
│   ├── champion_strategies.md
│   ├── reward_functions.md
│   ├── action_space_and_hyperparams.md
│   └── workflow_guide.md
└── pdf/                             ← 팀 공유용 인쇄물
    ├── race_operations_brief.pdf    ← 전체 전략 브리프
    ├── lane_playbook.pdf            ← 레인별 설정·코드 상세
    └── morning_checklist.pdf        ← 아침 판정 시트
```
