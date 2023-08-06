import os
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans


# 파일 탐색
def search_files(path):
    for root, _, files in os.walk(path):
        for file in files:
            file_name = os.path.join(root, file).replace('\\', '/')
            yield file_name


def gather_data(data_dir):
    # 미세먼지 데이터가 존재하는 동
    weather_dir = f'{data_dir}/pre/weather'  # 미세먼지 경로
    dong = [file_name.split('/')[-1][:8] for file_name in search_files(weather_dir)]
    dong = sorted(list(set(dong)))

    # weather
    weather_df = pd.DataFrame()
    for f in search_files(weather_dir):
        cd = f.split('/')[-1][:8]
        if cd in dong:
            temp_df = pd.read_csv(f, delimiter=',', index_col=0, parse_dates=True)
            temp_df['CD'] = cd
            weather_df = pd.concat((weather_df, temp_df))
    weather_df = weather_df.groupby('CD').mean()  # 평균

    # gs
    gs_dir = f'{data_dir}/pre/gs'
    gs_df = pd.DataFrame()
    for f in search_files(gs_dir):
        cd = f.split('/')[-1][:8]
        if cd in dong:
            temp_df = pd.read_csv(f, delimiter=',', index_col=0, parse_dates=True)
            gs_df = pd.concat((gs_df, temp_df))
    gs_df['CD'] = gs_df['CD'].apply(str)
    gs_df = gs_df.groupby('CD').mean()  # 평균

    # flow
    flow_dir = f'{data_dir}/pre/time_floating'
    flow_df = pd.DataFrame()
    for f in search_files(flow_dir):
        cd = f.split('/')[-1][:8]
        if cd in dong:
            temp_df = pd.read_csv(f, delimiter=',', index_col=0, parse_dates=True)
            temp_df['CD'] = cd
            flow_df = pd.concat((flow_df, temp_df))
    flow_df = flow_df.groupby('CD').mean()  # 평균

    # card
    card_dir = f'{data_dir}/pre/card'
    card_df = pd.DataFrame()
    for f in search_files(card_dir):
        cd = f.split('/')[-1][:8]
        if cd in dong:
            temp_df = pd.read_csv(f, delimiter=',', index_col=0, parse_dates=True)
            # 평균; 업종별 카드 이용금액; 다중공선성으로 성별, 연령대는 제외
            temp_df = temp_df.groupby(['MCT_CAT_CD']).mean()[['USE_AMT']].reset_index()
            temp_df.index = temp_df['MCT_CAT_CD'].apply(str)
            temp_df = temp_df[['USE_AMT']].T
            temp_df['CD'] = cd
            card_df = pd.concat((card_df, temp_df), sort=True)
    card_df = card_df.dropna(axis='columns')  # 결측치가 존재하는 컬럼 제거

    # 데이터 통합
    result = pd.merge(weather_df, gs_df, on='CD', how='inner')
    result = pd.merge(result, flow_df, on='CD', how='inner')
    result = pd.merge(result, card_df, on='CD', how='inner')

    # 행정동명 추가
    h_code_file = f'{data_dir}/GS리테일_동별 매출지수용 기준값 확인_AMT_NEW.xlsx'
    code = pd.read_excel(h_code_file, skiprows=1, sheet_name='참고)구_행정동코드',
                         usecols=[3, 4], names=['CD', '행정동'])
    code['CD'] = code['CD'].apply(str)
    result = result.join(code.set_index('CD'), on='CD')

    # 군집분석을 위해 컬럼명 수정
    # result.columns = [cn.replace(' ', '').replace('&', '').replace('/', '') for cn in result.columns]
    for cn in result.columns:
        try:
            result = result.rename(columns={f'{cn}': f'C{int(cn)}'})
        except ValueError:
            pass

    # CD, 행정동
    cd_list = result.iloc[:, [0, -1]]
    result = result.drop(columns=['CD', '행정동'])

    # 표준화
    result_norm = (result - result.mean()) / result.std()

    return result, result_norm, cd_list


# 적합한 군집의 갯수 확인
def select_cluster(input_df, save_dir):
    sse = []
    for i in range(1, len(input_df)):
        km = KMeans(n_clusters=i, algorithm='auto', random_state=42)
        km.fit(input_df)
        sse.append(km.inertia_)

    plt.plot(range(1, len(input_df)), sse, marker='o')
    plt.xlabel('K')
    plt.ylabel('SSE')

    # save fig
    plt.savefig(f'{save_dir}/n_cluster_sse.png')


if __name__ == '__main__':
    data_directory = '../data'  # data folder directory
    directory = f'{data_directory}/km'
    if not os.path.exists(directory):
        os.makedirs(directory)

    df, df_norm, _cd = gather_data(data_directory)
    df_norm.to_csv('test_norm.csv', header=True, index=False)
    select_cluster(df, directory)
