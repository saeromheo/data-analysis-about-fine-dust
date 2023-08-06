import pandas as pd
import numpy as np
import os
# 맥에서 한글 정규식 사용 위한 코드
import unicodedata
from datetime import datetime
from konlpy.tag import Komoran
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from PIL import Image
from sys import platform
from matplotlib import rcParams, font_manager, rc


def search_files(path):
    for root, _, files in os.walk(path):
        for file in files:
            file_name = os.path.join(root, file).replace('\\', '/')
            yield file_name


def word_filter(freq_data):
    print('단어 필터링 중...')
    komoran = Komoran()
    word_list = []
    for word in freq_data.이름:
        word = unicodedata.normalize('NFC', word)  # 맥에서 한글 정규식 사용 위한 코드
        temp = [tt[1] for tt in komoran.pos(word)]
        if len(set(temp).intersection(["NNG", "NNP"])) != 0:
            word_list.append(word)
        elif len(temp) == 1 and temp != ['NA']:  # trash
            continue
        else:
            word_list.append(word)
    return word_list


def sns_separate_mise(data_dir, section):
    save_directory = '../data/sns/mise'
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    for i in search_files(f'{data_dir}/sns/total_noun'):
        i = unicodedata.normalize('NFC', i)  # 맥에서 한글 정규식 사용 위한 코드
        if section in i:
            print(i)
            with open(i, 'r', encoding='utf-8') as f:
                sns = pd.DataFrame(f.readlines())
            date = pd.read_excel(f'{data_dir}/pre/sns/sns_month/total/{i.split(sep="/")[-1][:-4]}.xlsx', index_col=0, parse_dates=True)
            date.index = [datetime.strptime(str(x)[:10], '%Y-%m-%d') for x in date.index]
            sns = sns.set_index(date.index)
            weather = pd.read_csv(f'{data_dir}/cluster/label_all_weather.csv', index_col=0, parse_dates=True)
            weather['mise'] = 'bad'
            weather['mise'].loc[weather['pm10'] <= 50] = 'good'
            weather['mise'].loc[weather['pm10'] > 100] = 'dead'
            weather = weather[['mise']]
            sd = pd.merge(sns, weather, left_index=True, right_index=True)
            sd = sd.rename(columns={0: 'content'})
            sd.to_excel(f'{save_directory}/{i.split(sep="/")[-1][:-4]}.xlsx', header=True, index=True, engine='xlsxwriter')
            print(f'{i.split(sep="/")[-1][:-4]} 저장완료')


def make_freq(data_dir, section):
    save_directory = '../data/sns/frequency'
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    nouns = {}
    for i in search_files(f'{data_dir}/sns/mise'):
        i = unicodedata.normalize('NFC', i)  # 맥에서 한글 정규식 사용 위한 코드
        if section in i:
            print(f"{i} 파일 확인 중")
            df = pd.read_excel(i, index_col=0)
            for line in df['content']:
                for noun in line.split():
                    if noun not in nouns:
                        nouns[noun] = 0
                    nouns[noun] += 1
    result = pd.DataFrame(nouns.items(), columns=['이름', 'Frequency']).sort_values('Frequency', ascending=False)
    result = result[result['이름'].isin(word_filter(result))]
    result['Frequency'] = result['Frequency'] / sum(result['Frequency']) * 100
    result.to_csv(f'{save_directory}/frequency_{section}.csv', index=False, encoding='ms949')
    print(f'{section} 빈도 저장 완료')


def make_freq_season(data_dir, section):
    save_directory = '../data/sns/frequency'
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    season_dct = {'봄': ['03', '04', '05'],
                  '여름가을': ['06', '07', '08', '09', '10'],
                  '겨울': ['11', '12', '01', '02']}
    for s, mlist in season_dct.items():
        s = unicodedata.normalize('NFC', s)  # 맥에서 한글 정규식 사용 위한 코드
        nouns = {}
        for m in mlist:
            for i in search_files(f'{data_dir}/sns/mise'):
                i = unicodedata.normalize('NFC', i)  # 맥에서 한글 정규식 사용 위한 코드
                if section in i and i.endswith(f'{m}_{section}.xlsx'):
                    print(f"{i} 파일 확인 중")
                    df = pd.read_excel(i, index_col=0)
                    for line in df['content']:
                        for noun in line.split():
                            if noun not in nouns:
                                nouns[noun] = 0
                            nouns[noun] += 1
        result = pd.DataFrame(nouns.items(), columns=['이름', 'Frequency']).sort_values('Frequency', ascending=False)
        result = result[result['이름'].isin(word_filter(result))]
        result['Frequency'] = result['Frequency'] / sum(result['Frequency']) * 100
        result.to_csv(f'{save_directory}/frequency_{section}_{s}.csv', index=False, encoding='ms949')
        print(f"{section}_{s} 빈도 저장 완료")


def make_freq_cluster(data_dir, section):
    save_directory = '../data/sns/frequency'
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    for m in ['good', 'bad', 'dead']:
        nouns = {}
        for i in search_files(f'{data_dir}/sns/mise'):
            i = unicodedata.normalize('NFC', i)  # 맥에서 한글 정규식 사용 위한 코드
            if section in i:
                print(f"{i} 파일 확인 중")
                df = pd.read_excel(i, index_col=0)
                df = df[df['mise'] == m]
                for line in df['content']:
                    for noun in line.split():
                        if noun not in nouns:
                            nouns[noun] = 0
                        nouns[noun] += 1
        result = pd.DataFrame(nouns.items(), columns=['이름', 'Frequency']).sort_values('Frequency', ascending=False)
        result = result[result['이름'].isin(word_filter(result))]
        result['Frequency'] = result['Frequency'] / sum(result['Frequency']) * 100
        result.to_csv(f'{save_directory}/frequency_{section}_{m}.csv', index=False, encoding='ms949')
        print(f"{section}_{m} 빈도 저장 완료")


def freq_wordcloud(data_dir, section):
    save_directory = '../data/sns/wordcloud'
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    for i in ['', '_bad', '_dead', '_good', '_봄', '_여름가을', '_겨울']:
        df = pd.read_csv(f'{data_dir}/sns/frequency/frequency_{section}{i}.csv', encoding='ms949')
        dct = dict(zip(df.이름, df.Frequency))
        wc_mask = np.array(Image.open('./wc_cat.png'))

        wc = WordCloud(background_color='white', font_path='C:/Windows/Fonts/malgun.ttf', max_font_size=80,
                       mask=wc_mask).generate_from_frequencies(dct)
        plt.figure(figsize=(12, 12))
        plt.imshow(wc, interpolation='bilinear')
        plt.axis('off')
        plt.savefig(f'{save_directory}/frequency_{section}{i}.png')
        plt.close()
        print(f'frequency_{section}{i} wordcloud 저장 완료')


if __name__ == '__main__':
    data_directory = '../data'

    # if platform == "darwin":
    #     rc('font', family='AppleGothic')
    #     rcParams['axes.unicode_minus'] = False
    # elif platform == "win32":
    #     font_name = font_manager.FontProperties(fname="C:/Windows/Fonts/malgun.ttf").get_name()
    #     rc("font", family=font_name)
    #     rcParams['axes.unicode_minus'] = False
    #
    # sns_separate_mise(data_directory, '블로그')
    # sns_separate_mise(data_directory, '카페')
    #
    # make_freq(data_directory, '카페')
    # make_freq_season(data_directory, '카페')
    # make_freq_cluster(data_directory, '카페')
    #
    # make_freq(data_directory, '블로그')
    # make_freq_season(data_directory, '블로그')
    # make_freq_cluster(data_directory, '블로그')

    freq_wordcloud(data_directory, '블로그')
    freq_wordcloud(data_directory, '카페')
