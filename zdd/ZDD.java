package zdd;

import java.util.Random;
import java.util.HashMap;
import java.util.Iterator;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Comparator;
import java.math.BigInteger;

public class ZDD {
    int[] items;
    int[] idx;
    int n;
    ZDD_Node zero_terminal;
    ZDD_Node one_terminal;
    OrderedShareList orderedShareList;
    HashMap<ZDD_Node, ZDD_Node> node_table = new HashMap<>();
    HashMap<Pair<ZDD_Node, Integer>, ZDD_Node> cache_OFFSET = new HashMap<>(0);
    HashMap<Pair<ZDD_Node, int[]>, ZDD_Node> cache_OFFSET_S_BY_ARRAY = new HashMap<>(0);
    HashMap<Pair<ZDD_Node, BigInteger>, ZDD_Node> cache_OFFSET_S_BY_BIGINTEGER = new HashMap<>(0);
    HashMap<Pair<ZDD_Node, OrderedShareList.ListNode>, ZDD_Node> cache_OFFSET_S_BY_ORDEREDSHARELIST = new HashMap<>(0);
    HashMap<Pair<ZDD_Node, ZDD_Node>, ZDD_Node> cache_OFFSET_S_BY_ZDD_NODE = new HashMap<>(0);
    HashMap<Pair<ZDD_Node, Integer>, ZDD_Node> cache_ONSET = new HashMap<>(0);
    HashMap<Pair<ZDD_Node, OrderedShareList.ListNode>, ZDD_Node> cache_ONSET_S_BY_ORDEREDSHARELIST = new HashMap<>(0);
    HashMap<Pair<ZDD_Node, ZDD_Node>, ZDD_Node> cache_OR = new HashMap<>(0);
    HashMap<Pair<ZDD_Node, ZDD_Node>, ZDD_Node> cache_AND = new HashMap<>(0);
    HashMap<Pair<ZDD_Node, ZDD_Node>, ZDD_Node> cache_SETMINUS = new HashMap<>(0);
    HashMap<ZDD_Node, Integer> cache_COUNT = new HashMap<>(0);
    // HashMap<ZDD_Node, ZDD_Node> cache_REM = new HashMap<>(0);
    // HashMap<Pair<ZDD_Node, OrderedShareList.ListNode>, ZDD_Node> cache_ADD = new HashMap<>(0);
    // HashMap<Pair<ZDD_Node, OrderedShareList.ListNode>, ZDD_Node> cache_SWAP = new HashMap<>(0);
    // HashMap<Pair<ZDD_Node, ZDD_Node>, ZDD_Node> cache_DELTA = new HashMap<>(0);
    // HashMap<Tuple3<ZDD_Node, ZDD_Node, Integer>, ZDD_Node> cache_RESTRICT = new HashMap<>(0);
    // HashMap<Tuple3<ZDD_Node, ZDD_Node, Integer>, ZDD_Node> cache_DIST = new HashMap<>(0);
    // HashMap<Pair<ZDD_Node, Integer>, ZDD_Node> cache_GET_SIZE_OF = new HashMap<>(0);
    // HashMap<Pair<ZDD_Node, OrderedShareList.ListNode>, Boolean> cache_ISCONTAINS = new HashMap<>(0);

    public class ZDD_Node {
        // public class ZDD_Node implements Comparable<ZDD_Node>{
        int top;
        ZDD_Node zero;
        ZDD_Node one;
        int hash;

        // 葉を作る用
        public ZDD_Node(int hash) {
            this.top = n;
            this.hash = hash;
        }

        public ZDD_Node(int top, ZDD_Node zero, ZDD_Node one) {
            this.top = top;
            this.zero = zero;
            this.one = one;
            // ハッシュ値を計算（ハッシュ関数は適当）
            long x = top, y = zero.hashCode(), z = one.hashCode();
            this.hash = (int) ((((x + 10) & Integer.MAX_VALUE) * y % 3483643) * z % 1147483637);
        }

        // @Override
        // public int compareTo(ZDD_Node that) {
        // if(this.top == n && that.top == n) {
        // return 0;
        // } else if(this.top == n) {
        // return 1;
        // } else if(that.top == n) {
        // return -1;
        // } else {
        // int[] thisArray = {this.top, this.zero.top, this.one.top};
        // int[] thatArray = {that.top, that.zero.top, that.one.top};
        // return Arrays.compare(thisArray, thatArray);
        // }
        // }

        public boolean equals(Object that) {
            if (!(that instanceof ZDD_Node)) {
                return false;
            }
            ZDD_Node thatNode = (ZDD_Node) that;
            return this.top == thatNode.top && this.zero == thatNode.zero && this.one == thatNode.one;
        }

        public int hashCode() {
            return this.hash;
        }

        public boolean isTerminal() {
            return this.top == n;
        }

        public ZDD_Node offset(int e) {
            if (idx[this.top] > idx[e]) {
                return this;
            } else if (idx[this.top] == idx[e]) {
                return this.zero;
            }
            ZDD_Node node;
            Pair<ZDD_Node, Integer> key = new Pair<ZDD_Node, Integer>(this, e);
            if (cache_OFFSET.containsKey(key)) {
                node = cache_OFFSET.get(key);
            } else {
                node = getNode(this.top, this.zero.offset(e), this.one.offset(e));
                cache_OFFSET.put(key, node);
            }
            return node;
        }

        public ZDD_Node offset_s(int[] setE) { // ソート済みのarrayを渡す。
            if (this == zero_terminal || this == one_terminal || setE.length == 0) {
                return this;
            }
            int min_e = setE[0];
            ZDD_Node node;
            Pair<ZDD_Node, int[]> key = new Pair<ZDD_Node, int[]>(this, setE);
            if (cache_OFFSET_S_BY_ARRAY.containsKey(key)) {
                node = cache_OFFSET_S_BY_ARRAY.get(key);
            } else {
                if (idx[this.top] > idx[min_e]) {
                    node = this.offset_s(popFirstFromArray(setE));
                } else if (idx[this.top] == idx[min_e]) {
                    node = this.zero.offset_s(popFirstFromArray(setE));
                } else {
                    node = getNode(this.top, this.zero.offset_s(setE), this.one.offset_s(setE));
                }
                cache_OFFSET_S_BY_ARRAY.put(key, node);
            }
            return node;
        }

        public ZDD_Node offset_s(BigInteger setE) {
            if (this == zero_terminal || this == one_terminal || setE.equals(BigInteger.ZERO)) {
                return this;
            }
            int lsb = setE.getLowestSetBit();
            ZDD_Node node;
            Pair<ZDD_Node, BigInteger> key = new Pair<ZDD_Node, BigInteger>(this, setE);
            if (cache_OFFSET_S_BY_BIGINTEGER.containsKey(key)) {
                node = cache_OFFSET_S_BY_BIGINTEGER.get(key);
            } else {
                if (idx[this.top] > lsb) {
                    node = this.offset_s(setE.clearBit(lsb));
                } else if (idx[this.top] == lsb) {
                    node = this.zero.offset_s(setE.clearBit(lsb));
                } else {
                    node = getNode(this.top, this.zero.offset_s(setE), this.one.offset_s(setE));
                }
                cache_OFFSET_S_BY_BIGINTEGER.put(key, node);
            }
            return node;
        }

        public ZDD_Node offset_s(OrderedShareList.ListNode setE) {
            if (this == zero_terminal || this == one_terminal || setE.isEmpty()) {
                return this;
            }
            ZDD_Node node;
            Pair<ZDD_Node, OrderedShareList.ListNode> key = new Pair<ZDD_Node, OrderedShareList.ListNode>(this, setE);
            if (cache_OFFSET_S_BY_ORDEREDSHARELIST.containsKey(key)) {
                node = cache_OFFSET_S_BY_ORDEREDSHARELIST.get(key);
            } else {
                if (idx[this.top] > idx[setE.top]) {
                    node = this.offset_s(setE.nxt);
                } else if (idx[this.top] == idx[setE.top]) {
                    node = this.zero.offset_s(setE.nxt);
                } else {
                    node = getNode(this.top, this.zero.offset_s(setE), this.one.offset_s(setE));
                }
                cache_OFFSET_S_BY_ORDEREDSHARELIST.put(key, node);
            }
            return node;
        }

        public ZDD_Node offset_s(ZDD_Node setE) {
            if (this == zero_terminal || this == one_terminal || setE == one_terminal) {
                return this;
            }
            ZDD_Node node;
            Pair<ZDD_Node, ZDD_Node> key = new Pair<ZDD_Node, ZDD_Node>(this, setE);
            if (cache_OFFSET_S_BY_ZDD_NODE.containsKey(key)) {
                node = cache_OFFSET_S_BY_ZDD_NODE.get(key);
            } else {
                if (idx[this.top] > idx[setE.top]) {
                    node = this.offset_s(setE.one);
                } else if (idx[this.top] == idx[setE.top]) {
                    node = this.zero.offset_s(setE.one);
                } else {
                    node = getNode(this.top, this.zero.offset_s(setE), this.one.offset_s(setE));
                }
                cache_OFFSET_S_BY_ZDD_NODE.put(key, node);
            }
            return node;
        }

        public ZDD_Node onset(int e) {
            if (idx[this.top] > idx[e]) {
                return zero_terminal;
            } else if (idx[this.top] == idx[e]) {
                return this.one;
            }
            ZDD_Node node;
            Pair<ZDD_Node, Integer> key = new Pair<>(this, e);
            if (cache_ONSET.containsKey(key)) {
                node = cache_ONSET.get(key);
            } else {
                node = getNode(this.top, this.zero.onset(e), this.one.onset(e));
                cache_ONSET.put(key, node);
            }
            return node;
        }

        public ZDD_Node onset_s(OrderedShareList.ListNode setE) {
            if (setE.isEmpty()) {
                return this;
            } else if (idx[this.top] > idx[setE.top]) {
                return zero_terminal;
            }
            ZDD_Node node;
            Pair<ZDD_Node, OrderedShareList.ListNode> key = new Pair<>(this, setE);
            if (cache_OFFSET_S_BY_ORDEREDSHARELIST.containsKey(key)) {
                node = cache_ONSET_S_BY_ORDEREDSHARELIST.get(key);
            } else {
                if (idx[this.top] == idx[setE.top]) {
                    node = this.one.onset_s(setE.next());
                } else {
                    node = getNode(this.top, this.zero.onset_s(setE), this.one.onset_s(setE));
                }
                cache_ONSET_S_BY_ORDEREDSHARELIST.put(key, node);
            }
            return node;
        }

        public int count() {
            if (this == zero_terminal) {
                return 0;
            } else if (this == one_terminal) {
                return 1;
            }
            int cnt;
            ZDD_Node key = this;
            if (cache_COUNT.containsKey(key)) {
                cnt = cache_COUNT.get(key);
            } else {
                cnt = this.zero.count() + this.one.count();
                cache_COUNT.put(key, cnt);
            }
            return cnt;
        }

        public ZDD_Node or(ZDD_Node that) {
            if (this == zero_terminal || this == that) {
                return that;
            }
            if (that == zero_terminal) {
                return this;
            }
            Pair<ZDD_Node, ZDD_Node> key = new Pair<>(this, that);
            ZDD_Node node;
            if (cache_OR.containsKey(key)) {
                node = cache_OR.get(key);
            } else {
                if (idx[this.top] < idx[that.top]) {
                    node = getNode(this.top, this.zero.or(that), this.one);
                } else if (idx[this.top] > idx[that.top]) {
                    node = getNode(that.top, this.or(that.zero), that.one);
                } else {
                    node = getNode(this.top, this.zero.or(that.zero), this.one.or(that.one));
                }
                cache_OR.put(key, node);
            }
            return node;
        }

        public ZDD_Node and(ZDD_Node that) {
            if(this == zero_terminal || that == zero_terminal) {
                return zero_terminal;
            }
            if(this == that) {
                return this;
            }
            Pair<ZDD_Node, ZDD_Node> key = new Pair<>(this, that);
            ZDD_Node node;
            if(cache_AND.containsKey(key)) {
                node = cache_AND.get(key);
            } else {
                if(idx[this.top] < idx[that.top]) {
                    node = this.zero.and(that);
                } else if(idx[this.top] > idx[that.top]) {
                    node = this.and(that.zero);
                } else {
                    node = getNode(this.top, this.zero.and(that.zero), this.one.and(that.one));
                }
                cache_AND.put(key, node);
            }
            return node;

         }

        public ZDD_Node setminus(ZDD_Node that) {
            if(that == zero_terminal) {
                return this;
            }
            if(this == zero_terminal || this == that) {
                return zero_terminal;
            }
            Pair<ZDD_Node, ZDD_Node> key = new Pair<>(this, that);
            ZDD_Node node;
            if(cache_SETMINUS.containsKey(key)) {
                node = cache_SETMINUS.get(key);
            } else {
                if(idx[this.top] < idx[that.top]) {
                    node = getNode(this.top, this.zero.setminus(that), this.one);
                } else if(idx[this.top] > idx[that.top]) {
                    node = this.setminus(that.zero);
                } else {
                    node = getNode(this.top, this.zero.setminus(that.zero), this.one.setminus(that.one));
                }
                cache_SETMINUS.put(key, node);
            }
            return node;
        }

        // public ZDD_Node rem() {
        //     if (this == zero_terminal || this == one_terminal) {
        //         return zero_terminal;
        //     }
        //     ZDD_Node key = this;
        //     ZDD_Node node;
        //     if (cache_REM.containsKey(key)) {
        //         node = cache_REM.get(key);
        //     } else {
        //         node = getNode(this.top, this.zero.rem().or(this.one), this.one.rem());
        //         cache_REM.put(key, node);
        //     }
        //     return node;
        // }

        // public ZDD_Node add(OrderedShareList.ListNode setE) {
        //     if (this == zero_terminal || setE.size == 0) {
        //         return zero_terminal;
        //     }
        //     Pair<ZDD_Node, OrderedShareList.ListNode> key = new Pair<>(this, setE);
        //     ZDD_Node node;
        //     if (cache_ADD.containsKey(key)) {
        //         node = cache_ADD.get(key);
        //     } else {
        //         if (idx[this.top] < idx[setE.top]) {
        //             node = getNode(this.top, this.zero.add(setE), this.one.add(setE));
        //         } else if (idx[this.top] > idx[setE.top]) {
        //             node = getNode(setE.top, this.add(setE.nxt), this);
        //         } else {
        //             node = getNode(this.top, this.zero.add(setE.nxt), this.one.add(setE.nxt).or(this.zero));
        //         }
        //         cache_ADD.put(key, node);
        //     }
        //     return node;
        // }

        // public ZDD_Node swap(OrderedShareList.ListNode setE) {
        //     if (this == zero_terminal || this == one_terminal || setE.size == 0) {
        //         return zero_terminal;
        //     }
        //     Pair<ZDD_Node, OrderedShareList.ListNode> key = new Pair<>(this, setE);
        //     ZDD_Node node;
        //     if (cache_SWAP.containsKey(key)) {
        //         node = cache_SWAP.get(key);
        //     } else {
        //         if (idx[this.top] < idx[setE.top]) {
        //             node = getNode(this.top, this.zero.swap(setE).or(this.one.add(setE)), this.one.swap(setE));
        //         } else if (idx[this.top] > idx[setE.top]) {
        //             node = getNode(setE.top, this.swap(setE.nxt), this.rem());
        //         } else {
        //             node = getNode(this.top, this.zero.swap(setE.nxt).or(this.one.add(setE.nxt)),
        //                     this.one.swap(setE.nxt).or(this.zero.rem()));
        //         }
        //         cache_SWAP.put(key, node);
        //     }
        //     return node;
        // }

        // public ZDD_Node delta(ZDD_Node that) {
        //     if (this == zero_terminal || that == zero_terminal) {
        //         return zero_terminal;
        //     }
        //     if (this == one_terminal) {
        //         return that;
        //     }
        //     if (that == one_terminal) {
        //         return this;
        //     }
        //     Pair<ZDD_Node, ZDD_Node> key = new Pair<>(this, that);
        //     ZDD_Node node;
        //     if (cache_DELTA.containsKey(key)) {
        //         node = cache_DELTA.get(key);
        //     } else if (idx[this.top] < idx[that.top]) {
        //         node = getNode(this.top, this.zero.delta(that), this.one.delta(that));
        //     } else if (idx[this.top] > idx[that.top]) {
        //         node = getNode(that.top, this.delta(that.zero), this.delta(that.one));
        //     } else {
        //         node = getNode(this.top, this.zero.delta(that.zero).or(this.one.delta(that.one)),
        //                 this.zero.delta(that.one).or(this.one.delta(that.zero)));
        //     }
        //     cache_DELTA.put(key, node);
        //     return node;
        // }

        // public ZDD_Node restrict(ZDD_Node that, int k) {
        //     if (this == zero_terminal || that == zero_terminal || k < 0 || k > n - idx[this.top]) {
        //         return zero_terminal;
        //     }
        //     if (this == one_terminal && that == one_terminal) {
        //         return one_terminal;
        //     }
        //     Tuple3<ZDD_Node, ZDD_Node, Integer> key = new Tuple3<>(this, that, k);
        //     ZDD_Node node;
        //     if (cache_RESTRICT.containsKey(key)) {
        //         node = cache_RESTRICT.get(key);
        //     } else {
        //         if (idx[this.top] < idx[that.top]) {
        //             node = getNode(this.top, this.zero.restrict(that, k), this.one.restrict(that, k - 1));
        //         } else if (idx[this.top] > idx[that.top]) {
        //             node = this.restrict(that.zero, k);
        //         } else {
        //             node = getNode(this.top, this.zero.restrict(that.zero, k),
        //                                      this.one.restrict(that.zero, k - 1).or(this.one.restrict(that.one, k)));
        //         }
        //         cache_RESTRICT.put(key, node);
        //     }
        //     return node;
        // }

        // public ZDD_Node dist(ZDD_Node that, int k) {
        //     if (this == zero_terminal || that == zero_terminal || k < 0) {
        //         return zero_terminal;
        //     }
        //     if (this == one_terminal && that == one_terminal) {
        //         if (k == 0) {
        //             return one_terminal;
        //         } else {
        //             return zero_terminal;
        //         }
        //     }
        //     Tuple3<ZDD_Node, ZDD_Node, Integer> key = new Tuple3<>(this, that, k);
        //     ZDD_Node node;
        //     if (cache_DIST.containsKey(key)) {
        //         node = cache_DIST.get(key);
        //     } else {
        //         if (idx[this.top] < idx[that.top]) {
        //             node = getNode(this.top, this.zero.dist(that, k), this.one.dist(that, k - 1));
        //         } else if (idx[this.top] > idx[that.top]) {
        //             node = this.dist(that.zero, k).or(this.dist(that.one, k - 1));
        //         } else {
        //             node = getNode(this.top, this.zero.dist(that.zero, k).or(this.zero.dist(that.one, k - 1)),
        //                                      this.one.dist(that.zero, k - 1).or(this.one.dist(that.one, k)));

        //         }
        //         cache_DIST.put(key, node);
        //     }
        //     return node;
        // }

        // public ZDD_Node get_size_of(int k) {
        //     if (k < 0 || this == zero_terminal) {
        //         return zero_terminal;
        //     }
        //     if (this == one_terminal) {
        //         if (k == 0) {
        //             return one_terminal;
        //         } else {
        //             return zero_terminal;
        //         }
        //     }
        //     Pair<ZDD_Node, Integer> key = new Pair<>(this, k);
        //     ZDD_Node node;
        //     if (cache_GET_SIZE_OF.containsKey(key)) {
        //         node = cache_GET_SIZE_OF.get(key);
        //     } else {
        //         node = getNode(this.top, this.zero.get_size_of(k), this.one.get_size_of(k - 1));
        //         cache_GET_SIZE_OF.put(key, node);
        //     }
        //     return node;
        // }

        // public boolean isContains(OrderedShareList.ListNode setE) {
        //     if (setE.isEmpty() || this == zero_terminal || this == one_terminal) {
        //         return setE.isEmpty() && this == one_terminal;
        //     }
        //     if (idx[this.top] > idx[setE.top]) {
        //         return false;
        //     }
        //     Pair<ZDD_Node, OrderedShareList.ListNode> key = new Pair<>(this, setE);
        //     boolean bool;
        //     if (cache_ISCONTAINS.containsKey(key)) {
        //         bool = cache_ISCONTAINS.get(key);
        //     } else {
        //         if (idx[this.top] < idx[setE.top]) {
        //             bool = this.zero.isContains(setE);
        //         } else {
        //             bool = this.one.isContains(setE.nxt);
        //         }
        //         cache_ISCONTAINS.put(key, bool);
        //     }
        //     return bool;
        // }
    }

    public class OrderedShareList {
        ListNode terminal;
        HashMap<ListNode, ListNode> node_table = new HashMap<>();
        HashMap<Pair<ListNode, ListNode>, ListNode> cache_MERGE = new HashMap<>();
        HashMap<Pair<ListNode, ListNode>, ListNode> cache_SETMINUS = new HashMap<>();

        public class ListNode implements Iterable<ListNode>, Iterator<ListNode> {
            int top;
            ListNode nxt;
            int size;
            int hash;
            private ListNode iteraingNode;

            private ListNode(int hash) {
                this.top = n;
                this.size = 0;
                this.nxt = null;
                this.hash = hash;
                iteraingNode = this;
            }
            
            private ListNode(int top, ListNode nxt) {
                this.top = top;
                this.nxt = nxt;
                this.size = nxt.size + 1;
                this.hash = Long.hashCode(((long) top << 32) | nxt.hash);
                iteraingNode = this;
            }

            public boolean equals(Object that) {
                if (!(that instanceof ListNode)) {
                    return false;
                }
                ListNode thatNode = (ListNode) that;
                return this.top == thatNode.top && this.nxt == thatNode.nxt;
            }

            public int hashCode() {
                return this.hash;
            }

            public boolean hasNext() {
                if(iteraingNode.nxt == null) {
                    iteraingNode = this;
                    return false;
                } else {
                    return true;
                }
            }

            public ListNode next() {
                ListNode ret = this.iteraingNode;
                iteraingNode = iteraingNode.nxt;
                return ret;
            }

            public Iterator<ListNode> iterator() {
                this.iteraingNode = this;
                return this;
            }

            public boolean isEmpty() {
                return this.size == 0;
            }

            public ArrayList<Integer> toArray() {
                ArrayList<Integer> arrayList = new ArrayList<>();
                for (ListNode node: this) {
                    arrayList.add(node.top);
                }
                return arrayList;
            }

            public ListNode merge(ListNode that) {
                if (this == that || that == terminal) {
                    return this;
                } else if (this == terminal) {
                    return that;
                }
                Pair<ListNode, ListNode> key = new Pair<ListNode, ListNode>(this, that);
                ListNode node;
                if (cache_MERGE.containsKey(key)) {
                    node = cache_MERGE.get(key);
                } else {
                    if (idx[this.top] < idx[that.top]) {
                        node = getNode(this.top, this.nxt.merge(that));
                    } else if (idx[this.top] > idx[that.top]) {
                        node = getNode(that.top, this.merge(that.nxt));
                    } else {
                        node = getNode(this.top, this.nxt.merge(that.nxt));
                    }
                    cache_MERGE.put(key, node);
                }
                return node;
            }

            public ListNode setminus(ListNode that) {
                if (that == terminal) {
                    return this;
                } else if (this == terminal) {
                    return terminal;
                }
                Pair<ListNode, ListNode> key = new Pair<>(this, that);
                ListNode node;
                if (cache_SETMINUS.containsKey(key)) {
                    node = cache_SETMINUS.get(key);
                } else {
                    if (idx[this.top] < idx[that.top]) {
                        node = getNode(this.top, this.nxt.setminus(that));
                    } else if (idx[this.top] < idx[that.top]) {
                        node = getNode(this.top, this.setminus(that.nxt));
                    } else {
                        node = this.nxt.setminus(that.nxt);
                    }
                    cache_SETMINUS.put(key, node);
                }
                return node;
            }
        }

        public OrderedShareList() {
            Random r = new Random();
            this.terminal = new ListNode(r.nextInt());
        }

        public ListNode push(ArrayList<Integer> arrayList) {
            ArrayList<Integer> copyedArrayList = (ArrayList<Integer>) arrayList.clone();
            sortByIndex(copyedArrayList);
            ListNode root = this.terminal;
            for (int i = copyedArrayList.size() - 1; i >= 0; --i) {
                root = getNode(copyedArrayList.get(i), root);
            }
            return root;
        }

        public ListNode getNode(int top, ListNode nxt) {
            ListNode node = new ListNode(top, nxt);
            if (this.node_table.containsKey(node)) {
                node = node_table.get(node);
            } else {
                node_table.put(node, node);
            }
            return node;
        }
    }

    public ZDD() {} // 継承用のデフォルトコンストラクタ（使わない）

    public ZDD(int n) {
        // setIndex(e, i) で後から番号を振る
        this.n = n;
        this.items = new int[n + 1];
        Arrays.fill(this.items, -1);
        this.items[n] = n; // 葉のtopにあたる番兵
        this.idx = new int[n + 1];
        Arrays.fill(idx, -1);
        this.idx[n] = n;
        createZeroTerminal();
        createOneTerminal();
        this.orderedShareList = new OrderedShareList();
    }

    public ZDD(int[] permutation) {
        this.n = permutation.length;
        this.items = Arrays.copyOf(permutation, this.n + 1);
        this.items[this.n] = this.n; // 葉のtopにあたる番兵
        this.idx = new int[this.n + 1];
        for (int i = 0; i < this.n + 1; ++i) {
            this.idx[this.items[i]] = i;
        }
        createZeroTerminal();
        createOneTerminal();
        this.orderedShareList = new OrderedShareList();
    }

    void createZeroTerminal() {
        Random r = new Random();
        int hash = r.nextInt(10000);
        this.zero_terminal = new ZDD_Node(hash);
    }

    void createOneTerminal() {
        Random r = new Random();
        int hash;
        do {
            hash = r.nextInt(10000);
        } while (hash == zero_terminal.hash);
        this.one_terminal = new ZDD_Node(hash);
    }

    public void setIndex(int e, int i) {
        items[i] = e;
        idx[e] = i;
    }

    public boolean haveSetIndex(int e) {
        return idx[e] != -1;
    }

    public ZDD_Node getNode(int top, ZDD_Node zero, ZDD_Node one) {
        if (one == zero_terminal) {
            return zero;
        }
        ZDD_Node node = new ZDD_Node(top, zero, one);
        if (node_table.containsKey(node)) {
            node = node_table.get(node);
        } else {
            node_table.put(node, node);
        }
        return node;
    }

    public ZDD_Node emptySet() {
        return zero_terminal;
    }

    public ZDD_Node unitSet() {
        return one_terminal;
    }

    public int createdNodeCount() {
        return node_table.size();
    }

    public void sortByIndex(ArrayList<Integer> arrayList) {
        ItemComparator c = new ItemComparator();
        arrayList.sort(c);
    }

    private class ItemComparator implements Comparator<Integer> {
        public int compare(Integer x, Integer y) {
            if (idx[x] < idx[y]) {
                return -1;
            } else if (idx[x] == idx[y]) {
                return 0;
            } else {
                return 1;
            }
        }
    }

    public int[] make_sortedArray(ArrayList<Integer> arrayList) {
        ArrayList<Integer> copyedArrayList = (ArrayList<Integer>) arrayList.clone();
        sortByIndex(copyedArrayList);
        return castToArray(copyedArrayList);
    }

    public int[] castToArray(ArrayList<Integer> arrayList) {
        int[] array = new int[arrayList.size()];
        for (int i = 0; i < arrayList.size(); ++i) {
            array[i] = arrayList.get(i);
        }
        return array;
    }

    public int[] popFirstFromArray(int[] array) {
        int[] newArray = new int[array.length - 1];
        for (int i = 0; i < array.length - 1; ++i) {
            newArray[i] = array[i + 1];
        }
        return newArray;
    }

    public BigInteger make_BitSet(ArrayList<Integer> arrayList) {
        BigInteger set = BigInteger.ZERO;
        for (int a : arrayList) {
            set = set.setBit(idx[a]);
        }
        return set;
    }

    public ZDD_Node push(ArrayList<Integer> arrayList) {
        int[] sortedArray = make_sortedArray(arrayList);
        ZDD_Node node = one_terminal;
        for (int i = sortedArray.length - 1; i >= 0; --i) {
            node = getNode(sortedArray[i], zero_terminal, node);
        }
        return node;
    }

    public ZDD_Node push(OrderedShareList.ListNode listNode) {
        ArrayList<Integer> arrayList = new ArrayList<>(listNode.size);
        for (OrderedShareList.ListNode node : listNode) {
            arrayList.add(node.top);
        }
        return push(arrayList);
    }
}
