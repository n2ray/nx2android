package org.nx2a;

import android.app.Activity;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.os.Bundle;
import android.view.Gravity;
import android.view.View;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.Comparator;
import org.json.JSONObject;

/** Experimental library: each card selects a prepared game for the bundled runtime. */
public final class LibraryActivity extends Activity {
    private String runtimeId = "";
    private int dp(float n) { return (int) (n * getResources().getDisplayMetrics().density + 0.5f); }
    private GradientDrawable panel(int color, int stroke, int radius) {
        GradientDrawable d = new GradientDrawable(); d.setColor(color); d.setCornerRadius(dp(radius)); d.setStroke(dp(1), stroke); return d;
    }
    private TextView text(String value, int size, int color) {
        TextView t = new TextView(this); t.setText(value); t.setTextSize(size); t.setTextColor(color); return t;
    }
    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        if (getActionBar() != null) getActionBar().hide();
        try (java.io.InputStream in = getAssets().open("library-runtime-id.txt")) {
            byte[] id = new byte[17]; int n = in.read(id); if (n > 0) runtimeId = new String(id, 0, n, StandardCharsets.US_ASCII).trim();
        } catch (IOException ignored) { }
        showLibrary();
    }
    private void showLibrary() {
        LinearLayout page = new LinearLayout(this); page.setOrientation(LinearLayout.VERTICAL);
        page.setPadding(dp(28), dp(22), dp(28), dp(22)); page.setBackgroundColor(Color.rgb(16, 18, 23));
        page.setOnApplyWindowInsetsListener((v, insets) -> {
            v.setPadding(dp(28) + insets.getSystemWindowInsetLeft(), dp(22) + insets.getSystemWindowInsetTop(),
                         dp(28) + insets.getSystemWindowInsetRight(), dp(22) + insets.getSystemWindowInsetBottom());
            return insets;
        });
        TextView heading = text("GAME LIBRARY", 24, Color.rgb(245, 245, 250)); heading.setTypeface(Typeface.DEFAULT, Typeface.BOLD); page.addView(heading);
        TextView sub = text("Choose a prepared game", 14, Color.rgb(166, 165, 160));
        LinearLayout.LayoutParams subParams = new LinearLayout.LayoutParams(-1, -2); subParams.setMargins(0, dp(4), 0, dp(20)); page.addView(sub, subParams);
        ScrollView scroll = new ScrollView(this); LinearLayout cards = new LinearLayout(this); cards.setOrientation(LinearLayout.VERTICAL);
        scroll.addView(cards); page.addView(scroll, new LinearLayout.LayoutParams(-1, 0, 1)); setContentView(page);
        File external = getExternalFilesDir(null); File[] dirs = external == null ? null : new File(external, "games").listFiles();
        if (dirs != null) {
            Arrays.sort(dirs, Comparator.comparing(File::getName));
            for (File dir : dirs) addGame(cards, dir);
        }
        if (cards.getChildCount() == 0) cards.addView(text("No prepared games found.", 16, Color.LTGRAY));
    }
    private void addGame(LinearLayout cards, File dir) {
        String id = dir.getName();
        if (!dir.isDirectory() || !id.matches("[0-9A-F]{16}") || !new File(dir, "mods").isDirectory()
                || !new File(dir, "RomFS").isDirectory() || !new File(dir, "shaders.dmsv").isFile()) return;
        String name, version;
        try (FileInputStream in = new FileInputStream(new File(dir, "nx2a-data.json"))) {
            if (in.available() > 65536) return;
            byte[] data = new byte[65536]; int used = 0, n;
            while (used < data.length && (n = in.read(data, used, data.length - used)) > 0) used += n;
            JSONObject meta = new JSONObject(new String(data, 0, used, StandardCharsets.UTF_8));
            if (!id.equalsIgnoreCase(meta.getString("title_id"))) return;
            name = meta.getString("name"); version = meta.optString("display", "");
        } catch (Exception e) { return; }
        LinearLayout card = new LinearLayout(this); card.setOrientation(LinearLayout.HORIZONTAL); card.setGravity(Gravity.CENTER_VERTICAL);
        card.setPadding(dp(12), dp(12), dp(16), dp(12)); card.setBackground(panel(Color.rgb(31, 31, 42), Color.rgb(86, 84, 99), 10));
        ImageView cover = new ImageView(this); cover.setScaleType(ImageView.ScaleType.FIT_CENTER); cover.setBackgroundColor(Color.rgb(22, 22, 29));
        String coverPath = new File(dir, "cover.png").getPath(); BitmapFactory.Options bounds = new BitmapFactory.Options(); bounds.inJustDecodeBounds = true;
        BitmapFactory.decodeFile(coverPath, bounds); BitmapFactory.Options options = new BitmapFactory.Options();
        options.inSampleSize = CoverScale.sample(bounds.outWidth, bounds.outHeight);
        Bitmap bitmap = BitmapFactory.decodeFile(coverPath, options); if (bitmap != null) cover.setImageBitmap(bitmap);
        card.addView(cover, new LinearLayout.LayoutParams(dp(110), dp(145)));
        LinearLayout info = new LinearLayout(this); info.setOrientation(LinearLayout.VERTICAL); info.setPadding(dp(18), 0, 0, 0);
        TextView title = text(name, 20, Color.rgb(245, 245, 250)); title.setTypeface(Typeface.DEFAULT, Typeface.BOLD); info.addView(title);
        TextView detail = text((version.isEmpty() ? "" : version + "  ·  ") + id, 13, Color.rgb(173, 168, 154)); info.addView(detail);
        boolean compatible = id.equals(runtimeId);
        TextView play = text(compatible ? "▶  PLAY" : "Compatible runtime required", 15, Color.rgb(250, 54, 139)); play.setPadding(0, dp(18), 0, 0); info.addView(play);
        card.addView(info, new LinearLayout.LayoutParams(0, -2, 1));
        if (compatible) card.setOnClickListener(v -> select(id));
        LinearLayout.LayoutParams cp = new LinearLayout.LayoutParams(-1, -2); cp.setMargins(0, 0, 0, dp(12)); cards.addView(card, cp);
    }
    private void select(String id) {
        File tmp = new File(getFilesDir(), "library-selection.tmp"), selected = new File(getFilesDir(), "library-selection.txt");
        try (FileOutputStream out = new FileOutputStream(tmp)) { out.write((id + "\n").getBytes(StandardCharsets.US_ASCII)); out.getFD().sync(); }
        catch (IOException e) { Toast.makeText(this, "Could not select game", Toast.LENGTH_LONG).show(); return; }
        if (!tmp.renameTo(selected)) { tmp.delete(); Toast.makeText(this, "Could not select game", Toast.LENGTH_LONG).show(); return; }
        startActivity(new Intent(this, ExternalActivity.class));
    }
}
