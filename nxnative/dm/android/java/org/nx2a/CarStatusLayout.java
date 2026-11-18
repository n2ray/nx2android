package org.nx2a;

/** Places a non-interactive status pill beside the saved menu button without covering controls. */
final class CarStatusLayout {
    private CarStatusLayout() {}
    static float[] place(float[] data, int count, float w, float h, float width, float height) {
        if (data == null || count < 1 || data.length < 5 + count * 9 || w <= 0 || h <= 0 || width <= 0 || height <= 0) return null;
        int menu = 4 + (count - 1) * 9;
        float mx = data[menu + 1], my = data[menu + 2], radius = data[menu + 3], gap = h * .008f;
        float y = Math.max(0, Math.min(h - height, my - height / 2));
        for (int side : new int[]{1, -1}) {
            float x = side > 0 ? mx + radius + gap : mx - radius - gap - width;
            if (x < 0 || x + width > w) continue;
            boolean clear = true;
            for (int i = 0; i < count - 1; i++) {
                int b = 4 + i * 9; float cx = data[b + 1], cy = data[b + 2], hw = data[b + 3], hh = data[b + 4];
                if (x < cx + hw && x + width > cx - hw && y < cy + hh && y + height > cy - hh) { clear = false; break; }
            }
            if (clear) return new float[]{x, y};
        }
        return null;
    }
}
