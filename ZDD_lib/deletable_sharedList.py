import sys
sys.setrecursionlimit(1000000)
from random import randrange

class Deletable_SharedList_Node:
    def __init__(self, sl, top=None, nxt=None):
        self.sl = sl
        self.top = top
        self.nxt = nxt
        self.parents = set()
        self.parents_by_cache = set()
        if top is not None:
            self.hash = (top, nxt).__hash__()
            self.size = nxt.size + 1
    
    def __eq__(self, other) -> bool:
        return self.top == other.top and self.nxt is other.nxt
    
    def __hash__(self) -> int:
        return self.hash
    
    def __iter__(self):
        node = self
        while node.top is not None:
            yield node.top
            node = node.nxt
    
    def __len__(self) -> int:
        return self.size
    
    def __repr__(self) -> str:
        return list(self).__repr__()
    
    def __or__(self, other):
        """
            和集合
        """
        if self is self.sl.terminal or self is other:
            return other
        elif other is self.sl.terminal:
            return self
        elif self.sl.idx[self.top] < self.sl.idx[other.top]:
            return self.sl.get_node(self.top, self.nxt | other)
        elif self.sl.idx[self.top] > self.sl.idx[other.top]:
            return self.sl.get_node(other.top, self | other.nxt)
        return self.sl.get_node(self.top, self.nxt | other.nxt)
    
    def __and__(self, other):
        """
            共通部分
        """
        if self is self.sl.terminal or other is self.sl.terminal:
            return self.sl.terminal
        elif self is other:
            return self
        elif self.sl.idx[self.top] < self.sl.idx[other.top]:
            return self.nxt & other
        elif self.sl.idx[self.top] > self.sl.idx[other.top]:
            return self & other.nxt
        return self.sl.get_node(self.top, self.nxt & other.nxt)
    
    def __sub__(self, other):
        """
            差集合
        """
        if self is self.sl.terminal or self is other:
            return self.sl.terminal
        elif other is self.sl.terminal:
            return self
        elif self.sl.idx[self.top] < self.sl.idx[other.top]:
            return self.sl.get_node(self.top, self.nxt - other)
        elif self.sl.idx[self.top] > self.sl.idx[other.top]:
            return self - other.nxt
        return self.nxt - other.nxt
    
    def delete(self):
        del self.sl.node_table[self.sl.idx[self.top]][self.nxt]
        self.nxt.parents.discard(self)
        while self.parents_by_cache:
            p, key = self.parents_by_cache.pop()
            if key in p._cache_table:
                del p._cache_table[key]
        while self.parents:
            self.parents.pop().delete()
    
    def __del__(self):
        self.sl.create_cnt -= 1

class Deletable_SharedList:
    def __init__(self, zdd):
        self.idx = zdd.idx
        self.terminal = self._create_terminal()
        self.node_table = [{} for _ in range(len(zdd.node_table))]
        
        self.create_cnt = 0
    
    def _create_terminal(self):
        terminal = Deletable_SharedList_Node(sl=self)
        terminal.hash = randrange(10**9)
        terminal.size = 0
        return terminal
    
    def push(self, array:list):
        root = self.terminal
        for e in sorted(array, key=lambda e: self.idx[e], reverse=True):
            root = self.get_node(e, root)
        return root
    
    def get_node(self, top, nxt:Deletable_SharedList_Node):
        key = nxt
        if key in self.node_table[self.idx[top]]:
            node = self.node_table[self.idx[top]][key]
        else:
            node = Deletable_SharedList_Node(self, top, nxt)
            self.node_table[self.idx[top]][key] = node
            nxt.parents.add(node)
            self.create_cnt += 1
        return node

    def delete_nodes(self, e):
        for p in list(self.node_table[self.idx[e]].values()):
            p.delete()