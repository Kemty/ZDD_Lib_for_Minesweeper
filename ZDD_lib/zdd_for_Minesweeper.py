import sys
sys.setrecursionlimit(10000)
from pyvis.network import Network
from collections import deque, defaultdict
from random import randrange
from sharedList import SharedList, SharedList_Node

class ZDD_Node_for_Minesweeper:
    def __init__(self, zdd, top=None, zero=None, one=None):
        self.zdd = zdd
        self.top = top
        self.zero = zero
        self.one = one
        if top is not None:
            self.hash = (top, zero, one).__hash__()

    def __eq__(self, other) -> bool:
        if not isinstance(other, ZDD_Node_for_Minesweeper): return False
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

    def offset(self, e):
        if self.top == e:
            return self.zero
        elif self.zdd.idx[self.top] > self.zdd.idx[e]:
            return self
        key = (self.offset, self, e)
        if key not in self.zdd._cache_table:
            self.zdd._cache_table[key] = self.zdd.get_node(self.top, self.zero.offset(e), self.one.offset(e))
        return self.zdd._cache_table[key]
    
    def offset_s(self, E:SharedList):
        if len(E) == 0 or self is self.zdd.zero_terminal or self is self.zdd.one_terminal:
            return self
        key = (self.offset_s, self, E)
        if key not in self.zdd._cache_table:
            if self.top == E.top:
                self.zdd._cache_table[key] = self.zero.offset_s(E.nxt)
            elif self.zdd.idx[self.top] > self.zdd.idx[E.top]:
                self.zdd._cache_table[key] = self.offset_s(E.nxt)
            else:
                self.zdd._cache_table[key] = self.zdd.get_node(self.top, self.zero.offset_s(E), self.one.offset_s(E))
        return self.zdd._cache_table[key]

    def onset(self, e):
        if self.zdd.idx[self.top] == self.zdd.idx[e]:
            return self.one
        elif self.zdd.idx[self.top] > self.zdd.idx[e]:
            return self.zdd.zero_terminal
        key = (self.onset, self, e)
        if key not in self.zdd._cache_table:
            self.zdd._cache_table[key] = self.zdd.get_node(self.top, self.zero.onset(e), self.one.onset(e))
        return self.zdd._cache_table[key]
    
    def onset_s(self, E:SharedList_Node):
        if len(E) == 0 or self is self.zdd.zero_terminal:
            return self
        elif self is self.zdd.one_terminal:
            return self.zdd.zero_terminal
        elif self.zdd.idx[self.top] > self.zdd.idx[E.top]:
            return self.zdd.zero_terminal
        key = (self.onset_s, self, E)
        if key not in self.zdd._cache_table:
            if self.top == E.top:
                self.zdd._cache_table[key] = self.one.onset_s(E.nxt)
            else:
                self.zdd._cache_table[key] = self.zdd.get_node(self.top, self.zero.onset_s(E), self.one.onset_s(E))
        return self.zdd._cache_table[key]
    
    def hint(self, E:SharedList, h:int):
        if len(E) < h:
            return self.zdd.zero_terminal
        elif h == 0:
            return self.offset_s(E)
        elif self is self.zdd.zero_terminal or self is self.zdd.one_terminal:
            return self.zdd.zero_terminal
        e = E.top
        key = (self.hint, self, E, h)
        if key not in self.zdd._cache_table:
            if self.zdd.idx[self.top] < self.zdd.idx[e]:
                self.zdd._cache_table[key] = self.zdd.get_node(self.top, self.zero.hint(E, h), self.one.hint(E, h))
            elif self.zdd.idx[self.top] > self.zdd.idx[e]:
                self.zdd._cache_table[key] = self.hint(E.nxt, h)
            else:
                self.zdd._cache_table[key] = self.zdd.get_node(self.top, self.zero.hint(E.nxt, h), self.one.hint(E.nxt, h-1))
        return self.zdd._cache_table[key]
    
    def flags(self) -> SharedList_Node:
        assert self is not self.zdd.zero_terminal
        if self is self.zdd.one_terminal:
            return self.zdd.sl.terminal
        key = (self.flags, self)
        if key not in self.zdd._cache_table:
            if self.zero is self.zdd.zero_terminal:
                self.zdd._cache_table[key] = self.zdd.sl.get_node(self.top, self.one.flags())
            else:
                self.zdd._cache_table[key] = self.zero.flags() & self.one.flags()
        return self.zdd._cache_table[key]
    
    def items(self) -> SharedList_Node:
        if self.top is None:
            return self.zdd.sl.terminal
        key = (self.items, self)
        if key not in self.zdd._cache_table:
            self.zdd._cache_table[key] = self.zdd.sl.get_node(self.top, self.zero.items() | self.one.items())
        return self.zdd._cache_table[key]

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
        key = (self.limit_and_are_unneighbors_safe, self, b, m)
        if key not in self.zdd._cache_table:
            p0, u0 = self.zero.limit_and_are_unneighbors_safe(b, m)
            p1, u1 = self.one.limit_and_are_unneighbors_safe(b-1, m)
            p = self.zdd.get_node(self.top, p0, p1)
            self.zdd._cache_table[key] = (p, u0 and u1)
        return self.zdd._cache_table[key]
    
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

class ZDD_for_Minesweper:
    def __init__(self, H, W):
        n = H * W
        self.idx = {}
        self.idx[None] = n # 番兵として, 終端節点のラベルの添え字は最大に設定する
        self.zero_terminal = self._create_zero_terminal()
        self.one_terminal = self._create_one_terminal()
        self.node_table = {}
        self._cache_table = {}
        self.sl = SharedList(zdd=self)
        
        self.jump_cnt = 0 # 削除規則を適用した回数
        self.share_cnt = 0 # 共有規則を適用した回数
        self.create_cnt = 0 # 新しい節点を作った回数（終端節点は除く）
    
    def _create_zero_terminal(self):
        zero_terminal = ZDD_Node_for_Minesweeper(zdd=self)
        zero_terminal.hash = randrange(10**9)
        zero_terminal.dp_bu = {} # dp_BottomUpの脱出条件
        return zero_terminal
    
    def _create_one_terminal(self):
        one_terminal = ZDD_Node_for_Minesweeper(zdd=self)
        one_terminal.hash = randrange(10**9)
        while one_terminal.hash == self.zero_terminal.hash:
            one_terminal.hash = randrange(10**9)
        one_terminal.dp_bu = {0: 1} # dp_BottomUpの脱出条件
        return one_terminal

    def get_node(self, e, zero, one):
        if one is self.zero_terminal:
            self.jump_cnt += 1
            return zero
        key = (e, zero, one)
        if key not in self.node_table:
            p = ZDD_Node_for_Minesweeper(self, e, zero, one)
            self.node_table[key] = p
            self.create_cnt += 1
        else:
            p = self.node_table[key]
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
    
    def push(self, E:list|SharedList_Node):
        """
            組合せ集合Eのみを持つzdd({E})を得る.
        """
        node = self.one_terminal
        for e in sorted(E, key=lambda e: self.idx[e], reverse=True):
            node = self.get_node(e, self.zero_terminal, node)
        return node
    
    def combinations(self, E:SharedList_Node, k:int):
        """
            E⊆Uのうち, k個のアイテムを持つような組合せ集合全体をなすzddを得る.
            例:
                E := {a, b, c} のとき 
                combinations(E, 2) = {ab, ac, bc}
        """
        if k < 0 or len(E) < k:
            return self.zero_terminal
        if k == 0:
            return self.one_terminal
        key = (self.combinations, E, k)
        if key in self._cache_table:
            return self._cache_table[key]
        node = self.get_node(E.top, self.combinations(E.nxt, k), self.combinations(E.nxt, k-1))
        self._cache_table[key] = node
        return node