# 단계별 추천 보상 함수 (Reward Functions)

상위권 수상자들이 선호하는 **곱셈(Multiplication) 구조**와 페널티 기반의 보상 함수 템플릿입니다.

---

## 1. [Phase 1] 완주율 100% 확보용 베이스라인 보상 함수
* **목표**: 차선을 벗어나지 않고 트랙을 안정적으로 1바퀴 도는 기본 제어 정책 확립.

```python
def reward_function(params):
    '''
    [Phase 1] 안정적인 완주율 확보를 위한 베이스라인 보상 함수
    '''
    all_wheels_on_track = params['all_wheels_on_track']
    distance_from_center = params['distance_from_center']
    track_width = params['track_width']
    speed = params['speed']
    steering_angle = params['steering_angle']

    # 1. 트랙 이탈 방지 (Fail-safe)
    if not all_wheels_on_track:
        return 1e-3

    # 기본 보상 시작
    reward = 1.0

    # 2. 중심선 거리 기반 보상 (곱셈 방식)
    marker_1 = 0.10 * track_width
    marker_2 = 0.25 * track_width
    marker_3 = 0.45 * track_width

    if distance_from_center <= marker_1:
        reward *= 1.2
    elif distance_from_center <= marker_2:
        reward *= 0.8
    elif distance_from_center <= marker_3:
        reward *= 0.4
    else:
        reward *= 0.1  # 트랙 경계선 접근 시 감점

    # 3. 조향각 과도 꺾임 방지 (직선 안정성)
    if abs(steering_angle) > 15:
        reward *= 0.8

    # 4. 저속 주행 방지 (최소 권장 속도 유지)
    SPEED_BENCHMARK = 1.2
    if speed >= SPEED_BENCHMARK:
        reward *= (speed / SPEED_BENCHMARK)

    return float(reward)
```

---

## 2. [Phase 2] Heading 각도 & 방향 정렬 보상 함수
* **목표**: 트랙의 Waypoint 방향과 차량의 진행 방향(Heading)을 일치시켜 부드러운 코너링 구현.

```python
import math

def reward_function(params):
    '''
    [Phase 2] 진행 방향 정렬 및 코너링 최적화 보상 함수
    '''
    all_wheels_on_track = params['all_wheels_on_track']
    distance_from_center = params['distance_from_center']
    track_width = params['track_width']
    waypoints = params['waypoints']
    closest_waypoints = params['closest_waypoints']
    heading = params['heading']
    speed = params['speed']
    steering_angle = params['steering_angle']

    if not all_wheels_on_track:
        return 1e-3

    reward = 1.0

    # 1. 중심선 거리 유지
    marker_1 = 0.15 * track_width
    marker_2 = 0.35 * track_width

    if distance_from_center <= marker_1:
        reward *= 1.2
    elif distance_from_center <= marker_2:
        reward *= 0.7
    else:
        reward *= 0.2

    # 2. 진행 방향(Heading)과 트랙 접선 벡터 각도 차이 보상
    next_point = waypoints[closest_waypoints[1]]
    prev_point = waypoints[closest_waypoints[0]]

    track_direction = math.atan2(next_point[1] - prev_point[1], next_point[0] - prev_point[0])
    track_direction = math.degrees(track_direction)

    direction_diff = abs(track_direction - heading)
    if direction_diff > 180:
        direction_diff = 360 - direction_diff

    # 방향 일치도에 따른 감점/가산
    DIRECTION_THRESHOLD = 10.0
    if direction_diff <= DIRECTION_THRESHOLD:
        reward *= 1.2
    elif direction_diff <= 20.0:
        reward *= 0.8
    else:
        reward *= 0.4

    # 3. 흔들림(Wobble) 방지 페널티
    if abs(steering_angle) > 20 and speed > 1.8:
        reward *= 0.7

    return float(reward)
```

---

## 3. [Phase 3] Physical 실차 전용 고속 & 안티 워블링(Anti-Wobbling) 보상 함수
* **목표**: 실물 차량에서 스핀 방지 + 최고 속도 제한(Cap) + 최단 랩타임 달성.

```python
import math

def reward_function(params):
    '''
    [Phase 3] Physical 리그 전용 - 스피드 프로파일 및 흔들림 억제 보상 함수
    '''
    all_wheels_on_track = params['all_wheels_on_track']
    distance_from_center = params['distance_from_center']
    track_width = params['track_width']
    speed = params['speed']
    steering_angle = params['steering_angle']
    progress = params['progress']
    steps = params['steps']

    if not all_wheels_on_track:
        return 1e-3

    reward = 1.0

    # 1. 중심선 거리 보상
    if distance_from_center <= 0.15 * track_width:
        reward *= 1.3
    elif distance_from_center <= 0.30 * track_width:
        reward *= 0.85
    else:
        reward *= 0.3

    # 2. 속도 최적화 (2.0 ~ 2.4 m/s 권장 캡)
    SPEED_MAX_CAP = 2.4
    if speed >= 2.0:
        reward *= (speed / 2.0)
    elif speed < 1.4:
        reward *= 0.6  # 과도한 저속 주행 감점

    # 3. 실차 전용 고속 과조향 페널티 (스핀 및 이탈 방지)
    if speed > 1.8 and abs(steering_angle) > 15:
        reward *= 0.7
    if abs(steering_angle) > 25:
        reward *= 0.6

    # 4. 스텝 대비 진척도 보상 (빠른 완주 유도)
    if steps > 0:
        reward += (progress / steps) * 10.0

    return float(reward)
```
