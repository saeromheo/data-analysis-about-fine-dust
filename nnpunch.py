import sys
import subprocess


# 필요 패키지 설치 -> 설치 불필요 시 주석 처리
def install(package):
    subprocess.call([sys.executable, "-m", "pip", "install", package])


for pk in ['pandas', 'numpy', 'matplotlib', 'scikit-learn', 'statsmodels', 'pyshp', 'seaborn']:
    install(pk)


if __name__ == '__main__':
    from code.pre_main import pre_processing
    from code.k_means_main import k_means_clustering
    from code.gather_datas import gather_clusters
    from code.reg_season_gender_age import cluster_regression
    from code.anova import plot_anova

    # 데이터 경로
    data_directory = './data'  # data folder directory

    # 데이터 전처리
    pre_processing(data_directory)
    
    # 군집화
    k_means_clustering(data_directory)

    # 군집별 데이터 종합
    gather_clusters(data_directory)

    # 군집별 회귀분석
    cluster_regression(data_directory)

    # 분산 분석
    plot_anova(data_directory)
