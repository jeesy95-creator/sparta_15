1. 개요
본 분석을 통해 사용자 활동 데이터를 기반으로 일별 활동 상태(DayType)를 정의하고,
사용자 기준 정규화(z-score) 및 상태 전이 분석을 통해 활동 패턴 변화를 탐색하였다.

2. 비즈니스 목적
- 일상 행동 변화 파악 + 맞춤형 개입이 핵심 가치
- 단순히 “얼마나 움직였는가”가 아니라 “사용자 기준에서 활동 상태는 어떻게 달라지고, 어떻게 전이되는가?”

3. 데이터 전처리 및 파생변수 정의
- TotalActiveMinutes(총 활동 시간) : VeryActiveMinutes + FairlyActiveMinutes + LightlyActiveMinutes
- Sedentary Ratio(하루동안 앉아있는 시간의 비율) : SedentaryMinutes/1440

- DayType 기준 : 
  1) Active Day : TotalSteps > 7000 and TotalActiveMinutes > 60
  2) Over-Sedentary Day : Sedentary Ratio > 0.75 and TotalSteps > 0
  3) Low Engagement Day : TotalSteps < 3000 and TotalSteps > 0 and Sedentary Ratio > 0.5
  4) Rest Day : TotalSteps == 0
  5) Normal Day : 이 이외의 구간

4. 데이터 분석 결과
```python
import pandas as pd

act["ActivityDate"] = pd.to_datetime(act["ActivityDate"]).dt.date   # 날짜만 남김(시간 제거)
daily_counts = (
    act.groupby(["ActivityDate", "DayType"])
       .size()
       .unstack(fill_value=0)
       .sort_index()
)
daily_counts
```
각 날짜별 DayType의 수를 합계해서 정리한 결과를 EDA로 표현한 결과는 다음과 같다.
