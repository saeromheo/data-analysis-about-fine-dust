import itertools
import numpy as np
import pandas as pd
import seaborn as sns
import shapefile as shp
import matplotlib.pyplot as plt


def read_shape(sf):
    fields = [x[0] for x in sf.fields][1:]
    records = sf.records()
    shapes_coord = [s.points for s in sf.shapes()]
    df = pd.DataFrame(columns=fields, data=records)
    df = df.assign(coords=shapes_coord)
    return df


# Plotting multiple shapes on a full map
def plot_map_fill_multiples_ids(data_dir):
    # 파일 가져오기
    shp_path = f'{data_dir}/유동인구데이터/행정동경계파일/종로_노원_행정동.shp'
    sf = shp.Reader(shp_path, encoding='ms949')
    dong_db = pd.read_csv(f'{data_dir}/km/loc_cluster_label.csv')

    # 배경 설정
    sns.set(style='white', context='paper', color_codes=True)

    # 파일 읽기
    df = read_shape(sf)

    # 지도에서 사용할 색 팔레트 설정
    palette = itertools.cycle(sns.color_palette('colorblind'))

    # 지도 그리기
    fig, ax = plt.subplots(2, 3)

    for k in range(2):
        for j in range(3):
            # 각 labels에 속하는 동 이름 가져오기
            n = 3 * k + j

            dong_name = [h for h in dong_db.행정동 if dong_db[dong_db.행정동 == h].labels.values == n]

            # 전체 지도 그리기
            for shape in sf.shapeRecords():
                x = [i[0] for i in shape.shape.points[:]]
                y = [i[1] for i in shape.shape.points[:]]
                ax[k][j].plot(x, y, 'k')

            # 동 이름에 해당되는 구역 색 채우기
            c = next(palette)
            for dn in dong_name:
                shape_ex = sf.shape(df[df.HDONG_NM == dn].index.values[0])
                x_lon = np.zeros((len(shape_ex.points), 1))
                y_lat = np.zeros((len(shape_ex.points), 1))

                for ip in range(len(shape_ex.points)):
                    x_lon[ip] = shape_ex.points[ip][0]
                    y_lat[ip] = shape_ex.points[ip][1]

                ax[k][j].fill(x_lon, y_lat, color=c)

                # 지도 위에 동 이름 보여줄 때
                # x0 = np.mean(x_lon)
                # y0 = np.mean(y_lat)
                # ax[k][j].text(x0, y0, id, fontsize=10)

                # 지도 제목 입력
                sub = f'Cluster {n}'
                ax[k, j].text(952000, 1964500, sub, fontsize=15)

            # 축 눈금 없애기
            ax[k, j].set_yticklabels([])
            ax[k, j].set_xticklabels([])

    fig.tight_layout()
    plt.savefig(f'{data_dir}/km/km_map.png')


if __name__ == '__main__':
    data_directory = '../data'

    # 지도 그리기
    plot_map_fill_multiples_ids(data_directory)
