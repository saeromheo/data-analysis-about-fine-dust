# sns 데이터 월별로 나누기

import pandas as pd
from datetime import datetime
import os


# 파일 경로 찾기
def search_files(path):
    for root, _, files in os.walk(path):
        for file in files:
            file_name = os.path.join(root, file).replace('\\', '/')
            yield file_name


# 8개의 SNS파일을 카페/블로그로 나누고 월별로 쪼개기
def to_month_separate(data_dir, month, section):
    for idx in range(1, 9):
        # sns파일 불러오기
        print(f'{idx}번째 데이터 불러오기...')
        df = pd.read_excel(f'{data_dir}/SNS데이터/SNS_{idx}.xlsx', index_col='DATE')
        df = df[df['CONTENT'].notna()]
        df.index = [datetime.strptime(str(x)[:-2], '%Y%m%d%H%M') for x in df.index]

        save_dir = f'{data_dir}/pre/sns/sns_month/{section}'
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        a = []
        for i in month:
            print(f'{i} 저장 중...')
            output_file_name = f"{i}_{section}"

            # 섹션(카페/블로그)으로 나눈 뒤 해당 월의 데이터가 있는지 확인
            try:
                cafe = df[df.SECTION == section][i]
            except KeyError:
                continue

            # 해당 월의 데이터가 있으면 xlsx파일로 저장
            if cafe.empty is False:
                cafe.to_excel(f'{save_dir}/{output_file_name}{idx}.xlsx', header=True, index=True, engine='xlsxwriter')
                a.append(len(cafe))
                print('저장 완료')
                continue
            print('해당 월 데이터 없음')

        # 데이터 추출 제대로 되었는지 데이터 개수 비교
        print(sum(a) == len(df[df.SECTION == section]), '\n\n')


# 월별로 쪼갠 데이터를 합쳐서 하나의 데이터로 만들기
def to_month_all(data_dir, month, section):
    search_dir = f'{data_dir}/pre/sns/sns_month/{section}'
    save_dir = f'{data_dir}/pre/sns/sns_month/total'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # naver 블로그에서 필수로 포함되는 내용
    naver1 = 'URL 복사 이웃추가 본문 기타 기능 번역보기'
    naver2 = 'URL 복사 이웃추가 본문 기타 기능 지도로 보기 전체지도지도닫기 번역보기'  # 지도가 추가된 네이버블로그
    naver3 = 'URL 복사 본문 기타 기능 번역보기'  # 이웃추가가 없는 경우

    for idx in month:
        total = pd.DataFrame()
        output_file_name = f"{idx}_{section}"

        print(f'{idx}_{section} 데이터 불러오기...')
        for name in search_files(search_dir):
            # 이름에 해당 월이 들어가 있으면 데이터 가져와서 합치기
            if idx in name:
                df = pd.read_excel(f'{name}')
                total = pd.concat([total, df])

        # 블로그를 네이버블로그와 그 외 블로그로 분류하기 위한 if문 시작 (이하 8/8 새롬 추가)
        if section == '블로그':
            # 네이버 블로그인 경우 본문 내 제목과 반복문구 삭제 작업
            total.loc[total['CONTENT'].str.contains(f'{naver1}|{naver2}|{naver3}'), 'SECTION'] = 'NAVER'
            total.loc[total['SECTION'] != 'NAVER', 'SECTION'] = 'ETC'
            for j in range(len(total)):
                if total['SECTION'].iloc[j] == 'NAVER':
                    total['CONTENT'].iloc[j] = total['CONTENT'].iloc[j].replace(naver1, ' ').replace(naver2, ' ')\
                        .replace(naver3, ' ').replace(str(total['TITLE'].iloc[j]), ' ')  # 반복문구와 본문 내 포함된 제목 삭제

        total.to_excel(f'{save_dir}/{output_file_name}.xlsx', header=True, index=False, engine='xlsxwriter')
        print(f'{idx}_{section} 저장 완료 \n')
    print(f'{section} finish! \n\n')


if __name__ == '__main__':
    data_directory = '../data'

    months = ['2018-04', '2018-05', '2018-06', '2018-07', '2018-08', '2018-09',
              '2018-10', '2018-11', '2018-12', '2019-01', '2019-02', '2019-03']

    to_month_separate(data_directory, months, '카페')
    to_month_separate(data_directory, months, '블로그')

    to_month_all(data_directory, months, '카페')
    to_month_all(data_directory, months, '블로그')
