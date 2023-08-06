from code.pre_card import card2location
from code.pre_flow import age_floating2location
from code.pre_flow import time_floating2location
from code.pre_gs import gs2location
from code.pre_weather import station2location


# 데이터 전처리
def pre_processing(data_dir):
    print('카드 데이터 전처리...')
    card2location(data_dir)  # 카드ㅁ ㅓㅣ 출

    print('유동인구 데이터 전처리...')
    time_floating2location(data_dir)  # 시간대 유동
    age_floating2location(data_dir)  # 성연령 유동

    print('GS 데이터 전처리...')
    gs2location(data_dir)  # gs 리테일

    print('환경기상 데이터 전처리...')
    for freq in ['D', 'H']:  # D: day, H: hour
        station2location(data_dir, freq)


if __name__ == '__main__':
    data_directory = '../data'  # data folder directory
    pre_processing(data_directory)
