from zdd import ZDD
import gc
from time import perf_counter

class QueenProblem:

    def solve(n: int, show: bool = False) -> int:
        """
            n×n チェス盤でのクイーン問題を解く。
            show: zddを表示するか -> 
        """
        def _to_1d(i, j):
            return i*n + j
        
        start_time = perf_counter()
        ground_set = [_to_1d(i, j) for i in range(n-1, -1, -1) for j in range(n-1, -1, -1)]
        zdd = ZDD(ground_set)
        s = zdd.empty_set()
        for j in range(n):
            s = zdd.get_node(j, s, zdd.one_terminal)
        for i in range(1, n):
            t = zdd.empty_set()
            for j in range(n):
                u = s
                E = []
                for k in range(i):
                    E.append(_to_1d(i-k-1, j))
                    # u = u.offset(_to_1d(i-k-1, j))
                for k in range(min(i, j)):
                    E.append(_to_1d(i-k-1, j-k-1))
                    # u = u.offset(_to_1d(i-k-1, j-k-1))
                for k in range(min(i, n-j-1)):
                    E.append(_to_1d(i-k-1, j+k+1))
                    # u = u.offset(_to_1d(i-k-1, j+k+1))
                # E.sort(key=lambda e: zdd.idx[e])
                # for e in E:
                #     u = u.offset(e)
                u = u.offset_s(zdd.sl.push(E))
                t = zdd.get_node(_to_1d(i, j), t, u)
            s = t
        ans = s.count()
        end_time = perf_counter()
        time = end_time - start_time
        if show:
            s.show(f"Seinor_thesis\\output\\Queen_problem{n}.html")
        return ans, time, zdd.create_cnt

if __name__ == "__main__":
    repeat = 1
    for n in range(11, 15):
        t = float("inf")
        for _ in range(repeat):
            gc.collect()
            ans, time, create_cnt = QueenProblem.solve(n, False)
            t = min(t, time)
        print(f"{n}×{n}: {ans}ans, {t}sec, {create_cnt}nodes")