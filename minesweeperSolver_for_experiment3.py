from minesweeper import Minesweeper, TargetBoard
from zdd_for_Minesweeper import ZDD_for_Minesweper, ZDD_Node_for_Minesweeper
from minesweeperSolver import MinesweeperResult
from time import perf_counter
from random import randrange, choice
from collections import defaultdict
from combination import Combination
import gc
import numpy as np
from matplotlib import pyplot as plt

from timeout import *

class MinsweeperLogs:
    def __init__(self, S:int) -> None:
        self.S = S
        self.hint_cnt = 0
        self.zdd_size = np.array([0]*11)
        self.size_ratio = np.array([0]*11, dtype=float)
    
    def record(self, root:ZDD_Node_for_Minesweeper) -> None:
        """
            進行度(:= 処理したヒントマスの数 / 安全マスの総数) を11段階に分け, 各段階ごとにログを取る.
            段階ごとに, 最大値を代表値とする. 
        """
        self.hint_cnt += 1
        i = self.hint_cnt * 10 // self.S
        n = root.get_size()
        self.zdd_size[i] = max(self.zdd_size[i], n)
        self.size_ratio[i] = max(self.size_ratio[i], n/len(root.zdd.node_table))
    
    def view_graph(self):
        fig, axes = plt.subplots(2, 1)
        x = np.array(range(0, 101, 10))
        y0 = self.zdd_size
        y1 = self.size_ratio
        axes[0].plot(x, y0)
        axes[1].plot(x, y1)
        plt.show()

class MinesweeperSolver_for_experiment3:
    def __init__(self, minesweeper:Minesweeper):
        self.MS = minesweeper
        self.H = self.MS.H
        self.W = self.MS.W
        self.zdd = ZDD_for_Minesweper(self.H, self.W)
        self.root = self.zdd.unit_set()
        self.M = self.H * self.W # 非隣接マスの個数, add()での添え字振りにも使う.
        self.have_added = [False]*self.H*self.W # have_added[e] := マスeはadd()したか？
        self.neighbors = set() # 隣接マスの集合
        self.hints = set()
        self.cmb = Combination(self.H * self.W)

        S = self.H * self.W - (self.MS.B + self.MS.flag_cnt) # 安全マスの総数
        self.logs = MinsweeperLogs(S)
    
    def solve_auto_with_timelimit(self, time_limit=60):
        with time_limit_with_thread(time_limit):
            try:
                result = self.solve_auto()
            except TimeoutException:
                result = MinesweeperResult(None, 60.0, self.zdd.create_cnt)
        return result, self.logs

    def solve_auto(self) -> MinesweeperResult:
        if self.MS.target_board is None:
            si, sj = randrange(self.MS.H), randrange(self.MS.W)
            if self.MS.do_start_with_zero:
                self.MS.set_target_board(si, sj)
            else:
                self.MS.set_target_board()
            start_time = perf_counter()
            h = self.MS.open(si, sj)
            if h == -1:
                end_time = perf_counter()
                play_time = end_time - start_time
                return MinesweeperResult(False, play_time, self.zdd.create_cnt)
            self.hints.add((si, sj, h))
        else:
            start_time = perf_counter()
            self.read_playing_board()

        while not self.MS.have_finished():
            self.root, are_unneibors_safe = self.root.limit_and_are_unneighbors_safe(self.MS.B, self.M)
            assert self.root is not self.zdd.zero_terminal
            if are_unneibors_safe:
                for i, j in self.iterate_unneighbors_2d():
                    h = self.MS.open(i, j)
                    assert h is not None and h >= 0
                    self.hints.add((i, j, h))
            for i, j in self.iterate_safe_places_from_neighbor_2d():
                h = self.MS.open(i, j)
                assert h is not None and h >= 0
                self.hints.add((i, j, h))
            if self.hints:
                self.set_hints()
            else:
                i, j = self.get_the_safest_place_2d()
                h = self.MS.open(i, j)
                assert h is not None
                if h >= 0:
                    self.hints.add((i, j, h))
                    self.set_hints()
                else:
                    end_time = perf_counter()
                    play_time = end_time - start_time
                    return MinesweeperResult(False, play_time, self.zdd.create_cnt)
            self.set_flags()
        
        end_time = perf_counter()
        play_time = end_time - start_time
        return MinesweeperResult(True, play_time, self.zdd.create_cnt)
    
    def read_playing_board(self):
        """
            途中盤面から解く場合に, ソルバー内部の状態を盤面に合わせる.
            実験1 ではこの関数の時間を計測する.
        """
        for i in range(self.H):
            for j in range(self.W):
                e = self._to_1d(i, j)
                if self.MS.playing_board[i][j] == 'f':
                    if not self.have_added[e]:
                        self.add(e)
                elif self.MS.playing_board[i][j] != '.':
                    if not self.have_added[e]:
                        self.add(e)
                    for ni, nj in self._iterate_8d(i, j):
                        ne = self._to_1d(ni, nj)
                        if not self.have_added[e]:
                            self.add(ne)
                    h = self.MS.playing_board[i][j]
                    self.hints.add((i, j, int(h)))
                    self.set_hints()             

    def add(self, e):
        """
            隣接マスを台集合に追加する
        """
        self.M -= 1
        self.zdd.idx[e] = self.M
        self.have_added[e] = True
        i, j = self._to_2d(e)
        if self.MS.playing_board[i][j] == '.':
            self.neighbors.add(e)
            self.root = self.zdd.get_node(e, self.root, self.root)
    
    def set_hints(self):
        for i, j, h in self.hints:
            e = self._to_1d(i, j)
            if not self.have_added[e]:
                self.add(e)
            self.neighbors.discard(e)
            self.root = self.root.offset(e)
            E = []
            for ni, nj in self._iterate_8d(i, j):
                ne = self._to_1d(ni, nj)
                if not self.have_added[ne]:
                    self.add(ne)
                if self.MS.playing_board[ni][nj] == '.':
                    E.append(ne)
                elif self.MS.playing_board[ni][nj] == 'f':
                    h -= 1
            self.root = self.root.hint(self.zdd.sl.push(E), h)

            # hint演算を適用するたびにログを更新
            self.logs.record(self.root)
        self.hints.clear()
    
    def set_flags(self):
        E = []
        for e in self.root.flags():
            i, j = self._to_2d(e)
            assert self.MS.playing_board[i][j] != 'f'
            self.MS.flag(i, j)
            self.neighbors.discard(e)
            E.append(e)
        self.root = self.root.onset_s(self.zdd.sl.push(E))
    
    def iterate_safe_places_from_neighbor_2d(self):
        safe_places = self.neighbors - set(self.root.items())
        for e in safe_places:
            i, j = self._to_2d(e)
            yield i, j
    
    def iterate_unneighbors_1d(self):
        for i in range(self.H):
            for j in range(self.W):
                e = self._to_1d(i, j)
                if self.MS.playing_board[i][j] == '.' and not self.have_added[e]:
                    yield e
    
    def iterate_unneighbors_2d(self):
        for i in range(self.H):
            for j in range(self.W):
                e = self._to_1d(i, j)
                if self.MS.playing_board[i][j] == '.' and not self.have_added[e]:
                    yield i, j

    def get_the_safest_place_2d(self):
        """
            危険度最小のマスを1つ取る.
        """
        if self.root is self.zdd.one_terminal:
            e = choice(list(self.iterate_unneighbors_1d()))
            i, j = self._to_2d(e)
            return i, j
        dp = self.root.dp_Total()
        risk = defaultdict(int)
        for key, v in dp.items():
            e, k = key
            risk[e] += v * self.cmb.get(self.M, self.MS.B - k)
        risk_min_of_neighbors = min(risk.values())

        if self.M >= 1:
            risk_of_unneighbor = 0
            for k, v in self.root.dp_bu.items():
                risk_of_unneighbor += v * self.cmb.get(self.M - 1, self.MS.B - k - 1)
        else:
            risk_of_unneighbor = float("infinity")

        if risk_min_of_neighbors < risk_of_unneighbor:
            the_safest_places = [e for e, r in risk.items() if r == risk_min_of_neighbors]
        elif risk_min_of_neighbors > risk_of_unneighbor:
            the_safest_places = list(self.iterate_unneighbors_1d())
        else:
            the_safest_places = [e for e, r in risk.items() if r == risk_min_of_neighbors]
            the_safest_places.extend(self.iterate_unneighbors_1d())
        e = choice(the_safest_places)
        i, j = self._to_2d(e)
        return i, j

    def _to_1d(self, i, j):
        e = i * self.W + j
        return e
    
    def _to_2d(self, e):
        i, j = divmod(e, self.W)
        return i, j
    
    def _iterate_8d(self, i, j):
        D = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
        for di, dj in D:
            ni, nj = i + di, j + dj
            if 0 <= ni < self.H and 0 <= nj < self.W:
                yield ni, nj

if __name__ == "__main__":
    H, W, B = map(int, input().split())
    target = 3

    game_cnt = 0
    win_cnt = 0
    clear_time_sum = 0
    node_cnt_sum = 0

    while win_cnt < target:
        gc.collect()
        game_cnt += 1
        minesweeper = Minesweeper(H, W, B, do_start_with_zero=True)
        solver = MinesweeperSolver_for_experiment3(minesweeper)
        result, logs = solver.solve_auto_with_timelimit(time_limit=60)
        del solver, minesweeper
        result.show(do_show_details=True)
        if result.is_win:
            win_cnt += 1
            clear_time_sum += result.play_time
            node_cnt_sum += result.node_cnt
        logs.view_graph()
    
    print(f"{game_cnt}games, {clear_time_sum/target}sec, {node_cnt_sum/target}nodes")