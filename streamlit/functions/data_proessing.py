# coding:utf-8
"""
よく使う関数まとめファイル
"""

import pickle


def load_pickle(file_path, file_name):
    """
    pickleをloadする関数
    """
    with open("{}/{}".format(file_path, file_name), 'rb') as f:
        return pickle.load(f)


def save_pickle(file_path, file_name, var_name):
    """
    pickleをloadする関数
    """
    with open("{}/{}".format(file_path, file_name), 'wb') as f:
        pickle.dump(var_name, f)


def train_test_split(pd_results, test_size):
    """
    訓練データとテストデータを分割する関数
    データの順番は変更しない(日付を紐つけしているデータ等に使用)
    params:
    pd_results(DataFrame):データを分割する元データ
    test_size(float):テストデータのサイズ(min:0.1〜max:1.0)
    return:
    分割したテストデータと訓練データを返す
    train_data:訓練データ
    test＿data：テストデータ
    """
    sorted_id_list = pd_results.sort_values("date").index.unique()

    train_id_list = sorted_id_list[:round(len(sorted_id_list) * (1-test_size))]
    test_id_list = sorted_id_list[round(len(sorted_id_list) * (1-test_size)):]

    train = pd_results.loc[train_id_list]
    # X_train = train.drop(["date", "rank"], axis=1)
    # y_train = train["rank"]

    test = pd_results.loc[test_id_list]
    # X_test = test.drop(["date", "rank"], axis=1)
    # y_test = test["rank"]

    print(f"元データの数{len(pd_results)}")
    print(f"訓練データの数{len(train)}")
    print(f"テストデータの数{len(test)}")

    return train, test


def roc_graph_plot(y_label, y_pred):
    """
    roc曲線をプロットする
    """
    fpr, tpr, thresholds = roc_curve(y_label, y_pred)
    plt.plot(fpr, tpr, marker='o')
    plt.xlabel("False positive rate")
    plt.ylabel("True positive rate")
    plt.grid
    plt.show()
    plt.close()
