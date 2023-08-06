import os
import pandas as pd
import numpy as np
from datetime import datetime


def station2location(data_dir, frequency):
    # 구 이름, 사용 columns
    gu_dct = {'종로구': [1, 4],
              '노원구': [7, 10]}

    # 데이터 경로
    weather_file = f'{data_dir}/01_Innovation 분야 데이터 정의서(통합)/04_Innovation 분야_환경기상데이터(케이웨더)_데이터정의서(행정동추가).xlsx'
    h_code_file = f'{data_dir}/GS리테일_동별 매출지수용 기준값 확인_AMT_NEW.xlsx'
    search_dir = f'{data_dir}/환경기상데이터'
    save_dir = f'{data_dir}/pre/weather'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    for gu_name, use_cols in gu_dct.items():
        # load files
        gu = pd.read_excel(weather_file, sheet_name='경진대회용 후보 지점',
                           usecols=use_cols, names=['스테이션', '행정동'])
        gu['행정동'] = gu['행정동'].str.replace(',', '.').str.replace(' ', '')  # 행정동 이름 수정
        code = pd.read_excel(h_code_file, skiprows=1, sheet_name='참고)구_행정동코드',
                             usecols=[3, 4], names=['행정동코드', '행정동'])

        # join dataframes
        gu = gu.join(code.set_index('행정동'), on='행정동')
        gu = gu.dropna(how='any')  # 천연동, 명동 등 제외

        # 여러 측정기 -> 동마다 평균|최대 측정값을 계산하여 새로운 파일 생성
        for h in set(gu['행정동']):
            # 특정 동의 데이터
            temp = gu.loc[gu['행정동'] == h]

            # 현재 동의 미세먼지 측정기 코드들
            stations = set(temp['스테이션'].values)

            # 빈 데이터프레임: 현재 작업중인 동의 정보를 담을 base dataframe
            base_df = pd.DataFrame()

            # 현재 동의 모든 측정기에서 구한 값의 평균 계산
            for s in stations:
                # 파일 불러오기
                file_name = f"{search_dir}/{gu_name}/{s}.csv"
                df = pd.read_csv(file_name, delimiter=',', index_col='tm',
                                 usecols=[0, 3, 6, 7, 8, 9])  # tm, pm10, noise, temp, humi, pm25

                # 결측치(-999) NaN으로 변경
                df = df.replace(-999, np.NaN)
                df = df.replace(-9999, np.NaN)

                # 현재 동의 모든 측정기 값을 join
                base_df = pd.concat((base_df, df))

            # frequency 단위로 그룹
            base_df.index = [datetime.strptime(str(x), '%Y%m%d%H%M') for x in base_df.index]
            base_df = base_df.groupby(pd.Grouper(freq=frequency)).mean()

            # to csv
            for h_c in temp['행정동코드'].values:
                # 출력 파일 이름: 행정동 코드
                output_file_name = f"{int(h_c)}_{frequency}"
                base_df.to_csv(f"{save_dir}/{output_file_name}.csv", header=True, index=True)


if __name__ == '__main__':
    data_directory = '../data'  # data folder directory
    for freq in ['D', 'H']:  # D: day, H: hour
        station2location(data_directory, freq)
