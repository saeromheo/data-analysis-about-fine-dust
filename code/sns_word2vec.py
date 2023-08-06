from gensim.models import word2vec
from sklearn.manifold import TSNE
from matplotlib import rcParams, font_manager, rc
from sys import platform
from konlpy.tag import Komoran
import matplotlib.pyplot as plt
import pandas as pd
import os
# 맥에서 한글 정규식 사용 위한 코드
import unicodedata


def search_files(path):
    for root, _, files in os.walk(path):
        for file in files:
            file_name = os.path.join(root, file).replace('\\', '/')
            yield file_name


def integration(section, season='all'):
    total = []
    season_dct = {'봄': ['03', '04', '05'],
                  '여름가을': ['06', '07', '08', '09', '10'],
                  '겨울': ['11', '12', '01', '02']}
    season = unicodedata.normalize('NFC', season)  # 맥에서 한글 정규식 사용 위한 코드
    section = unicodedata.normalize('NFC', section)  # 맥에서 한글 정규식 사용 위한 코드
    if season == 'all':
        for name in search_files(search_dir):
            if section in name:
                print(f'{name} 데이터 불러오기...')
                with open(name, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    total = total + lines
    elif season != 'all':
        for m in season_dct[season]:
            m = unicodedata.normalize('NFC', m)  # 맥에서 한글 정규식 사용 위한 코드
            for name in search_files(search_dir):
                name = unicodedata.normalize('NFC', name)  # 맥에서 한글 정규식 사용 위한 코드
                if section in name and name.endswith(f'{m}_{section}.txt'):
                    print(f'{name} 데이터 불러오기...')
                    with open(name, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        total = total + lines
    with open(f'{save_dir}/{section}_{season}.txt', 'w', encoding='utf-8') as f:
        f.write(''.join(total))


def make_w2v(section, season='all'):
    if season == 'all':
        integration(section)
    elif season != 'all':
        integration(section, season)
    data = word2vec.LineSentence(f'{save_dir}/{section}_{season}.txt')
    # 500차원의 벡터, 주변 단어는 20개까지, 출현빈도 10번 미만 제외, Skip-Gram이용
    print(f'{section}_{season} word2vector-ing...')
    model = word2vec.Word2Vec(data,
                              size=500,
                              window=10,
                              hs=1,
                              min_count=10,
                              sg=1)
    model.save(f'{save_dir}/{section}_{season}.model')


def load_w2v(section, target, max_n, season='all'):
    model = word2vec.Word2Vec.load(f'{save_dir}/{section}_{season}.model')
    li = model.wv.most_similar(positive=[target], topn=max_n)
    komoran = Komoran()
    word_list = []
    dist_list = []
    for word, dist in li:
        temp = [tt[1] for tt in komoran.pos(word)]
        if len(set(temp).intersection(["NNG", "NNP"])) != 0:
            word_list.append(word)
            dist_list.append(dist)

    # 가까운 단어와 거리를 csv로 저장
    df = pd.DataFrame({'word': word_list,
                       'dist': dist_list})
    df.to_csv(f'{save_dir}/{section}_{target}_{season}.csv', encoding='ms949')

    # 그림으로 저장
    word_list.append('미세먼지')
    x = model[word_list]
    tsne = TSNE(perplexity=30, n_components=2, init='pca', n_iter=2000)
    x_tsne = tsne.fit_transform(x)
    df2 = pd.DataFrame(x_tsne, index=word_list, columns=['x', 'y'])

    plt.figure(figsize=(16, 9))
    plt.scatter(df2['x'], df2['y'])
    for word, pos in df2.iterrows():
        if word == '미세먼지':
            plt.annotate(word, pos, color='red')
        else:
            plt.annotate(word, pos, va='bottom')
    plt.savefig(f'{save_dir}/{section}_{target}_{season}.png')
    plt.close()


if __name__ == '__main__':
    data_directory = '../data'  # data folder directory

    if platform == "darwin":
        rc('font', family='AppleGothic')
        rcParams['axes.unicode_minus'] = False
    elif platform == "win32":
        font_name = font_manager.FontProperties(fname=f"{data_directory}/NanumBarunGothic.ttf").get_name()
        rc("font", family=font_name)
        rcParams['axes.unicode_minus'] = False

    search_dir = '../data/sns/total_noun'
    save_dir = '../data/sns/w2v'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    make_w2v('블로그', '봄')
    make_w2v('카페', '봄')
    for s in ['봄', '여름가을', '겨울']:
        load_w2v('블로그', '미세먼지', 100, s)
        load_w2v('카페', '미세먼지', 100, s)
