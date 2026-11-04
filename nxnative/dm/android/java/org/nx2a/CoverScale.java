package org.nx2a;

public final class CoverScale {
    private CoverScale() { }
    public static int sample(int width, int height) {
        int sample = 1;
        while (Math.max(width, height) / sample > 1024) sample *= 2;
        return sample;
    }
}
