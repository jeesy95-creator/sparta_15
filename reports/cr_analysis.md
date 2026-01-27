FitBit 사용자 활동 데이터 분석 보고서 (Analysis Report)
1. 개요 (Overview)
본 분석은 FitBit 사용자의 활동 로그(act) 데이터를 기반으로 **사용자의 기록 패턴(자동 vs 수동)**과 시계열 활동 추세를 파악하는 것을 목적으로 한다. 특히 데이터 수집 초기 단계의 불안정성을 식별하고, 사용자 유형을 분류하여 행동 패턴을 시각화하는 데 중점을 두었다.

2. 데이터 전처리 (Data Preprocessing)
2.1 날짜 형식 변환 및 정렬
ActivityDate 컬럼을 문자열에서 datetime 객체로 변환.

시계열 분석의 정확성을 위해 날짜순으로 데이터 정렬 수행.

2.2 파생 변수 생성
DateRange (주차 구간): 데이터의 시작일(최소 날짜)을 기준으로 7일 단위의 주차(Week) 범위를 생성하여 주별 분석 용이성 확보.

UserCategory (유형 분류): TrackerDistance(기기 자동 기록)와 LoggedActivitiesDistance(수동 입력) 유무에 따라 사용자 유형 분류.

3. 주요 분석 내용 및 시각화
3.1 사용자 기록 패턴 분석 (User Recording Pattern)
사용자가 활동을 기록하는 방식(자동 트래커 사용 여부 vs 수동 입력 여부)을 분석하여 사용자 그룹을 정의함.

분석 로직:

Total Count: 전체 기록 횟수.

Manual Count: 수동 입력(LoggedDistance > 0) 횟수.

Auto Count: 자동 트래커(TrackerDistance > 0) 기록 횟수.

Pure Manual: 자동 기록 없이 오직 수동 입력만 하는 사용자 식별.

시각화 (Bar & Line Chart):

막대 그래프: 사용자별 총 기록 횟수 비교.

선 그래프: 수동 입력 횟수(주황색)와 자동 기록 횟수(파란색)를 중첩하여 패턴 비교.

결과: 대부분의 사용자는 자동 기록과 수동 입력을 병행하거나 자동 기록 위주이나, 특정 소수 사용자(예: Id 2891...)는 완전 수동 입력 패턴을 보임.

3.2 시계열 활동 추세 분석 (Temporal Trends)
전체 기간을 7일 단위로 나누어(DateRange), 총 활동 시간과 활성 사용자 수의 변화를 격자형 그래프(FacetGrid)로 시각화함.

분석 지표:

총 활동 시간 (TotalActiveMinutes): 사용자의 활동 강도 파악.

활성 사용자 수 (Unique User Count): 일자별 데이터 기록 참여도 파악.

시각화 (FacetGrid Line Plot):

각 주차별(Subplot) 날짜 흐름에 따른 지표 변화 추적.

신뢰구간(Confidence Interval)을 표시하여 데이터의 변동성 확인.

개선 사항: X축(날짜) 꼬임 방지를 위해 각 Subplot별 xlim 개별 설정 및 여백(Padding) 추가.

3.3 요일별 활동 패턴 (Day of Week Analysis)
요일에 따른 평균 활동량의 차이를 분석.

분석 로직: 요일 순서(Mon ~ Sun)를 정렬(Reindex)하여 요일별 평균 활동 시간 집계.

시각화: 선 그래프를 통해 주중과 주말의 활동량 차이 확인.

4. 주요 인사이트 (Key Insights)
4.1 데이터 안정화 시기 식별
초기 불안정 구간 (~3월 말): 3월 12일 ~ 4월 1일 구간은 사용자 수가 1~3명 내외로 매우 적고, 활동 시간의 편차가 극심함. 초기 테스트 기간으로 추정됨.

안정화 구간 (4월 초 ~): 4월 2일부터 사용자 수가 30명 내외로 안정화되며, 활동 시간 데이터의 신뢰구간이 좁아짐. 통계적 유의미성은 4월 2일 이후 데이터부터 확보됨.

4.2 사용자 유형의 이원화
대다수 사용자는 트래커를 활용한 자동 기록을 주된 수단으로 사용함.

'완전 수동 입력자' 그룹이 존재하며, 이들은 트래커 데이터가 0임에도 꾸준히 활동 로그를 남기는 특이 패턴을 보임.

4.3 활동량 및 이탈 징후
활동 수준: 안정화 구간 기준, 일 평균 활동 시간은 200~300분 내외로 높게 나타남 (생활 활동 포함 추정).

이탈 징후: 5월 2주차(5/7 ~)로 접어들며 사용자 수와 활동 시간이 동반 하락하는 추세가 관찰됨. 프로젝트 종료 임박 또는 사용자 피로도(Fatigue) 누적 가능성 있음.

5. 사용된 주요 코드 (Key Code Snippets)
5.1 안전한 시각화 라벨링 및 축 설정
Python
# 막대 그래프 라벨링 (Safe Labeling)
for container in ax.containers:
    ax.bar_label(container, fmt='%d', padding=3)

# Y축 범위 자동 확보
max_val = data['Count'].max()
plt.ylim(0, max_val * 1.2)
5.2 시계열 FacetGrid 최적화
Python
# 각 Subplot별 X축 범위 개별 설정 (축 꼬임 방지)
for ax in g.axes.flat:
    if ax.get_lines():
        dates = ax.get_lines()[0].get_xdata()
        buffer = 0.5 # 반나절 여백
        ax.set_xlim(dates.min() - buffer, dates.max() + buffer)