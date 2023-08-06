import os
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.formula.api as sm
from sys import platform
from matplotlib import rcParams, font_manager, rc


def gather_labels_df(n_cluster, data_dir, sex_cd='A'):
    for i in range(n_cluster):
        base_df = pd.DataFrame()
        for data in ['weather', 'gs', 'flow_age', 'card']:
            read_df = pd.read_csv(f'{data_dir}/cluster/label{i}_{data}.csv', index_col=0, parse_dates=True)
            if data == 'weather':
                read_df = read_df.loc[:, ['pm10', 'noise', 'temp', 'humi']]
            if data == 'gs':
                read_df = read_df.loc[:, ['매출지수', '홈리빙', '취미여가활동', '임신육아']]
                if sex_cd != 'A':
                    continue
            elif data == 'card':
                if sex_cd != 'A':
                    read_df = read_df[read_df['SEX_CD'] == sex_cd]
                read_df = read_df.loc[:, ['MCT_CAT_CD', 'USE_AMT', 'AGE_CD']]
                # read_df = read_df[read_df['MCT_CAT_CD'].isin([20, 21, 22, 40, 52, 62, 70])]
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
            for fn, cn in base_df.columns.values[9:]:
                try:
                    base_df = base_df.rename(columns={(fn, cn): f'{sex_cd}{int(fn)}C{int(cn)}'})
                except ValueError:
                    pass
        elif sex_cd != 'A':
            for fn, cn in base_df.columns.values[5:]:
                try:
                    base_df = base_df.rename(columns={(fn, cn): f'{sex_cd}{int(fn)}C{int(cn)}'})
                except ValueError:
                    pass

        # 회귀분석을 위해 데이터가 너무 적은 컬럼 제거
        base_df = base_df.loc[:, base_df.count(axis='rows') > 10]

        # 표준화
        base_df = (base_df - base_df.mean()) / base_df.std()

        yield base_df


def p_select(input_df, p_value):
    # season
    season_dct = {'봄': pd.concat((input_df.loc['2018-04-01':'2018-05-31'], input_df['2019-03-01':])),
                  '여름가을': input_df.loc['2018-06-01':'2018-10-31'],
                  '겨울': input_df.loc['2018-11-01':'2019-02-28']}

    selected = []
    for i, (sk, s_df) in enumerate(season_dct.items()):
        # regression p value dataframe
        base_df = pd.DataFrame()

        s_df = s_df.loc[:, s_df.count(axis='rows') > 21]

        for df_c in s_df.columns:
            result = sm.ols(formula=f'{df_c} ~ pm10 + humi + temp + flow', data=s_df).fit()
            base_df.loc[:, df_c] = result.pvalues
        base_df = base_df.drop(columns=['pm10', 'noise', 'temp', 'humi', 'flow'])
        base_df = base_df.drop('Intercept')

        # select columns
        true_list = base_df.loc['pm10'] <= p_value
        selected.extend(base_df.loc[:, true_list].columns.values)
    return list(set(selected))


def reg_plot(number, col_list, input_df, save_dir, f_name):
    reg_list = col_list + ['pm10', 'humi', 'temp', 'flow']
    selected_df = input_df.loc[:, reg_list]

    # 회귀분석
    for cl in col_list:
        result = sm.ols(formula=f'{cl} ~ pm10 + humi + temp + flow', data=selected_df).fit()

        # write summary file
        p = result.pvalues
        r = result.rsquared
        if p.loc['pm10'] <= 0.05 and r >= 0.2:
            if p.loc['pm10'] <= p.loc['humi'] and p.loc['pm10'] <= p.loc['temp']:
                f = open(f_name, 'a', encoding='utf-8')  # log
                print(f'{number}군집 {cl}', file=f)
                print(result.summary(), file=f)
                f.close()

            # plot
            df = pd.DataFrame()
            df['pm10'] = selected_df['pm10']
            df[f'{cl}'] = selected_df[f'{cl}']
            df = df.dropna()
            df.plot(figsize=(15, 8))
            plt.title(f'{number}군집 {cl}')
            plt.legend()
            plt.savefig(f'{save_dir}/{number}군집_{cl}.png')  # save fig
            plt.close()


def reg_season_plot(number, col_list, base_df, save_dir, f_name):
    reg_list = col_list + ['pm10', 'humi', 'temp', 'flow']
    base_df = base_df.loc[:, reg_list]

    season_dct = {'봄': pd.concat((base_df.loc['2018-04-01':'2018-05-31'], base_df['2019-03-01':])),
                  '여름가을': base_df.loc['2018-06-01':'2018-10-31'],
                  '겨울': base_df.loc['2018-11-01':'2019-02-28']}

    # 회귀분석
    for cl in col_list:
        for i, (sk, s_df) in enumerate(season_dct.items()):
            result = sm.ols(formula=f'{cl} ~ pm10 + humi + temp + flow', data=s_df).fit()

            p = result.pvalues
            r = result.rsquared
            if p.loc['pm10'] <= 0.05 and r >= 0.2:
                if p.loc['pm10'] <= p.loc['humi'] and p.loc['pm10'] <= p.loc['temp']:
                    f = open(f_name, 'a', encoding='utf-8')  # log
                    print(f'{number}군집 {cl} {sk}', file=f)
                    print(result.summary(), file=f)
                    f.close()

                    # plot
                    df = pd.DataFrame()
                    df['pm10'] = s_df['pm10']
                    df[f'{cl}'] = s_df[f'{cl}']
                    df = df.dropna()
                    if sk == '봄':
                        df = df.set_index(df.index.astype('str'))
                        df.plot(figsize=(11, 9))
                        try:
                            n_vl = df.index.get_loc('2019-03-01')
                        except KeyError:
                            cnt = 2
                            while True:
                                try:
                                    if cnt >= 10:
                                        n_vl = df.index.get_loc(f'2019-03-{cnt}')
                                    else:
                                        n_vl = df.index.get_loc(f'2019-03-0{cnt}')
                                    break
                                except KeyError:
                                    cnt += 1

                        plt.axvline(x=n_vl, color='black', linestyle='--', linewidth=3)
                    else:
                        plt.figure(figsize=(11, 9))
                        plt.plot(df)
                    plt.title(f'{number}군집 {cl} {sk}')
                    plt.legend(df, loc="upper right")
                    plt.savefig(f'{save_dir}/{number}군집_{cl}_{sk}.png')  # save fig
                    plt.close()


def cluster_regression(data_dir):
    print('군집별 회귀분석...')
    # 폰트
    if platform == "darwin":
        rc('font', family='AppleGothic')
        rcParams['axes.unicode_minus'] = False
    elif platform == "win32":
        font_name = font_manager.FontProperties(fname="C:/Windows/Fonts/malgun.ttf").get_name()
        rc("font", family=font_name)
        rcParams['axes.unicode_minus'] = False

    n = 6
    gender = ['M', 'A', 'F']
    for g in gender:
        # 저장 파일
        save_directory1 = f'{data_dir}/reg/{g}'
        if not os.path.exists(save_directory1):
            os.makedirs(save_directory1)
        save_directory2 = f'{data_dir}/reg_season/{g}'
        if not os.path.exists(save_directory2):
            os.makedirs(save_directory2)

        f_name1 = f'{save_directory1}/reg_{g}.txt'
        f_name2 = f'{save_directory2}/reg_season_{g}.txt'

        # 저장 파일이 이미 존재하면 삭제
        if os.path.exists(f_name1):
            os.remove(f_name1)
        if os.path.exists(f_name2):
            os.remove(f_name2)

        for idx, b_df in enumerate(gather_labels_df(n, data_dir, g)):
            selected_list = p_select(b_df, 0.05)

            # reg plot
            reg_plot(idx, selected_list, b_df, save_directory1, f_name1)
            reg_season_plot(idx, selected_list, b_df, save_directory2, f_name2)


if __name__ == '__main__':
    data_directory = '../data'  # data folder directory
    cluster_regression(data_directory)
