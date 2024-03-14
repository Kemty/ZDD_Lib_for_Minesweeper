package zdd;

import java.lang.Runtime;

public class QueenProblemTest {
    public static void main(String[] args) {
        int repeat = 3;
        int startN = 1, endN = 14;
        for(int n = startN; n <= endN; ++n) {
            int ans = 0;
            int nodeCnt = 0;
            int fastestTime = Integer.MAX_VALUE;
            for(int i = 0; i < repeat; ++i) {
                Runtime r = Runtime.getRuntime();
                r.gc();
                QueenProblem queenProblem = new QueenProblem(n);
                // int[] ans_nodeCnt_clearTime = queenProblem.solve();
                int[] ans_nodeCnt_clearTime = queenProblem.solveByHalfEnumeration();
                ans = ans_nodeCnt_clearTime[0];
                nodeCnt = ans_nodeCnt_clearTime[1];
                fastestTime = Integer.min(fastestTime, ans_nodeCnt_clearTime[2]);
            }
            System.out.printf("%1$d×%1$d: %2$d種類, %3$dノード, %4$dms\n", n, ans, nodeCnt, fastestTime);
        }
    }
    
}
