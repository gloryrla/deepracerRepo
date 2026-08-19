# AWS DeepRacer 코딩 & 실물 차량 배포 워크플로우 (End-to-End 가이드)

---

## 1. 전체 파이프라인 한눈에 보기

```mermaid
flowchart TD
    subgraph 1. 코딩 & 설정 (My PC / AWS Console)
        A["Python 보상 함수 코딩\n(reward_function)"] --> C["AWS DeepRacer 콘솔 입력"]
        B["Action Space & 하이퍼파라미터 설정"] --> C
    end

    subgraph 2. 클라우드 강화학습 (AWS Cloud)
        C --> D["AWS SageMaker (RL 알고리즘)"]
        C --> E["AWS RoboMaker (3D 물리 시뮬레이션)"]
        D <--> E
        E --> F["학습 완료 모델 생성\n(model.tar.gz)"]
    end

    subgraph 3. 모델 다운로드 & 실차 업로드
        F --> G["노트북으로 model.tar.gz 다운로드"]
        G --> H{"차량 업로드 방식 선택"}
        H -->|방법 A| I["USB 드라이브 복사 ➔ 차량 연결"]
        H -->|방법 B (권장)| J["차량 Wi-Fi 접속 ➔ 웹 콘솔 업로드"]
    end

    subgraph 4. 물리 트랙 실전 주행
        I --> K["조향 0점(Calibration) 확인"]
        J --> K
        K --> L["실물 트랙 자율주행 실행 🚀"]
    end
```

---

## 2. 우리가 실제로 '코딩'하는 것

우리가 직접 파이썬 코드로 작성하는 것은 **보상 함수(Reward Function)** 하나입니다!

* **입력값 (`params` 딕셔너리)**: 시뮬레이터/차량이 실시간으로 측정하는 10여 가지 센서 데이터
  * `distance_from_center` (중심선과의 거리)
  * `steering_angle` (현재 조향각)
  * `speed` (현재 속도)
  * `heading` (차량이 바라보는 각도)
  * `all_wheels_on_track` (바퀴가 트랙 위에 있는지 여부)
  * `waypoints` (트랙 좌표점들) 등
* **출력값 (`reward` 실수형 숫자)**: 
  * 잘한 행동에는 높은 점수(예: 1.5), 나쁜 행동(트랙 이탈, 급핸들)에는 낮은 점수(예: 0.1)를 반환하는 파이썬 함수입니다.

---

## 3. 학습부터 로봇(실차) 배포까지 5단계 절차

### 1단계: AWS 콘솔에서 모델 생성 & 코드 입력
1. AWS 콘솔 로그인 ➔ **AWS DeepRacer** 서비스로 이동.
2. **Create Model** 클릭.
3. 우리가 정의한 **Action Space** 및 **하이퍼파라미터** 입력.
4. **Reward function** 입력창에 우리가 작성한 파이썬 코드를 복사/붙여넣기.
5. 학습 시간(예: 45분~60분) 설정 후 **Start training** 클릭.

### 2단계: 클라우드 시뮬레이션 학습
* AWS의 가상 시뮬레이터(RoboMaker)에서 차량이 혼자 수만 번 트랙을 달리며 보상을 최대화하는 딥러닝 정책(Policy)을 스스로 학습합니다.

### 3단계: 완성된 모델 다운로드
* 학습 완료 후 모델 상세 페이지에서 **`Download Model`** 버튼을 누르면 `model.tar.gz` (신경망 가중치 파일)가 내 노트북에 저장됩니다.

### 4단계: 실물 차량(DeepRacer RC카)에 업로드 (2가지 방법)
* **방법 ① (웹 콘솔 업로드 - 가장 많이 씀 ⭐)**:
  1. 노트북으로 DeepRacer 차량의 Wi-Fi에 접속합니다.
  2. 웹 브라우저에서 `https://deepracer.aws` 또는 차량 IP(`192.168.x.x`)로 접속합니다 (기기 관리자 화면).
  3. **Models** 탭 클릭 ➔ **Upload model** 클릭 ➔ 다운로드받은 `model.tar.gz` 선택하여 전송!
* **방법 ② (USB 복사)**:
  1. USB 드라이브에 `models/` 폴더를 생성하고 그 안에 `model.tar.gz`를 넣습니다.
  2. DeepRacer 차량의 USB 포트에 꽂으면 자동으로 모델이 로드됩니다.

### 5단계: 조향 캘리브레이션 & 트랙 주행
1. 차량 웹 콘솔의 **Calibration** 메뉴에서 차가 일직선으로 가도록 서보모터 영점(0°)을 맞춥니다.
2. 업로드한 모델을 선택하고 속도 스로틀(Throttle)을 설정한 뒤 **Start Driving**을 누르면 차량 앞 카메라가 트랙을 보며 스스로 판단하여 주행합니다!
