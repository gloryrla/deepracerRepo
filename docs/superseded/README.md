# 폐기된 문서 (참고용 보관)

아래 문서들은 **트랙·채점 방식이 확정되기 전**에 작성되어 현행 설계와 모순된다.
**여기 있는 코드나 수치를 절대 그대로 쓰지 마라.** 현행 문서는 저장소 루트의 `README.md`,
`plans/atoz_design.md`, `reward_functions/` 다.

| 파일 | 폐기 사유 |
| :--- | :--- |
| `reward_functions.md` | 여기 실린 보상 함수 3종에 결함이 있다. Phase 1에 속도 보상이 섞여 있고(수렴 방해), 중앙선 보상과 레이싱 라인 추종을 동시에 넣어 목표가 충돌하며, 곱셈 기반 보상에 `reward += (progress/steps)*10` 같은 큰 덧셈 항이 얹혀 조향·속도 페널티를 무력화한다. 수정된 코드는 `reward_functions/lane_*.py` |
| `action_space_and_hyperparams.md` | 조향 ±25~30°를 권하지만, 계산된 최적 경로가 요구하는 최대 조향은 11.8°다. 또 본문은 "10~12개 권장"인데 표에는 8개만 실려 있어 자체 모순이 있다 |
| `competition_overview.md` | 채점을 **Best Lap**으로 적었으나 실제로는 **2개 모델의 평균 시간**이다. 전략의 전제가 정반대로 바뀐다 |
| `competition_knowledge.md` | 트랙·규정이 대부분 TBD 상태인 초기 골격 |
| `created_models_log.md` | 폐기된 구계정에서 만든 모델 8개 기록. re:Invent 2018 기준이라 트랙도 틀렸다 |
