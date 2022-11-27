# coding:utf-8
"""
よく使う関数まとめファイル
"""

# 関数のimport
import pickle
import matplotlib as plt
from sklearn.metrics import roc_curve, roc_auc_score


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


def drop_duplicates_for_id(df):
    """
    重複列を削除する関数
    ただrace_id・horse_idが異なるデータの重複データは消さないようにするために・・・
    1.一度idをcolumnに加えてdrop_duplicates()を実行する
    2. 重複データ削除後にidをcolumnから削除する
    この処理によりidが一致していて重複しているデータ(本当に二重で格納しているデータ)のみを削除できる

    params:
    df(dataframe):重複データを削除したいデータフレーム

    return:
    df(dataframe):重複行削除後のデータフレーム
    """
    df["id"] = df.index
    df = df.drop_duplicates().drop("id", axis=1).copy()  # 重複行の削除とidの列を削除
    return df

def get_swap_dict(d):
    """
    辞書のkeyとvalueを入れ替える
    """
    return {v: k for k, v in d.items()}
