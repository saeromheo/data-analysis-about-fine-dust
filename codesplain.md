## 전처리 및 분석과정 코드설명

> 양적 데이터

1. nnpunch.py : 데이터 전처리, 군집분석, 회귀분석, 분산분석을 전부 실행(2부터 5까지의 파일 전부 실행)

2. pre_main.py :  데이터 전처리 실행
    1. pre_card.py : 카드매출데이터 전처리. 인덱스를 날짜 형식으로 변경 후 행정동코드를 기준으로 파일 분리
    2. pre_flow.py : 유동인구데이터 전처리
        - time_floating2location : 유동인구를 시간대별로 분류한 뒤 행정동코드를 기준으로 파일 분리
        - age_floating2location : 유동인구를 성/연령별로 분류한 뒤 행정동코드를 기준으로 파일 분리
    3. pre_gs.py : gs리테일데이터 전처리. 인덱스를 날짜 형식으로 변경 후 행정동코드를 기준으로 파일 분리
    4. pre_weather.py : 환경기상데이터 전처리. 각 행정동에 속한 측정기의 데이터를 병합한 뒤 1일/1시간 기준으로 평균을 구한 뒤 저장

3. k_means_main.py : 군집분석 실행
    1. pre_km.py : 군집분석을 위한 전처리a
        - gather_data : 미세먼지 데이터가 존재하는 행정동의 카드매출, 유동인구, gs리테일, 환경기상데이터를 병합 후 표준화 진행
        - select_cluster : 적합한 군집의 갯수 확인
    2. km.py : 군집분석
        - corr_select : 다중공선성 제거를 위해 상관분석 진행 후 상관이 높은 컬럼 제거
        - vif_check : 다중공선성 제거를 위해 VIF값 확인 
        - Km : K-means 군집분석 진행
        - logistic_check : 군집분석 검증을 위한 OvR 로지스틱 회귀분석 진행 및 예측결과 그래프 작성
    3. logistic.py : 군집별 회귀분석
        - logistic : 군집분석 검증을 위한 로지스틱 회귀분석 진행 및 예측결과 그래프 작성
    4. map_km.py : 각 군집에 속한 행정동이 나타나 있는 지도 그리기

4. gather_datas.py : 군집별 데이터 병합
    - gater_clusters : 각 군집에 속한 행정동의 데이터를 병합한 후 날짜를 기준으로 평균을 구한 뒤 저장

5. reg_season_gender_age.py : 군집별 회귀분석 실행
    - gather_labels_df : 군집별로 각 데이터를 병합 후 성별에 따라 데이터를 나눈 뒤 표준화 진행
    - p_select : 계절별로 환경기상, 유동인구 데이터를 독립변수로 하는 회귀분석 진행 후 통계적으로 유의미한 종속변수만 선택
    - reg_plot : 회귀분석 결과파일 작성 및 유의미한 종속변수와 미세먼지 수치 간의 경향성 확인을 위한 그래프 작성
    - reg_season_plot : 계절별로 reg_plot 실행

6. anova.py : 군집별 분산분석 실행
    - gater_labels_df : 군집별로 각 데이터를 병합 후 성별에 따라 데이터를 나눈 뒤 미세먼지 수치에 따라 3개의 집단으로 구분한 mise변수 추가
    - anova : mise변수를 독립변수로 하는 분산분석 진행 후 통계적으로 유의미한 종속변수의 결과파일 작성 및 mise변수를 기준으로 평균을 구한 뒤 막대그래프 작성.
    - anova_season : 계절별로 anova 실행


> 텍스트 데이터(SNS 데이터)

1. pre_sns.py : SNS데이터 전처리
    - to_month_separate : 8개의 SNS데이터를 각각 섹션(블로그, 카페)/월별로 분리
    - to_month_all : 불필요한 내용 삭제 후 하나의 섹션(블로그, 카페)/월별 파일로 병합

2. sns_noun.py : 명사추출
    - extract_noun : 한글 외 다른 문자를 제거한 후 Okt를 이용하여 섹션(블로그, 카페)/월별로 명사추출

3. sns_frequency.py : 빈도분석
    - sns_separate_mise : 미세먼지 수치에 따라 3개의 집단으로 구분한 mise변수 추가
    - make_freq : 섹션별(블로그, 카페) 빈도분석 진행
    - make_freq_season : 섹션(블로그, 카페)/계절별 빈도분석 진행
    - make_freq_cluster : 섹션(블로그, 카페)/미세먼지수치별 빈도분석 진행
    - freq_wordcloud : 섹션별/계절별/미세먼지수치별 빈도분석 결과로 워드클라우드 생성

4. sns_w2v.py : Word2Vector모델 생성 및 결과 분석
    - integration : 월별로 구분되어 있는 명사 데이터를 계절별로 통합
    - make_w2v : 계절별로 Word2Vector모델 생성
    - load_w2v : Word2Vector모델 결과 탐색 및 시각화