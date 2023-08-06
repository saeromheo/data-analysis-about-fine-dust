import os
import pandas as pd


# 파일 탐색
def search_files(path):
    for root, _, files in os.walk(path):
        for file in files:
            file_name = os.path.join(root, file).replace('\\', '/')
            yield file_name


# 자료 수집
def gather(data_dir, freq, label_name, h_code):
    save_dir = f'{data_dir}/cluster'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # 구의 모든 데이터 불러오기
    def load_gu_files(search_dir):
        result_df = pd.DataFrame()
        for f in search_files(search_dir):
            if f.split('/')[-1][:8] in h_code:
                temp_df = pd.read_csv(f, delimiter=',', index_col=0, parse_dates=True)
                result_df = pd.concat((result_df, temp_df))
        return result_df

    # 데이터 경로(H/D)
    weather_dir = f'{data_dir}/pre/weather'  # 미세먼지(H/D)
    flow_dir = f'{data_dir}/pre/time_floating'  # 시간대유동(H)
    flow_age_dir = f'{data_dir}/pre/age_floating'  # 성연령유동(D)
    card_dir = f'{data_dir}/pre/card'  # 카드ㅁㅓㅣ출(D)
    gs_dir = f'{data_dir}/pre/gs'  # gs(D)

    if len(h_code) == 1:  # 하나의 동
        h_code = h_code[0]
        # 미세먼지 데이터
        wf = f'{weather_dir}/{h_code}_{freq}.csv'
        weather_df = pd.read_csv(wf, delimiter=',', index_col=0, parse_dates=True)
        if freq == 'H':
            # 시간대유동 데이터
            ff = f'{flow_dir}/{h_code}_flow.csv'
            flow_df = pd.read_csv(ff, delimiter=',', index_col=0, parse_dates=True)
            weather_flow = pd.concat((weather_df, flow_df), axis=1)
            weather_flow.to_csv(f'{save_dir}/{label_name}_weather_flow.csv', header=True, index=True)
        elif freq == 'D':
            # 성연령유동 데이터
            af = f'{flow_age_dir}/{h_code}_flow_age.csv'
            flow_age_df = pd.read_csv(af, delimiter=',', index_col=0, parse_dates=True)

            # 카드 데이터
            cf = f'{card_dir}/{h_code}.csv'
            card_df = pd.read_csv(cf, delimiter=',', index_col=0, parse_dates=True)
            card_df = card_df.drop(columns=['CD'])

            # gs 데이터
            gf = f'{gs_dir}/{h_code}.csv'
            gs_df = pd.read_csv(gf, delimiter=',', index_col=0, parse_dates=True)
            gs_df = gs_df.drop(columns=['CD'])

            # to csv
            weather_df.to_csv(f'{save_dir}/{label_name}_weather.csv', header=True, index=True)
            flow_age_df.to_csv(f'{save_dir}/{label_name}_flow_age.csv', header=True, index=True)
            card_df.to_csv(f'{save_dir}/{label_name}_card.csv', header=True, index=True)
            gs_df.to_csv(f'{save_dir}/{label_name}_gs.csv', header=True, index=True)
    else:
        # 미세먼지 데이터
        weather_df = pd.DataFrame()
        for file_name in search_files(weather_dir):
            info = file_name.split('/')[-1]
            if info[:8] in h_code and info[9:10] == freq:
                temp = pd.read_csv(file_name, delimiter=',', index_col=0, parse_dates=True)
                weather_df = pd.concat((weather_df, temp))
        weather_df = weather_df.groupby(pd.Grouper(freq=freq)).mean()
        if freq == 'H':
            flow_df = load_gu_files(flow_dir)  # 시간대유동 데이터
            flow_df = flow_df.groupby(pd.Grouper(freq=freq)).mean()
            weather_flow = pd.concat((weather_df, flow_df), axis=1)
            weather_flow.to_csv(f'{save_dir}/{label_name}_weather_flow.csv', header=True, index=True)
        elif freq == 'D':
            # 성연령유동 데이터
            flow_age_df = load_gu_files(flow_age_dir)
            flow_age_df = flow_age_df.groupby([pd.Grouper(freq=freq), 'SEX_CD']).mean()

            # 카드 데이터
            card_df = load_gu_files(card_dir)
            card_df = card_df.drop(columns=['CD'])
            card_df = card_df.groupby([pd.Grouper(freq=freq), 'MCT_CAT_CD', 'SEX_CD', 'AGE_CD']).mean()

            # gs
            gs_df = load_gu_files(gs_dir)
            gs_df = gs_df.drop(columns=['CD'])
            gs_df = gs_df.groupby([pd.Grouper(freq=freq)]).mean()

            # to csv
            weather_df.to_csv(f'{save_dir}/{label_name}_weather.csv', header=True, index=True)
            flow_age_df.to_csv(f'{save_dir}/{label_name}_flow_age.csv', header=True, index=True)
            card_df.to_csv(f'{save_dir}/{label_name}_card.csv', header=True, index=True)
            gs_df.to_csv(f'{save_dir}/{label_name}_gs.csv', header=True, index=True)


# 군집별 데이터 종합
def gather_clusters(data_dir):
    print('군집별 데이터 종합...')

    labels = pd.read_csv(f'{data_dir}/km/loc_cluster_label.csv', delimiter=',')
    all_ = []
    for i in range(labels['labels'].max() + 1):
        label_list = labels[labels['labels'] == i]['CD'].values
        label_list = list(map(str, label_list))
        all_.extend(label_list)
        gather(data_dir, 'D', f'label{i}', label_list)
    gather(data_dir, 'D', 'label_all', all_)


if __name__ == '__main__':
    data_directory = '../data'  # data folder directory
    gather_clusters(data_directory)
