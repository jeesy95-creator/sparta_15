# %%
num1 = 3
num2 = 5
def solution(num1, num2):
    return num1 - num2
print(solution(num1, num2))
# %%

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("../data/dailyActivity_merged_fin_sum.csv")
act = df.copy()
# %%

act.head()


# %%
# 날짜 컬럼을 datetime으로 변환
act['ActivityDate'] = pd.to_datetime(act['ActivityDate'])
# %%
# 추가 전처리 - [단위 변환] Mile -> Km 

# 변환할 컬럼 리스트 자동 추출
distance_cols = [col for col in act.columns if 'Distance' in col]

# 1 Mile = 1.60934 Km
# 모든 거리 컬럼에 1.60934를 곱해서 km로 변환
act[distance_cols] = act[distance_cols] * 1.60934

# 소수점 2자리로 깔끔하게 정리
act[distance_cols] = act[distance_cols].round(2)

# 잘 바뀌었나 확인 
print("===[단위 변환 완료] Mile -> Km ===")
act[distance_cols].head()
# %%
act['Id'] = act['Id'].astype(str) # Id 컬럼을 문자열로 변환
#
#  %%
# 미착용일 제거
non_wear = (act['TotalSteps'] == 0) & (act['TotalDistance'] == 0) & (act['SedentaryMinutes'] >= 1380)
print(f"미착용일 수: {non_wear.sum()}개")
act = act[~non_wear].copy()

# 파생 변수 생성
act["ActivityDate"] = pd.to_datetime(act["ActivityDate"])
act['weekday'] = act['ActivityDate'].dt.day_name()
act['is_weekend'] = act['weekday'].isin(['Saturday', 'Sunday'])
act['TotalActiveMinutes'] = (
    act['VeryActiveMinutes'] + 
    act['FairlyActiveMinutes'] + 
    act['LightlyActiveMinutes'])

# %%
print(act['weekday'].dtype)
# %%
# 한글 폰트 설정

import matplotlib.font_manager as fm
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

candidates = ["Malgun Gothic", "맑은 고딕", "NanumGothic", "굴림", "Gulim"]
installed = {f.name for f in fm.fontManager.ttflist}

for font in candidates:
    if font in installed:
        plt.rcParams["font.family"] = font
        break

plt.rcParams["axes.unicode_minus"] = False  # 마이너스(-) 깨짐 방지

print("선택된 폰트:", plt.rcParams["font.family"])
# %%
# 숫자 단위 통일 및 정리 (Rounding)
# 이유: Distance 관련 컬럼들이 소수점 13자리까지 있어서 보기 힘듦. 소수점 2자리로 축약
dist_cols = ['TotalDistance', 'TrackerDistance', 'VeryActiveDistance', 
             'ModeratelyActiveDistance', 'LightActiveDistance', 'SedentaryActiveDistance']
act[dist_cols] = act[dist_cols].round(2)

# 논리적 이상치 처리 (Data Consistency)
# 이유: 하루는 24시간(1440분)인데, 다 더해서 1440분이 넘는 데이터는 '오류'. 1440분 초과 데이터를 제거
act['Total_Minutes_Check'] = (act['VeryActiveMinutes'] + 
                              act['FairlyActiveMinutes'] + 
                              act['LightlyActiveMinutes'] + 
                              act['SedentaryMinutes'])

# 1440분 이하인 정상 데이터만 남기기
act = act[act['Total_Minutes_Check'] <= 1440].copy()
# %%
# 2-2. Calorie 그룹 추가
bins = [1000, 1500, 2000, 2500, float('inf')]
labels = ['1000-1500', '1500-2000', '2000-2500', '2500 이상']
act['CalorieGroup'] = pd.cut(act['Calories'], bins=bins, labels=labels, right=False)

print("✓ CalorieGroup 컬럼 추가 완료")
print(f"\n칼로리 그룹별 데이터 개수:")
print(act['CalorieGroup'].value_counts().sort_index())
# %%
# 하루동안 앉아있는 시간의 비율
act["SedentaryRatio"] = act["SedentaryMinutes"] / 1440 #1440 : 하루 총 1440분.
act["SedentaryRatio"]
# %%
# DayType 분류
import numpy as np

conditions = [
    (act["TotalSteps"] >= 7000) | (act["TotalActiveMinutes"] >= 60), # Active
    (act["SedentaryRatio"] >= 0.75) & (act["TotalSteps"] > 0), # Over-Sedentary
    (act["TotalSteps"] < 3000) & (act["SedentaryRatio"] >= 0.50) & (act["TotalSteps"] > 0)  # Low Engagement
]

choices = ["Active Day", "Over-Sedentary Day", "Low Engagement Day"]

act["DayType"] = np.select(conditions, choices, default="Normal Day")

# %%
# 운동 강도 점수 (Intensity_Score)
act['Intensity_Score'] = (
    (act['VeryActiveMinutes'] * 2) + 
    (act['FairlyActiveMinutes'] * 1.5) + 
    (act['LightlyActiveMinutes'] * 1)
)
# %% 
# 효율성 지표(Efficiency) 만들기
# 공식: 운동 강도 점수(Intensity_Score) / 총 활동 시간(Total_Active_Minutes)
# 의미: 1분 움직일 때마다 몇 점이나 따냈나 (높을수록 고강도 운동!)
# 주의: 활동 시간이 0분인 경우 에러가 나지 않도록 np.where로 예외 처리
act['Efficiency'] = np.where(
    act['Total_Active_Minutes'] > 0, 
    act['Intensity_Score'] / act['Total_Active_Minutes'], 
    0
)

# %%
#   주요 스탯(능력치) 찍는법
key_stats = [
    'TotalSteps',           # 걸음 수
    'TotalDistance',        # 이동 거리 (km)
    'VeryActiveMinutes',    # 고강도 운동 시간 (분)
    'FairlyActiveMinutes',  # 중강도 운동 시간 (분)
    'LightlyActiveMinutes', # 저강도 운동 시간 (분)
    'Calories',             # 소모 칼로리
    'Efficiency'            # 효율성 (가성비)
]
# %%
start_date = '2016-04-01'
end_date = '2016-05-12'
act = act[(act['ActivityDate'] >= start_date) & (act['ActivityDate'] <= end_date)].copy()
# %%

#이상치 확인
print("\n=== IQR 방법 이상치 개수 ===")

outlier_cols = ['TotalSteps', 'TotalDistance', 'TrackerDistance',
                'LoggedActivitiesDistance', 'VeryActiveDistance',
                'ModeratelyActiveDistance', 'LightActiveDistance',
                'VeryActiveMinutes','FairlyActiveMinutes', 
                'LightlyActiveMinutes', 
                'SedentaryMinutes', 'Calories']

for col in outlier_cols:
    Q1 = act[col].quantile(0.25)
    Q3 = act[col].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    outliers = act[(act[col] < lower_bound) | (act[col] > upper_bound)]
    
    if len(outliers) > 0:
        print(f"{col}: {len(outliers)}개 (하한: {lower_bound:.2f}, 상한: {upper_bound:.2f})")

# 3-4. 이상치 제거
def remove_outliers_iqr(df, columns):
    """IQR 방법으로 이상치 제거"""
    df_clean = df.copy()
    
    for col in columns:
        Q1 = df_clean[col].quantile(0.25)
        Q3 = df_clean[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        # 이상치 제거
        df_clean = df_clean[(df_clean[col] >= lower_bound) & (df_clean[col] <= upper_bound)]
    
    return df_clean

# 이상치 제거할 주요 컬럼
outlier_cols = ['TotalSteps', 'TotalDistance', 'TrackerDistance',
                'LoggedActivitiesDistance', 'VeryActiveDistance',
                'ModeratelyActiveDistance', 'LightActiveDistance',
                'VeryActiveMinutes','FairlyActiveMinutes', 
                'LightlyActiveMinutes', 
                'SedentaryMinutes', 'Calories']

print(f"이상치 제거 전: {len(act)}행")
act = remove_outliers_iqr(act, outlier_cols)
#print(f"이상치 제거 후: {len(act1)}행")
#print(f"제거된 행: {len(act) - len(act1)}행")
#print("✓ 이상치 제거 완료")

act.head()

# %%
# 4-1. 최종 데이터 정보
print("=== 최종 데이터 정보 ===")
print(f"행 개수: {len(act)}")
print(f"열 개수: {len(act.columns)}")
print(f"\n데이터 타입:\n{act.dtypes}")

# %%

# 칼로리 효율
act["CaloriesPerKm"] = np.where(
    act["TotalDistance"] > 0,
    act["Calories"] / act["TotalDistance"],
    np.nan
)

# 2. NaN 제거 (중요!)
act = act.dropna(subset=['CaloriesPerKm'])

act.head()

# %%
# 소모칼로리 & 지속성 분류
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
class activity_level(Enum):
    LEVEL_1 = "저활동"  # 1000-1500 kcal
    LEVEL_2 = "보통활동"  # 1500-2000 kcal
    LEVEL_3 = "활동적"  # 2000-2500 kcal
    LEVEL_4 = "고활동"  # 2500+ kcal

class persistence_level(Enum):
    TYPE_A = "안정적"  # 평균(32일) 이상
    TYPE_B = "유동적"  # 평균(32일) 미만
   

class PersonaType(Enum):
    Newbie  = activity_level.LEVEL_1, persistence_level.TYPE_A & persistence_level.TYPE_B #"입문자형"
    Beginner = activity_level.LEVEL_2, persistence_level.TYPE_B #"초보자형"
    Turtle = activity_level.LEVEL_2, persistence_level.TYPE_A #"거북이형"
    Burst_Learner = activity_level.LEVEL_3, persistence_level.TYPE_B #"벼락치기형"
    Ideal_student = activity_level.LEVEL_3, persistence_level.TYPE_A #"모범생형"
    Lazy_genius = activity_level.LEVEL_4, persistence_level.TYPE_B #"게으른 천재형"
    Veteran = activity_level.LEVEL_4, persistence_level.TYPE_A  # "고인물형"


@dataclass
class MonthlyActivityData:
    """한 달 동안 수집된 활동 데이터"""
    total_steps: int = 0
    total_distance: float = 0.0
    very_active_minutes: int = 0
    fairly_active_minutes: int = 0
    lightly_active_minutes: int = 0
    CalorieGroup: category    
    efficiency: float = 0.0
    
    # 추가 정보 (선택적) 소윤님 혹시 실행 필요하시면 써주세요:
    active_days: int = 0  # 활동한 날 수
    max_streak: int = 0  # 최대 연속 활동일
    total_days: int = 30  # 전체 기간 (기본 30일)


@dataclass
class PersonaInfo:
    """페르소나 상세 정보"""
    persona_type: PersonaType
    activity_level: activity_level
    persistence_type: persistence_level
    description: str
    strengths: List[str]
    weaknesses: List[str]
    short_term_goal: str
    medium_term_goal: str
    long_term_goal: str
    recommended_programs: List[str]
    """페르소나 자동 분류"""


    class MonthlyPersonaClassifier:
        def __init__(self):
          self.persona_info = self._load_persona_info()
        """페르소나 정의 초기화"""
        def classify(self, data: MonthlyActivityData) -> PersonaInfo:

      