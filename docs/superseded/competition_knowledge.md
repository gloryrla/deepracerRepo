# AWS DeepRacer & Physical AI 경진대회 지식 베이스

> **목적**: 2박 3일 Physical AI (AWS DeepRacer) 경진대회 전략, 대회 규칙, 트랙 정보, 보상 함수 모델링, 하이퍼파라미터 및 Sim-to-Real 노하우 축적 문서

---

## 1. 대회 개요 및 환경 (Competition Overview)
* **대회명**: 2박 3일 Physical AI 경진대회
* **주요 타겟**: AWS DeepRacer / 강화학습 기반 autonomous driving
* **실행 환경**: (TBD - AWS Console / DeepRacer-for-Cloud / Local Docker 등)
* **트랙 정보**: (TBD - 트랙 명칭, 트랙 길이, 코너 특성 등)
* **제약 조건**: (TBD - 평가 기준: 3분 내 최단 랩타임 / Off-track 감점 / 연속 주행 완주율 등)

---

## 2. 강화학습(RL) 설계 지침 (MDP Framework)

### 2.1 Action Space
* **Steering Angles**: (TBD - e.g., [-30°, -15°, 0°, 15°, 30°])
* **Speed Range**: (TBD - e.g., [1.0 m/s ~ 4.0 m/s])

### 2.2 State & Input Variables
* `all_wheels_on_track`, `x`, `y`, `distance_from_center`, `heading`, `progress`, `steps`, `speed`, `steering_angle`, `track_width`, `waypoints`, `closest_waypoints`, `is_left_of_center` 등

### 2.3 Racing Line & Waypoint Math
* **Racing Line 전략**: 단순 Centerline 주행이 아닌 Apex를 관통하는 최적 선회 궤적 산출
* **Radius of Curvature Formula**:
  $$R = \frac{1}{\kappa} = \left| \frac{dx}{dt} \frac{d^2y}{dt^2} - \frac{dy}{dt} \frac{d^2x}{dt^2} \right|^{-1}$$

---

## 3. 타임라인별 전략 및 체크포인트

* **[DAY 1]**: 베이스라인 보상 함수 수립, Waypoint 궤적 계산, 완주율 100% 확보
* **[DAY 2]**: Dynamic Speed Profile 적용, CloudWatch 로그 분석 기반 오버피팅 예방, 랩타임 단축
* **[DAY 3]**: Sim-to-Real (실물 차량 적용) 최적화, 파이널 랩타임 도전

---

## 4. 대회 세부 정보 & 획득 데이터 (사용자 제공 정보 기록 구역)

*(유저가 제공하는 정보를 여기에 지속적으로 학습 및 정리 업데이트 예정)*

