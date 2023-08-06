import pandas as pd
from konlpy.tag import *
import re
import os
# 맥에서 한글 정규식 사용 위한 코드
import unicodedata


def search_files(path):
    for root, _, files in os.walk(path):
        for file in files:
            file_name = os.path.join(root, file).replace('\\', '/')
            yield file_name


def extract_noun(search_dir, section):
    for name in search_files(search_dir):
        name = unicodedata.normalize('NFC', name)   # 맥에서 한글 정규식 사용 위한 코드

        if section in name:
            print(f'{name} 데이터 불러오기...')

            df = pd.read_excel(f'{name}', index_col=0)

            print(len(df))  # 전체 데이터 개수

            # content칼럼에서 한글 및 숫자만 추출하여 각 문장을 리스트에 반환
            content = [hangul.sub('', str(i)) for i in df.CONTENT]

            results = []
            for i, line in enumerate(content):
                print(f"{i}번째 추출")
                # 명사 추출
                malist = okt.nouns(line)
                r = [word for word in malist if len(word) > 1]
                # 각 문장에서 추출한 2글자 이상의 명사를 띄어쓰기로 구분하여 한 문장으로 다시 재조립
                rl = (" ".join(r)).strip()
                results.append(rl)

            cafe_file = f"{name.split('/')[-1][:-5]}.txt"

            with open(cafe_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(results))

            print(f'{name}파일 완료')


if __name__ == '__main__':
    search_directory = '../data/pre/sns/sns_month/total'
    save_dir = "../data/sns/total_noun"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    hangul = re.compile('[^ ㄱ-ㅣ가-힣0-9]+')
    okt = Okt()

    extract_noun(search_directory, '카페')
    extract_noun(search_directory, '블로그')
