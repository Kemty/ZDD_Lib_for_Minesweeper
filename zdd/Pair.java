package zdd;

public class Pair<X, Y> {
    public X x;
    public Y y;
    
    public Pair(X x, Y y){
        this.x = x;
        this.y = y;
    }

    public boolean equals(Object that) {
            if(!(that instanceof Pair)) {
                return false;
            }
            Pair<X, Y> thatPair = (Pair)that;
        return this.x.equals(thatPair.x) && this.y.equals(thatPair.y);
    }

    public int hashCode() {
        long xh = x.hashCode(), yh = y.hashCode();
        return (int)(((5*xh+12345)&Integer.MAX_VALUE)*yh%1107483613);
    }
}
