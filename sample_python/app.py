# coding:utf-8

# 必要なライブラリのimport
import pandas as pd
import numpy as np


def main():
    # 適当にdfを生成
    df = pd.DataFrame(np.arange(12).reshape(3, 4))

    # 作成したdfを表示
    print(df)
    print(df)


if __name__ == '__main__':
    main()
