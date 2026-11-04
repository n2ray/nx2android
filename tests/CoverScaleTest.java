import org.nx2a.CoverScale;

public final class CoverScaleTest {
    public static void main(String[] args) {
        if (CoverScale.sample(256, 256) != 1 || CoverScale.sample(-1, -1) != 1
                || CoverScale.sample(4096, 2048) != 4) throw new AssertionError("cover sampling");
    }
}
