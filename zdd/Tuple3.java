package zdd;

public class Tuple3<X, Y, Z> {
    X x;
    Y y;
    Z z;

    public Tuple3(X x, Y y, Z z) {
        this.x = x;
        this.y = y;
        this.z = z;
    } 

    public boolean equals(Object that) {
        if(!(that instanceof Tuple3)) {
            return false;
        }
        Tuple3<X, Y, Z> thatTuple3 = (Tuple3)that;
        return this.x.equals(thatTuple3.x) && this.y.equals(thatTuple3.y) && this.z.equals(thatTuple3.z);
    }

    public int hashCode() {
        // Pair<X, Pair<Y, Z>> thisPair = new Pair<>(x, new Pair<Y, Z>(y, z));
        // return thisPair.hashCode();
        long xh = x.hashCode(), yh = y.hashCode(), zh = z.hashCode();
        return (int) ((((xh + 10) & Integer.MAX_VALUE) * yh % 3483643) * zh % 1147483637);
    }
}