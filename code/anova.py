import os
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
from matplotlib import rcParams, font_manager, rc
from sys import platform
from statsmodels.formula.api import ols
from pandas.core.groupby.generic import DataError


def gather_labels_df(n_cluster, data_dir, sex_cd='A'):
    for i in range(n_cluster):
        base_df = pd.DataFrame()
        for data in ['weather', 'gs', 'flow_age', 'card']:
            read_df = pd.read_csv(f'{data_dir}/cluster/label{i}_{data}.csv', index_col=0, parse_dates=True)

            if data == 'weather':
                read_df = read_df.loc[:, ['pm10']]

                # 미세먼지 수치 범주화
                # read_df['mise'] = 1
                # read_df['mise'].loc[read_df['pm10'] <= 50] = 0
                # read_df['mise'].loc[read_df['pm10'] > 100] = 2

                read_df['mise'] = 'bad'
                read_df.loc[read_df['pm10'] <= 50, 'mise'] = 'good'
                read_df.loc[read_df['pm10'] > 100, 'mise'] = 'dead'
                read_df = read_df.drop(columns='pm10')

            if data == 'gs':
                if sex_cd != 'A':
                    continue

            elif data == 'card':
                if sex_cd != 'A':
                    read_df = read_df[read_df['SEX_CD'] == sex_cd]
                read_df = read_df.loc[:, ['MCT_CAT_CD', 'USE_AMT', 'AGE_CD']]
                read_df = read_df[read_df['MCT_CAT_CD'].isin([20, 21, 22, 35, 40, 42, 60, 62, 70, 71, 80, 81, 92])]
                read_df = read_df.groupby([read_df.index, 'MCT_CAT_CD', 'AGE_CD']).sum().loc[:, 'USE_AMT']
                read_df = read_df.unstack().unstack()

            elif data == 'flow_age':
                if sex_cd == 'A':
                    read_df = read_df.groupby([read_df.index]).mean()
                else:
                    read_df = read_df[read_df['SEX_CD'] == sex_cd]
                    read_df = read_df.drop(columns='SEX_CD')
                read_df = read_df.mean(axis=1)
                base_df['flow'] = read_df
                continue

            base_df = pd.concat((base_df, read_df), axis=1)

        if sex_cd == 'A':
            for fn, cn in base_df.columns.values[11:]:
                try:
                    base_df = base_df.rename(columns={(fn, cn): f'{sex_cd}{int(fn)}C{int(cn)}'})
                except ValueError:
                    pass
        elif sex_cd != 'A':
            for fn, cn in base_df.columns.values[2:]:
                try:
                    base_df = base_df.rename(columns={(fn, cn): f'{sex_cd}{int(fn)}C{int(cn)}'})
                except ValueError:
                    pass

        # base_df.to_csv('base_df.csv', encoding='ms949')

        # 분산분석을 위해 데이터가 너무 적은 컬럼 제거
        base_df = base_df.loc[:, base_df.count(axis='rows') > 20]

        yield base_df


def anova(number, input_df, save_dir, f_name1):
    column_list = []
    for cn in input_df.columns[1:]:
        df_lm = ols(f'{cn} ~ C(mise)', data=input_df).fit()
        if sm.stats.anova_lm(df_lm)['PR(>F)'][0] < .05:
            f = open(f_name1, 'a', encoding='utf-8')  # log
            print(f'{number} 군집 {cn}', file=f)
            print(sm.stats.anova_lm(df_lm), file=f)
            print('========================\n', file=f)
            f.close()
            column_list.append(cn)

    df = pd.concat((input_df[column_list], input_df[['mise']]), axis=1)
    df = df.groupby('mise').mean()
    df = df.reindex(index=['good', 'bad', 'dead'])

    df.loc['bad'] = (df.loc['bad'] - df.loc['good']) / df.loc['good'] * 100
    df.loc['dead'] = (df.loc['dead'] - df.loc['good']) / df.loc['good'] * 100
    df.loc['good'] = 0

    df = df.drop(index='good')

    df.plot(kind='bar', figsize=(15, 8))
    plt.title(f'{number}군집')
    plt.legend()
    plt.savefig(f'{save_dir}/{number}군집.png')  # save fig
    plt.close()


def anova_season(number, input_df, save_dir, f_name2):
    season_dct = {'봄': pd.concat((input_df.loc['2018-04-01':'2018-05-31'], input_df['2019-02-28':])),
                  '여름가을': input_df.loc['2018-06-01':'2018-10-31'],
                  '겨울': input_df.loc['2018-11-01':'2019-02-28']}
    for (sk, s_df) in season_dct.items():
        column_list = []
        for cn in input_df.columns[1:]:
            df_lm = ols(f'{cn} ~ C(mise)', data=s_df).fit()
            try:
                a = sm.stats.anova_lm(df_lm)['PR(>F)'][0]
            except ValueError:
                continue
            if a < .05:
                f = open(f_name2, 'a', encoding='utf-8')  # log
                print(f'{number} 군집 {sk} {cn}', file=f)
                print(sm.stats.anova_lm(df_lm), file=f)
                print('========================\n', file=f)
                f.close()
                column_list.append(cn)

        try:
            df = pd.concat((input_df[column_list], input_df[['mise']]), axis=1)
            df = df.groupby('mise').mean()
            df = df.reindex(index=['good', 'bad', 'dead'])

            df.loc['bad'] = (df.loc['bad'] - df.loc['good']) / df.loc['good'] * 100
            df.loc['dead'] = (df.loc['dead'] - df.loc['good']) / df.loc['good'] * 100
            df.loc['good'] = 0

            bad_c = df.loc['bad'].abs() >= 50
            dead_c = df.loc['dead'].abs() >= 50
            t_c = list(set(bad_c[bad_c].index.values.tolist() + dead_c[dead_c].index.values.tolist()))
            if len(t_c) == 0:
                continue
            df = df.loc[:, t_c]
            # df = df.loc[:, df.loc['bad'].abs() >= 10 or df.loc['dead'].abs() >= 10]

            # df.to_csv(f'{save_dir}/categorical_{number}.csv', encoding='ms949')
            df = df.drop(index='good')

            df.plot(kind='bar', figsize=(15, 8))
            plt.title(f'{number}군집')
            plt.legend()
            plt.savefig(f'{save_dir}/{number}군집_{sk}.png')  # save fig
            plt.close()
        except DataError:
            pass


def plot_anova(data_dir):
    print('분산 분석...')
    # 폰트
    if platform == "darwin":
        rc('font', family='AppleGothic')
        rcParams['axes.unicode_minus'] = False
    elif platform == "win32":
        font_name = font_manager.FontProperties(fname="C:/Windows/Fonts/malgun.ttf").get_name()
        rc("font", family=font_name)
        rcParams['axes.unicode_minus'] = False

    n = 6
    gender = ['A', 'F', 'M']

    for g in gender:
        save_directory1 = f'{data_dir}/anova/{g}'
        if not os.path.exists(save_directory1):
            os.makedirs(save_directory1)
        save_directory2 = f'{data_dir}/anova_season/{g}'
        if not os.path.exists(save_directory2):
            os.makedirs(save_directory2)

        f_name1 = f'{save_directory1}/anova_{g}.txt'
        f_name2 = f'{save_directory2}/anova_season_{g}.txt'

        if os.path.exists(f_name1):
            os.remove(f_name1)
        if os.path.exists(f_name2):
            os.remove(f_name2)

        for idx, b_df in enumerate(gather_labels_df(n, data_dir, g)):
            anova(idx, b_df, save_directory1, f_name1)
            anova_season(idx, b_df, save_directory2, f_name2)


if __name__ == '__main__':
    data_directory = '../data'  # data folder directory
    plot_anova(data_directory)
