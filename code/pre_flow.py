import os
import pandas as pd
from datetime import datetime


# 파일 탐색
def search_files(path):
    for root, _, files in os.walk(path):
        for file in files:
            file_name = os.path.join(root, file).replace('\\', '/')
            yield file_name


def time_floating2location(data_dir):
    # 데이터 경로
    search_dir = f'{data_dir}/유동인구데이터/시간대유동'
    save_dir = f'{data_dir}/pre/time_floating'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # 전체기간을 담을 빈 dataframe
    base_df = pd.DataFrame()

    # search_dir 탐색
    for file_name in search_files(search_dir):
        df = pd.read_csv(file_name, delimiter='|', index_col='STD_YMD')
        df = df.drop(columns=['STD_YM', 'HDONG_NM'])
        base_df = pd.concat((base_df, df))

    for h in set(base_df['HDONG_CD']):
        # 특정 동의 데이터
        df = base_df[base_df['HDONG_CD'] == h].drop(columns=['HDONG_CD'])

        # output file name
        output_file_name = f"{save_dir}/{str(h)[:8]}_flow.csv"

        for cc in df.keys():
            c = cc.split('_')[1]
            df = df.rename(columns={cc: c})
        df = pd.DataFrame({'flow': df.unstack()})
        df.index = [datetime.strptime(f"{i[1]}{i[0]}", '%Y%m%d%H') for i in df.index]
        df = df.sort_index()

        # to csv
        df.to_csv(output_file_name, header=True, index=True)


def age_floating2location(data_dir):
    # 데이터 경로
    search_dir = f'{data_dir}/유동인구데이터/성연령유동'
    save_dir = f'{data_dir}/pre/age_floating'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # 전체기간을 담을 빈 dataframe
    base_df = pd.DataFrame()

    # search_dir 탐색
    for file_name in search_files(search_dir):
        df = pd.read_csv(file_name, delimiter='|', index_col='STD_YMD')
        df = df.drop(columns=['STD_YM', 'HDONG_NM'])
        base_df = pd.concat((base_df, df))

    for h in set(base_df['HDONG_CD']):
        # 특정 동의 데이터
        temp = base_df[base_df['HDONG_CD'] == h].drop(columns=['HDONG_CD'])

        # output file name
        output_file_name = f"{save_dir}/{str(h)[:8]}_flow_age.csv"

        df = pd.DataFrame()

        for gender, gender_code in {'WMAN': 'F', 'MAN': 'M'}.items():
            # 특정 성별 column만 선택
            cols = [k for k in temp.keys() if k.startswith(gender)]
            gender_temp = temp[cols]

            # column명 변경
            for cc in gender_temp.keys():
                c = cc.split('_')[-1]
                gender_temp = gender_temp.rename(columns={cc: c})

            # 성별구분 column 추가
            gender_temp['SEX_CD'] = gender_code

            df = pd.concat((df, gender_temp))

        df.index = [datetime.strptime(str(x), '%Y%m%d') for x in df.index]
        df = df.sort_index()

        # 카드데이터와 연령대 통일
        df['0024'] = df['0004'] + df['0509'] + df['1014'] + df['1519'] + df['2024']
        df['65U'] = df['6569'] + df['70U']
        df = df.drop(columns=['0004', '0509', '1014', '1519', '2024', '6569', '70U'])

        # column 순서 변경
        cols = df.columns.tolist()
        cols = cols[-2:-1] + cols[:-3] + cols[-1:] + cols[-3:-2]
        df = df[cols]

        # to csv
        df.to_csv(output_file_name, header=True, index=True)


if __name__ == '__main__':
    data_directory = '../data'  # data folder directory
    time_floating2location(data_directory)
    age_floating2location(data_directory)
