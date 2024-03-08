import sys
sys.setrecursionlimit(10000)
from pyvis.network import Network
from collections import deque, defaultdict
from random import randrange
from deletable_sharedList import Deletable_SharedList, Deletable_SharedList_Node

class Deletable_ZDD_Node_for_Minesweeper:
    def __init__(self, zdd, top=None, zero=None, one=None):
        self.zdd = zdd
        self.top = top
        self.zero = zero
        self.one = one
        self.parents = set()
        self.parents_by_cache = set()
        self._cache_table = {}
        if top is not None:
            self.hash = (top, zero, one).__hash__()

    def __eq__(self, other) -> bool:
        if not isinstance(other, Deletable_ZDD_Node_for_Minesweeper): return False
        return self.top == other.top and self.zero is other.zero and self.one is other.one
    
    def __hash__(self) -> int:
        return self.hash
    
    def __repr__(self) -> str:
        ret = []
        stack = [(self, True)] # (現在のノード, 入りがけか？)
        current_set = []
        while stack:
            p, is_enter = stack.pop()
            if is_enter:
                if p is self.zdd.zero_terminal:
                    continue
                if p is self.zdd.one_terminal:
                    ret.append(current_set[:]) # current_setをコピーしてretに記録
                    continue
                current_set.append(p.top)
                stack.append((p.zero, True))
                stack.append((p, False))
                stack.append((p.one, True))
            elif p is not self.zdd.zero_terminal and p is not self.zdd.one_terminal:
                current_set.pop()
        return ret.__str__()
    
    def show(self, filename):
        """
            selfによるzddを図示
            filemame: html拡張子のファイル名
        """
        nodes = {self: 0}
        net = Network(directed=True)
        dq = deque()
        if self is self.zdd.zero_terminal:
            net.add_node(nodes[self], shape="box", label="⏊")
        elif self is self.zdd.one_terminal:
            net.add_node(nodes[self], shape="box", label="⏉")
        else:
            net.add_node(nodes[self], shape="circle", label=self.top.__repr__())
            dq.appendleft(self)
        while dq:
            p = dq.pop()
            if p.zero not in nodes:
                nodes[p.zero] = len(nodes)
                if p.zero is self.zdd.zero_terminal:
                    net.add_node(nodes[p.zero], shape="box", label="⏊")
                elif p.zero is self.zdd.one_terminal:
                    net.add_node(nodes[p.zero], shape="box", label="⏉")
                else:
                    net.add_node(nodes[p.zero], shape="circle", label=p.zero.top.__repr__())
                    dq.appendleft(p.zero)
            net.add_edge(nodes[p], nodes[p.zero], color="red")
            if p.one not in nodes:
                nodes[p.one] = len(nodes)
                if p.one is self.zdd.zero_terminal:
                    net.add_node(nodes[p.one], shape="box", label="⏊")
                elif p.one is self.zdd.one_terminal:
                    net.add_node(nodes[p.one], shape="box", label="⏉")
                else:
                    net.add_node(nodes[p.one], shape="circle", label=p.one.top.__repr__())
                    dq.appendleft(p.one)
            net.add_edge(nodes[p], nodes[p.one], color="blue")
        net.show(filename, notebook=False)
    
    def is_terminal(self):
        return self.top is None

    def offset(self, e, cache=None):
        if self.top == e:
            return self.zero
        elif self.zdd.idx[self.top] > self.zdd.idx[e]:
            return self
        if cache is None:
            cache = {}
        key = (self, e)
        if key not in cache:
            p = self.zdd.get_node(self.top, self.zero.offset(e, cache), self.one.offset(e, cache))
            cache[key] = p
        return cache[key]
    
    def offset_s(self, E:Deletable_SharedList_Node, cache=None):
        if len(E) == 0 or self is self.zdd.zero_terminal or self is self.zdd.one_terminal:
            return self
        if cache is None:
            cache = {}
        key = (self, E)
        if key not in cache:
            if self.top == E.top:
                p = self.zero.offset_s(E.nxt, cache)
            elif self.zdd.idx[self.top] > self.zdd.idx[E.top]:
                p = self.offset_s(E.nxt, cache)
            else:
                p = self.zdd.get_node(self.top, self.zero.offset_s(E, cache), self.one.offset_s(E, cache))
            cache[key] = p
        return cache[key]

    def onset(self, e, cache=None):
        if self.zdd.idx[self.top] == self.zdd.idx[e]:
            return self.one
        elif self.zdd.idx[self.top] > self.zdd.idx[e]:
            return self.zdd.zero_terminal
        if cache is None:
            cache = {}
        key = (self, e)
        if key not in cache:
            p = self.zdd.get_node(self.top, self.zero.onset(e, cache), self.one.onset(e, cache))
            cache[key] = p
        return cache[key]
    
    def onset_s(self, E:Deletable_SharedList_Node, cache=None):
        if len(E) == 0 or self is self.zdd.zero_terminal:
            return self
        elif self is self.zdd.one_terminal:
            return self.zdd.zero_terminal
        elif self.zdd.idx[self.top] > self.zdd.idx[E.top]:
            return self.zdd.zero_terminal
        if cache is None:
            cache = {}
        key = (self, E)
        if key not in cache:
            if self.top == E.top:
                p = self.one.onset_s(E.nxt, cache)
            else:
                p = self.zdd.get_node(self.top, self.zero.onset_s(E, cache), self.one.onset_s(E, cache))
            cache[key] = p
        return cache[key]
    
    def hint(self, E:Deletable_SharedList_Node, h:int, cache=None):
        if len(E) < h:
            return self.zdd.zero_terminal
        elif h == 0:
            return self.offset_s(E)
        elif self is self.zdd.zero_terminal or self is self.zdd.one_terminal:
            return self.zdd.zero_terminal
        if cache is None:
            cache = {}
        e = E.top
        key = (self, E, h)
        if key not in cache:
            if self.zdd.idx[self.top] < self.zdd.idx[e]:
                p = self.zdd.get_node(self.top, self.zero.hint(E, h, cache), self.one.hint(E, h, cache))
            elif self.zdd.idx[self.top] > self.zdd.idx[e]:
                p = self.hint(E.nxt, h, cache)
            else:
                p = self.zdd.get_node(self.top, self.zero.hint(E.nxt, h, cache), self.one.hint(E.nxt, h-1, cache))
            cache[key] = p
        return cache[key]
    
    def flags(self) -> Deletable_SharedList_Node:
        assert self is not self.zdd.zero_terminal
        if self is self.zdd.one_terminal:
            return self.zdd.sl.terminal
        key = self.flags
        if key not in self._cache_table:
            if self.zero is self.zdd.zero_terminal:
                p = self.zdd.sl.get_node(self.top, self.one.flags())
            else:
                p = self.zero.flags() & self.one.flags()
            self._cache_table[key] = p
            p.parents_by_cache.add((self, key))
        return self._cache_table[key]
    
    def items(self) -> Deletable_SharedList_Node:
        if self.top is None:
            return self.zdd.sl.terminal
        key = self.items
        if key not in self._cache_table:
            p = self.zdd.sl.get_node(self.top, self.zero.items() | self.one.items())
            self._cache_table[key] = p
            p.parents_by_cache.add((self, key))
        return self._cache_table[key]

    def limit_and_are_unneighbors_safe(self, b:int, m:int):
        """
            爆弾総数を超える解候補を削除する.
            また, 解候補の爆弾数が唯一であり, かつそれが爆弾総数に一致するならTrueを返す.
            → Trueなら非隣接マスが全て安全
        """
        if self is self.zdd.zero_terminal or b < 0:
            return self.zdd.zero_terminal, True
        if self is self.zdd.one_terminal:
            if m < b:
                return self.zdd.zero_terminal, True
            return self.zdd.one_terminal, b == 0
        key = (self.limit_and_are_unneighbors_safe, b, m)
        if key not in self._cache_table:
            p0, u0 = self.zero.limit_and_are_unneighbors_safe(b, m)
            p1, u1 = self.one.limit_and_are_unneighbors_safe(b-1, m)
            p = self.zdd.get_node(self.top, p0, p1)
            self._cache_table[key] = (p, u0 and u1)
            p.parents_by_cache.add((self, key))
        return self._cache_table[key]
    
    def dp_BottomUp(self) -> dict:
        """
            p.dp_bu[k] := 1-枝をk本使うp-⟙パスの総数
            を求める.
        """
        if hasattr(self, "dp_bu"): # _create_(zero/one)_terminal でdp_buが追加されていることに注意
            return self.dp_bu
        dp_bu = defaultdict(int)
        for k, v in self.zero.dp_BottomUp().items():
            dp_bu[k] += v
        for k, v in self.one.dp_BottomUp().items():
            dp_bu[k+1] += v
        self.dp_bu = dp_bu
        return dp_bu
    
    def dp_TopDown(self) -> list:
        """
            p.dp_td[k] := 1-枝をk本使うroot-pパスの総数
            を求める.
            ポロジカルソートしたlistを, 再利用のため返り値とする. (dp_Totalで使う)
        """
        assert not self.is_terminal()
        self.dp_td = {0: 1}
        tps = self._topological_sort()
        seen = set()
        for p in tps:
            if p.zero not in seen:
                seen.add(p.zero)
                p.zero.dp_td = defaultdict(int)
            if p.one not in seen:
                seen.add(p.one)
                p.one.dp_td = defaultdict(int)
            for k, v in p.dp_td.items():
                p.zero.dp_td[k] += v
                p.one.dp_td[k+1] += v
        return tps
    
    def dp_Total(self) -> dict:
        """
            dp[(e, k)] := eの節点から出る1-枝を使うroot-⟙パスであって, k本の1-枝を使うものの総数
            を求める.
        """
        assert not self.is_terminal()
        dp = defaultdict(int)
        nodes = self.dp_TopDown()
        self.dp_BottomUp()
        for p in nodes:
            for k_td, v_td in p.dp_td.items():
                for k_bu, v_bu in p.one.dp_bu.items():
                    dp[(p.top, k_td + k_bu + 1)] += v_td * v_bu
        return dp

    def _topological_sort(self) -> list:
        if self.is_terminal():
            return []
        rtps = [] # ここに節点がトポロジカル順序の逆順に入る
        visited = set()
        stack = [(self, True)] # （節点, 入りがけか？）
        while stack:
            p, is_ord = stack.pop()
            if is_ord:
                if p in visited: continue
                visited.add(p)
                stack.append((p, False))
                if not p.zero.is_terminal():
                    stack.append((p.zero, True))
                if not p.one.is_terminal():
                    stack.append((p.one, True))
            else:
                rtps.append(p)
        return rtps[::-1]
    
    def get_size(self) -> int:
        """
            selfを根とするZDDの節点数を得る.（実験3で使用）
        """
        seen = set([self])
        dq = deque([self])
        while dq:
            p = dq.pop()
            if p.is_terminal(): continue
            if p.zero not in seen:
                seen.add(p.zero)
                dq.appendleft(p.zero)
            if p.one not in seen:
                seen.add(p.one)
                dq.appendleft(p.one)
        return len(seen - set([self.zdd.zero_terminal, self.zdd.one_terminal]))
    
    def delete(self):
        # print(f"{id(self)}, yamete-")
        del self.zdd.node_table[self.zdd.idx[self.top]][(self.zero, self.one)]
        self.zero.parents.discard(self)
        self.one.parents.discard(self)
        while self._cache_table:
            key, val = self._cache_table.popitem()
            if isinstance(val, Deletable_SharedList_Node): # itemsかflagsのメモの場合
                val.parents_by_cache.discard((self, key))
            else: # limit_and_are_unneighbors_safeのメモの場合
                p = val[0]
                p.parents_by_cache.discard((self, key))
        while self.parents_by_cache:
            p, key = self.parents_by_cache.pop()
            if key in p._cache_table:
                del p._cache_table[key]
        while self.parents:
            self.parents.pop().delete()
    
    def __del__(self):
        self.zdd.delete_cnt += 1
        # print(f"{id(self)}, gue-")

class Deletable_ZDD_for_Minesweper:
    def __init__(self, H, W):
        n = H * W
        self.idx = {}
        self.idx[None] = n # 番兵として, 終端節点のラベルの添え字は最大に設定する
        self.zero_terminal = self._create_zero_terminal()
        self.one_terminal = self._create_one_terminal()
        self.node_table = [{} for _ in range(n)]
        self.sl = Deletable_SharedList(zdd=self)

        self.jump_cnt = 0 # 削除規則を適用した回数
        self.share_cnt = 0 # 共有規則を適用した回数
        self.create_cnt = 0 # 新しい節点を作った回数（終端節点は除く）
        self.delete_cnt = 0 # 新しい節点を作った回数（終端節点は除く）
    
    def _create_zero_terminal(self):
        zero_terminal = Deletable_ZDD_Node_for_Minesweeper(zdd=self)
        zero_terminal.hash = randrange(10**9)
        zero_terminal.dp_bu = {} # dp_BottomUpの脱出条件
        return zero_terminal
    
    def _create_one_terminal(self):
        one_terminal = Deletable_ZDD_Node_for_Minesweeper(zdd=self)
        one_terminal.hash = randrange(10**9)
        while one_terminal.hash == self.zero_terminal.hash:
            one_terminal.hash = randrange(10**9)
        one_terminal.dp_bu = {0: 1} # dp_BottomUpの脱出条件
        return one_terminal

    def get_node(self, e, zero, one):
        if one is self.zero_terminal:
            self.jump_cnt += 1
            return zero
        key = (zero, one)
        if key not in self.node_table[self.idx[e]]:
            p = Deletable_ZDD_Node_for_Minesweeper(self, e, zero, one)
            self.node_table[self.idx[e]][key] = p
            zero.parents.add(p)
            one.parents.add(p)
            self.create_cnt += 1
        else:
            p = self.node_table[self.idx[e]][key]
            self.share_cnt += 1
        return p
    
    def empty_set(self):
        """
            空のzdd ({}) を得る.
        """
        return self.zero_terminal
    
    def unit_set(self):
        """
            空の組合せ集合のみを持つzdd ({λ}) を得る.
        """
        return self.one_terminal

    def single_literal_set(self, e):
        """
            組合せ集合eのみを持つzdd ({e}) を得る.
        """
        assert e in self.idx
        return self.get_node(e, self.zero_terminal, self.one_terminal)
    
    def push(self, E:list|Deletable_SharedList_Node):
        """
            組合せ集合Eのみを持つzdd({E})を得る.
        """
        node = self.one_terminal
        for e in sorted(E, key=lambda e: self.idx[e], reverse=True):
            node = self.get_node(e, self.zero_terminal, node)
        return node
    
    def delete_nodes(self, e):
        self.sl.delete_nodes(e)
        for p in list(self.node_table[self.idx[e]].values()):
            p.delete()