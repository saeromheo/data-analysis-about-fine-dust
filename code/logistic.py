import os
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.formula.api as sm


def logistic(input_df, n, save_dir):
    df = input_df.drop(columns='labels')

    # 종로1.2.3.4가동, 창신3동 제외
    df = df.drop(6)
    df = df.drop(11)
    df = df.reset_index()
    df = df.drop(columns='index')

    iv = ' + '.join(df.columns[:-n].values)

    chk_n = 0
    for i in range(n):
        if input_df[f'label{i}'].sum() == 1:
            chk_n += 1

    fig, ax_lst = plt.subplots(n-chk_n, 1, figsize=(8, 5))  # 종로1.2.3.4가동, 창신3동
    plt.setp(ax_lst, xticks=df.index)

    # 저장 파일
    f_name = f'{save_dir}/p_summary.txt'

    # 저장 파일이 이미 존재하면 삭제
    if os.path.exists(f_name):
        os.remove(f_name)

    chk = 0
    p_df = pd.DataFrame()
    for i in range(n):
        if input_df[f'label{i}'].sum() == 1:
            chk += 1
            continue

        # 회귀분석
        f = open(f_name, 'a', encoding='utf-8')  # log
        print(f'{i}번째 군집 분석', file=f)
        result = sm.ols(formula=f'label{i} ~ {iv}', data=df).fit()
        p_df[f'label{i}'] = result.pvalues
        print(result.summary(), file=f)
        f.close()

        # plot
        ax_lst[i-chk].plot(df[f'label{i}'], label='Real')
        ax_lst[i-chk].plot(result.predict(), label='Predict')
        ax_lst[i-chk].set_title(f'Cluster {i}')
        ax_lst[i-chk].legend(loc="upper left")
    fig.tight_layout()
    p_df = p_df.drop('Intercept')
    p_df.to_csv(f'{save_dir}/p_values.csv', index=True, header=True)

    # save fig
    plt.savefig(f'{save_dir}/logistic_result.png')


if __name__ == '__main__':
    data_directory = '../data'  # data folder directory
    directory = f'{data_directory}/km'
    if not os.path.exists(directory):
        os.makedirs(directory)

    test_df = pd.read_csv('test2.csv')
    logistic(test_df, 4, directory)
