import os
import collections
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.multiclass import OneVsRestClassifier
from sklearn.linear_model import LogisticRegression
from statsmodels.stats.outliers_influence import variance_inflation_factor


def corr_select(input_df):
    corr = input_df.corr(method='pearson')
    rm_col = []
    for i, cr in enumerate(corr.columns):
        a = corr[f'{cr}'].iloc[i+1:]
        chk = a[a >= 0.7].index.values
        for c in chk:
            rm_col.append(c)
    result_df = input_df.drop(columns=rm_col)
    return result_df


def vif_check(input_df, save_dir):
    vif = pd.DataFrame()
    vif["VIF Factor"] = [variance_inflation_factor(input_df.values, i) for i in range(input_df.shape[1])]
    vif["features"] = input_df.columns

    # log
    with open(f'{save_dir}/vif.txt', 'w', encoding='utf-8') as f:
        print(vif, file=f)


def km(input_df, n):
    # 적당한 분포의 군집을 찾을 때까지 반복
    while True:
        kmeans = KMeans(n_clusters=n,
                        algorithm='auto',
                        max_iter=1000)
        kmeans = kmeans.fit(input_df)
        labels = kmeans.predict(input_df)
        count = collections.Counter(labels)

        # 특별히 분리되는 군집을 제외한 나머지 군집이 균등한 분포인지 확인
        if sorted(count.values())[3] >= sum(count.values()) * 0.25:
            break

    result_df = input_df.copy()
    result_df['labels'] = labels

    for i in range(n):
        result_df[f'label{i}'] = result_df['labels'] == i
    result_df.iloc[:, -n:] = result_df.iloc[:, -n:].applymap(int)

    return result_df


def logistic_check(input_df, save_dir, n):
    df = input_df.iloc[:, :-n].copy()
    df = df.sort_values(by='labels')
    model_ovr = OneVsRestClassifier(LogisticRegression(solver='liblinear')).fit(df.iloc[:, :-1], df.iloc[:, -1])
    ax1 = plt.subplot(211)
    pd.DataFrame(model_ovr.decision_function(df.iloc[:, :-1])).plot(ax=ax1, legend=True)
    plt.title('Decision Function')
    ax2 = plt.subplot(212)
    pd.DataFrame(model_ovr.predict(df.iloc[:, :-1]), columns=["prediction"]).plot(marker='o', ls="", ax=ax2)
    plt.title('Predict')
    plt.tight_layout()

    # save fig
    plt.savefig(f'{save_dir}/logistic_check.png')


if __name__ == '__main__':
    data_directory = '../data'  # data folder directory
    directory = f'{data_directory}/km'
    if not os.path.exists(directory):
        os.makedirs(directory)

    test_df = pd.read_csv('test.csv')
    test_df = corr_select(test_df)
    vif_check(test_df, directory)

    test_df2 = km(test_df, 4)

    # plot logistic_check
    logistic_check(test_df2, directory, 4)

    test_df2.to_csv('test2.csv', header=True, index=False)
