package zdd;

import java.util.ArrayList;
import java.util.Scanner;

public class QueenProblem {
    int n;
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        System.out.print("input N: ");
        int n = scanner.nextInt();

        QueenProblem solver = new QueenProblem(n);
        // solver.solve();
        solver.solveByHalfEnumeration();
        scanner.close();
    }

    public QueenProblem(int n) {
        this.n = n;
    }

    public int[] solve() {
        long startTime = System.currentTimeMillis();
        int[] permutation = new int[n*n];
        for(int i = 0; i < n*n; ++i) {
            permutation[i] = n*n-1-i; // 右下から順に番号を振る
        }
        ZDD zdd = new ZDD(permutation);

        ZDD.ZDD_Node s = zdd.zero_terminal;
        for(int j = 0; j < n; ++j) {
            s = zdd.getNode(grid(0, j), s, zdd.one_terminal);
        }
        for(int i = 1; i < n; ++i) {
            ZDD.ZDD_Node t = zdd.zero_terminal;
            for(int j = 0; j < n; ++j) {
                ArrayList<Integer> arrayList = new ArrayList<Integer>();
                for(int k = 0; k < i; ++k) {
                    arrayList.add(grid(i-k-1, j));
                }
                for(int k = 0; k < Integer.min(i, j); ++k) {
                    arrayList.add(grid(i-k-1, j-k-1));
                }
                for(int k = 0; k < Integer.min(i, n-j-1); ++k) {
                    arrayList.add(grid(i-k-1, j+k+1));
                }
                // --1個ずつoffset-- //
                // zdd.sortByIndex(arrayList);
                // ZDD.ZDD_Node u = s;
                // for(int e: arrayList) {
                //     u = u.offset(e);
                // }
                // t = zdd.getNode(grid(i, j), t, u);
                
                // --まとめてoffset-- //
                t = zdd.getNode(grid(i, j), t, s.offset_s(zdd.make_sortedArray(arrayList)));
                // t = zdd.getNode(grid(i, j), t, s.offset_s(zdd.make_BitSet(arrayList)));
                // t = zdd.getNode(grid(i, j), t, s.offset_s(zdd.orderedShareList.push(arrayList)));
                // t = zdd.getNode(grid(i, j), t, s.offset_s(zdd.push(arrayList)));
            }
            s = t;
            // System.out.println(i); // 途中経過の表示
        }
        
        int ans = s.count();
        
        long endTime = System.currentTimeMillis();
        int clearTime = (int)(endTime-startTime);
        // System.out.println(zdd.createdNodeCount());
        System.out.printf("%1$d×%1$d: %2$d種類, %3$dノード, %4$dms\n", n, ans, zdd.createdNodeCount(), clearTime);
        System.out.println(zdd.cache_OFFSET.size() + zdd.cache_OFFSET_S_BY_ARRAY.size());
        return new int[]{ans, zdd.createdNodeCount(), clearTime};
    }

    public int[] solveByHalfEnumeration() {
        long startTime = System.currentTimeMillis();
        int[] permutation = new int[n*n];
        for(int i = 0; i < n*n; ++i) {
            permutation[i] = n*n-1-i; // 右下から順に番号を振る
        }
        ZDD zdd = new ZDD(permutation);
        
        // 0行目は左半分のみ考える
        ZDD.ZDD_Node s = zdd.zero_terminal;
        for(int j = 0; j < n/2; ++j) {
            s = zdd.getNode(grid(0, j), s, zdd.one_terminal);
        }
        for(int i = 1; i < n; ++i) {
            ZDD.ZDD_Node t = zdd.zero_terminal;
            for(int j = 0; j < n; ++j) {
                ArrayList<Integer> arrayList = new ArrayList<Integer>();
                for(int k = 0; k < i; ++k) {
                    arrayList.add(grid(i-k-1, j));
                }
                for(int k = 0; k < Integer.min(i, j); ++k) {
                    arrayList.add(grid(i-k-1, j-k-1));
                }
                for(int k = 0; k < Integer.min(i, n-j-1); ++k) {
                    arrayList.add(grid(i-k-1, j+k+1));
                }

                // zdd.sortByIndex(arrayList);
                // ZDD.ZDD_Node u = s;
                // for(int e: arrayList) {
                //     u = u.offset(e);
                // }
                // t = zdd.getNode(grid(i, j), t, u);

                // t = zdd.getNode(grid(i, j), t, s.offset_s(zdd.make_BitSet(arrayList)));
                t = zdd.getNode(grid(i, j), t, s.offset_s(zdd.orderedShareList.push(arrayList)));
                // t = zdd.getNode(grid(i, j), t, s.offset_s(zdd.push(arrayList)));
            }
            s = t;
            // System.out.println(i);
        }
        
        int ans = s.count();
        
        // n:奇数のとき、0行目で真ん中に置き、1行目は左半分に置く場合を考える必要あり。
        if(n%2 == 1) {
            s = zdd.getNode(grid(0, n/2), zdd.zero_terminal, zdd.one_terminal);
            for(int i = 1; i < n; ++i) {
                ZDD.ZDD_Node t = zdd.zero_terminal;
                for(int j = 0; j < n; ++j) {
                    if(i == 1 && j == n/2) break;
                    ArrayList<Integer> arrayList = new ArrayList<Integer>();
                    for(int k = 0; k < i; ++k) {
                        arrayList.add(grid(i-k-1, j));
                    }
                    for(int k = 0; k < Integer.min(i, j); ++k) {
                        arrayList.add(grid(i-k-1, j-k-1));
                    }
                    for(int k = 0; k < Integer.min(i, n-j-1); ++k) {
                        arrayList.add(grid(i-k-1, j+k+1));
                    }
                    // zdd.sortByIndex(arrayList);
                    // ZDD.ZDD_Node u = s;
                    // for(int e: arrayList) {
                    //     u = u.offset(e);
                    // }
                    // t = zdd.getNode(grid(i, j), t, u);
                    
                    t = zdd.getNode(grid(i, j), t, s.offset_s(zdd.orderedShareList.push(arrayList)));
                    // t = zdd.getNode(grid(i, j), t, s.offset_s(zdd.push(arrayList)));
                }
                s = t;
                // System.out.println(i);
            }
            ans += s.count();
        }

        ans *= 2;

        long endTime = System.currentTimeMillis();
        int clearTime = (int)(endTime-startTime);
        // System.out.printf("%1$d×%1$d: %2$d種類, %3$dノード, %4$dms\n", n, ans, zdd.createdNodeCount(), clearTime);
        return new int[]{ans, zdd.createdNodeCount(), clearTime};
    }

    private int grid(int i, int j) {
        return i*n + j;
    }
}
