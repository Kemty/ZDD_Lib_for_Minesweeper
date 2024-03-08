"""
    実験3: ゲームプレイ中のZDD節点数の推移

    概要:

        ゲームプレイ中のZDDの節点数と生成した総節点数の遷移について調査する.

    計測方法:

        爆弾の割合10%, 20%それぞれに対し, 20×20, 40×40, 60×60の盤面を用意し,
        進行度ごとに（節点数）及び（節点数/総節点数）をプロットしたグラフを作成する.

        ただし, 進行度は10%刻みで11段階に分割し, 各区間内での最大値を代表値としてプロットした.
"""

from minesweeper import Minesweeper
from minesweeperSolver_for_experiment3 import MinesweeperSolver_for_experiment3
from matplotlib import pyplot as plt
import numpy as np

if __name__ == "__main__":
    plt.rc('font', family='MS Gothic')
    with open("ZDD_lib\\output\\experiment3_dataset.txt", 'r') as dataset:
        x = np.arange(0, 101, 10)
        for R in [1, 2]:
            fig, axes = plt.subplots(2, 3, sharey="row", sharex="all")
            axes[0, 0].set_ylabel("ZDDの節点数(個)")
            axes[1, 0].set_ylabel("ZDDの節点数/総節点数")
            for c, N in enumerate([20, 40, 60]):
                B = N * N * R // 10
                print(f"{N}×{N}, B={B}")

                axes[0, c].set_title(f"{N}×{N}")
                axes[1, c].set_xlabel("進行度(%)")

                # 盤面の読み込み
                board = [[False]*N for _ in range(N)]
                dataset.readline()
                for i in range(N):
                    row = dataset.readline()
                    for j in range(N):
                        if row[j] == '#':
                            board[i][j] = True
                        elif row[j] == 's':
                            si, sj = i, j
                minesweeper = Minesweeper(N, N, B, False)
                minesweeper.set_target_board(board=board)
                minesweeper.open(si, sj)

                solver = MinesweeperSolver_for_experiment3(minesweeper)
                result, logs = solver.solve_auto_with_timelimit(time_limit=50)
                y0 = logs.zdd_size
                y1 = logs.size_ratio
                axes[0, c].plot(x, y0)
                axes[1, c].plot(x, y1)
                result.show(True)
            plt.show()