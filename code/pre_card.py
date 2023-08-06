import os
import pandas as pd
from datetime import datetime


def card2location(data_dir):
    # 데이터 경로
    search_dir = f'{data_dir}/CARD_SPENDING_190809.txt'
    save_dir = f'{data_dir}/pre/card'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # load files
    card_data = pd.read_csv(search_dir, delimiter='\t', index_col='STD_DD')
    card_data.index = [datetime.strptime(str(x), '%Y%m%d') for x in card_data.index]

    # 구 코드와 동 코드 합쳐서 행정동 코드로 변환
    card_data['CD'] = '11' + card_data['GU_CD'].apply(str) + card_data['DONG_CD'].apply(str)

    # 구 코드와 동 코드 삭제
    card_data = card_data.drop(['GU_CD', 'DONG_CD'], axis=1)

    for c in set(card_data['CD']):
        # 특정 동의 데이터
        temp = card_data.loc[card_data['CD'] == c]

        temp.to_csv(f"{save_dir}/{c}.csv", header=True, index=True)


if __name__ == '__main__':
    data_directory = '../data'  # data folder directory
    card2location(data_directory)
