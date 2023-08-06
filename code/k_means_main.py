import os
import pandas as pd
from code.pre_km import gather_data
from code.pre_km import select_cluster
from code.km import corr_select
from code.km import vif_check
from code.km import km
from code.km import logistic_check
from code.logistic import logistic
from code.map_km import plot_map_fill_multiples_ids


# 군집화
def k_means_clustering(data_dir):
    print('군집화...')
    save_dir = f'{data_dir}/km'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # 데이터 전처리
    df, df_norm, cd = gather_data(data_dir)
    corr = df_norm.corr(method='pearson')
    corr.to_csv(f'{save_dir}/corr.csv', index=True, header=True)
    select_cluster(df, save_dir)  # check number of clusters
    n_clusters = 6

    # 군집분석
    df_norm = corr_select(df_norm)  # 서로 의존적인 독립변수 제거
    vif_check(df_norm, save_dir)  # VIF 수치 확인
    df_norm = km(df_norm, n_clusters)  # k_means algorithm & labelling
    logistic_check(df_norm, save_dir, n_clusters)  # plot logistic_check

    # 회귀분석
    logistic(df_norm, n_clusters, save_dir)

    # to csv
    result_df = pd.concat((cd, df_norm['labels']), axis=1)
    result_df.to_csv(f'{save_dir}/loc_cluster_label.csv', header=True, index=False)
    result_all_df = pd.concat((cd, df_norm.iloc[:, :-n_clusters]), axis=1)
    result_all_df.to_csv(f'{save_dir}/loc_cluster_all.csv', header=True, index=False)

    # 지도 그리기
    plot_map_fill_multiples_ids(data_dir)


if __name__ == '__main__':
    data_directory = '../data'
    k_means_clustering(data_directory)
