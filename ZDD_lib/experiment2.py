"""
    実験2: 性能テスト

    概要:

        ランダムに生成したマインスイーパーを解かせ, 勝率と解答速度を計測する.
    
    計測方法:

        ・盤面のサイズ: 20×20, 40×40, 60×60, 80×80
        ・爆弾総数: 10%, 20%
        ・初手はランダムで開き, そのマスがヒント数字0になるように盤面を生成

        それぞれ50回テストし

        ・勝数
        ・勝利したゲームのみでの時間 最小, 中央値, 最大
        ・全ゲームでの時間 最小, 中央値, 最大

        を計測する. ただし, 
        
        ・時間上限: 200sec
        
        であり, これを超えた場合はテストを中断し, ∞ sec として集計する. (コード内では配列の型の都合上200.0secとしている)

    備考: 

        比較対象とするソルバーを用意できていないため, ソルバーとしての優劣を客観的に判断することはできない.
        ただし,
        ・安全であると確定するマスが存在する場合, 必ず開く.
        ・存在しない場合は, 危険度を正確に計算し最も安全なマスを開く
        という特性上, 勝率については十分に高いと考えられる.
"""

from minesweeper import Minesweeper
from minesweeperSolver import MinesweeperSolver, MinesweeperResult
import numpy as np
import gc

if __name__ == "__main__":
    with open("ZDD_lib\\output\\experiment2_dataset.txt", 'r') as dataset:
        for N in [20, 40, 60, 80]:
            for R in [1, 2]:
                B = N * N * R // 10
                print(f"{N}×{N}, B={B}")
                win_times = []
                all_times = []
                for k in range(1, 51):

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

                    gc.collect()
                    solver = MinesweeperSolver(minesweeper)
                    result = solver.solve_auto_with_timelimit(time_limit=200)
                    is_win, play_time = result.is_win, result.play_time

                    all_times.append(play_time)
                    if is_win:
                        win_times.append(play_time)
                    print(k, end=' ', flush=True)
                print()
                
                win_cnt = len(win_times)
                print(win_cnt)
                if win_cnt >= 1:
                    win_times = np.array(win_times, dtype=float)
                    print(np.min(win_times), np.median(win_times), np.max(win_times))
                else:
                    print("-")
                all_times = np.array(all_times, dtype=float)
                print(np.min(all_times), np.median(all_times), np.max(all_times))

"""
実験結果:

20×20, B=40
1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 
49
0.011324099963530898 0.01621129992417991 0.023735799943096936
0.011324099963530898 0.016177500016056 0.023735799943096936
20×20, B=80
1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 
24
0.019130200031213462 0.031070650031324476 0.1547349999891594
0.0022661000257357955 0.029367999988608062 0.1547349999891594
40×40, B=160
1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 
44
0.05833840009290725 0.07118250004714355 0.17876979999709874
0.05833840009290725 0.07135320000816137 0.17876979999709874
40×40, B=320
1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 
18
0.21822560008149594 0.37163005000911653 0.7122799000935629
0.006014899932779372 0.38727349997498095 1.2525072999997064
60×60, B=360
1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 
48
0.21841189998667687 0.31427664996590465 0.5028451000107452
0.21841189998667687 0.31235474994173273 0.5028451000107452
60×60, B=720
1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 
15
1.328819000045769 1.9392109999898821 11.007734699989669
0.006714400020428002 2.0578179999720305 20.883125900058076
80×80, B=640
1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 
45
0.6645829000044614 0.7930698998970911 1.3662586999125779
0.6338090000208467 0.7952560499543324 1.3662586999125779
80×80, B=1280
1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 
5
4.781472299946472 8.714502900023945 15.110079600010067
0.020858299918472767 7.268972500052769 61.08219680003822
"""