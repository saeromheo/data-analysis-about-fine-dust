import os
import pandas as pd
from datetime import datetime


def gs2location(data_dir):
    # 데이터 경로 설정
    search_dir = f'{data_dir}/GS리테일_동별 매출지수용 기준값 확인_AMT_NEW.xlsx'
    save_dir = f'{data_dir}/pre/gs'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # load file
    gs_data = pd.read_excel(search_dir, sheet_name='종합테이블', index_col='OPER_DT')
    gs_data.index = [datetime.strptime(str(x), '%Y%m%d') for x in gs_data.index]  # index를 날짜 형식으로 변경

    # 행정동 코드와 중복되는 구 코드 삭제
    gs_data = gs_data.drop(['BOR_CD'], axis=1)

    # 행정동 코드명 수정, 카드 매출 데이터와 코드명 통일
    gs_data.columns.values[0] = 'CD'

    # '분석용 상품 대분류 코드'를 '분석용 상품 대분류 명'으로 변경
    gs_data.columns.values[1:] = ['매출지수', '식사', '간식', '마실거리', '홈리빙', '헬스뷰티', '취미여가활동', '사회활동', '임신육아']

    # %값을 금액으로 변경
    gs_data['매출지수'] = gs_data['매출지수'] * 100
    for i in range(2, len(gs_data.columns)-1):
        gs_data.iloc[:, i] = gs_data['매출지수'] * gs_data.iloc[:, i]

    # 행정동 코드를 기준으로 파일 분리
    for c in set(gs_data['CD']):
        # 특정 동의 데이터 추출
        temp = gs_data.loc[gs_data['CD'] == c]

        # 추출한 동별 데이터를 csv 파일로 저장
        temp.to_csv(f"{save_dir}/{c}.csv", header=True, index=True)


if __name__ == '__main__':
    data_directory = '../data'  # data folder directory
    gs2location(data_directory)
