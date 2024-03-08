"""
    実験1: 先行研究[1] によるソルバーとの性能比較

        概要:

            マインスイーパーの途中盤面を入力とし, ZDDの構築にかかる時間を比較する.
            [1]では3つの解法が提案されているが, そのうちZDDの再帰的な処理によるものと比較する.
            [1]と問題設定を揃えるため, 爆弾総数条件は考慮しないZDDを構築するものとする.
        
        比較方法:

            ・盤面のサイズ: 20×20
            ・爆弾総数: 10%, 20%, 30% (40, 80, 120)
            ・開かれたマス: 10%, 30%, 50% (40, 120, 200)

            の盤面をそれぞれ10個ずつランダムに生成し, ZDDを構築する時間の最小, 平均, 最大を求める.
        
        注意事項:

            [1]では, 提案手法のうちフロンティア法を用いたものが最も高速であるという結果が記されている.
            しかし, 本研究ではフロンティア法に関して詳しく調査することが時間の都合上できなかったため,
            今後の課題としたい.
"""

from minesweeper import Minesweeper, TargetBoard
from minesweeperSolver import MinesweeperSolver
from zdd import ZDD
from random import sample
from time import perf_counter
import gc
import numpy as np

def solve_with_naive_ZDD(minesweeper:Minesweeper) -> int:
    H, W = minesweeper.H, minesweeper.W
    m = set() # 隣接マスの集合
    hints = [] # ヒントの集合
    for i in range(H):
        for j in range(W):
            if minesweeper.playing_board[i][j] != '.':
                X = []
                for ni, nj in minesweeper._iterate_8d(i, j):
                    if minesweeper.playing_board[ni][nj] == '.':
                        ne = minesweeper._to_1d(ni, nj)
                        m.add(ne)
                        X.append(ne)
                hints.append((X, int(minesweeper.playing_board[i][j])))
    zdd = ZDD(m)
    m = zdd.sl.push(m)
    X, c = hints[0]
    X = zdd.sl.push(X)
    root = zdd.S(m, zdd.sl.push(X), c)
    for X, c in hints[1:]:
        X = zdd.sl.push(X)
        root &= zdd.S(m, X, c)
    return len(root.zdd.node_table)

def test(minesweeper:Minesweeper):

    # [1]の手法
    gc.collect()
    start_time = perf_counter()
    their_node = solve_with_naive_ZDD(minesweeper)
    end_time = perf_counter()
    their_time = end_time - start_time

    # 本研究の手法
    gc.collect()
    start_time = perf_counter()
    our_solver = MinesweeperSolver(minesweeper)
    our_solver.read_playing_board()
    end_time = perf_counter()
    our_node = len(our_solver.zdd.node_table)
    our_time = end_time - start_time

    return their_node, their_time, our_node, our_time

if __name__ == "__main__":
    with open("ZDD_lib\\output\\experiment1_dataset.txt", 'r') as dataset:
        H, W = 20, 20
        for B in [40, 80, 120]:
            for K in [40, 120, 200]:
                their_nodes = np.array([0.0]*10)
                their_times = np.array([0.0]*10)
                our_nodes = np.array([0.0]*10)
                our_times = np.array([0.0]*10)
                for i in range(10):
                    dataset.readline()
                    minesweeper = Minesweeper(H, W, B, False)
                    minesweeper.playing_board = [list(dataset.readline()) for _ in range(H)]

                    gc.collect()
                    their_node, their_time, our_node, our_time = test(minesweeper)
                    their_nodes[i] = their_node
                    their_times[i] = their_time
                    our_nodes[i] = our_node
                    our_times[i] = our_time
                    print(i+1, end=" ", flush=True)

                print()
                print(f"B={B}, K={K}:")
                print(np.min(their_nodes), np.min(our_nodes), np.min(their_times), np.min(our_times))
                print(np.average(their_nodes), np.average(our_nodes), np.average(their_times), np.average(our_times))
                print(np.max(their_nodes), np.max(our_nodes), np.max(their_times), np.max(our_times))

"""
実験結果:

1 2 3 4 5 6 7 8 9 10 
B=40, K=40:
9389.0 463.0 0.056602499971631914 0.03436029999284074
32882.2 872.7 0.38723487000679596 0.04058023999677971
200101.0 2926.0 2.8974275000509806 0.05216829996788874
1 2 3 4 5 6 7 8 9 10 
B=40, K=120:
25146.0 754.0 0.15671079995809123 0.040510800026822835
39190.7 1526.7 0.3252269700053148 0.04681037000846118
64580.0 3173.0 0.677236899966374 0.0601487000240013
1 2 3 4 5 6 7 8 9 10 
B=40, K=200:
24497.0 360.0 0.14705710002453998 0.040476499998476356
29410.4 540.1 0.19420540001592598 0.042578790005063635
53870.0 1518.0 0.45059299998683855 0.047682000033091754
1 2 3 4 5 6 7 8 9 10 
B=80, K=40:
23708.0 954.0 0.1457442000391893 0.035288300015963614
60980.6 1582.3 0.40175255000358445 0.04043525000452064
144812.0 3263.0 1.034382900048513 0.0499462999869138
1 2 3 4 5 6 7 8 9 10 
B=80, K=120:
56919.0 3484.0 0.43434229999547824 0.055140300013590604
251534.8 10454.9 2.131887650024146 0.11200768999406137
559975.0 22862.0 5.019120300014038 0.18862749997060746
1 2 3 4 5 6 7 8 9 10 
B=80, K=200:
29945.0 502.0 0.16260820004390553 0.0433871999848634
39485.7 1230.7 0.23733170000487008 0.050664519978454337
76018.0 4231.0 0.5025703000137582 0.0717634999891743
1 2 3 4 5 6 7 8 9 10 
B=120, K=40:
147941.0 2517.0 1.026414499967359 0.0436483999947086
438699.5 5045.9 2.8270565999962853 0.05441657000919804
1469723.0 11111.0 9.459393299999647 0.07793600001605228
1 2 3 4 5 6 7 8 9 10 
B=120, K=120:
190167.0 9247.0 1.295552099996712 0.0963999999803491
868640.1 31590.2 6.872990339988609 0.3031397800077684
2441070.0 76344.0 20.687940899981186 0.6856891000061296
1 2 3 4 5 6 7 8 9 10 
B=120, K=200:
34578.0 805.0 0.17485640000086278 0.04616779997013509
39567.0 1157.8 0.21687915000366048 0.05130756999133155
46173.0 2276.0 0.25555780000286177 0.06286269996780902
"""