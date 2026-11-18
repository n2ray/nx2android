package org.nx2a;

import android.app.Activity;
import android.os.Bundle;
import android.view.View;
import android.view.WindowManager;
import android.view.Window;
import android.view.KeyEvent;
import android.view.MotionEvent;
import android.view.InputDevice;
import android.os.Build;
import android.view.WindowInsets;
import android.view.WindowInsetsController;

/** Phone controller for the same game activity while Android Auto shows its window. */
public final class CarPadActivity extends Activity {
    private static CarPadActivity current;
    private View pad;
    private boolean started;

    private void hideBars() {
        if (Build.VERSION.SDK_INT >= 30) {
            WindowInsetsController insets = getWindow().getInsetsController();
            if (insets != null) { insets.setSystemBarsBehavior(WindowInsetsController.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE); insets.hide(WindowInsets.Type.systemBars()); }
        }
    }

    @Override public boolean dispatchKeyEvent(KeyEvent event) {
        int s = event.getSource();
        if (((s & InputDevice.SOURCE_GAMEPAD) == InputDevice.SOURCE_GAMEPAD || (s & InputDevice.SOURCE_DPAD) == InputDevice.SOURCE_DPAD)
                && ExternalActivity.externalControllerKey(event)) return true;
        return super.dispatchKeyEvent(event);
    }
    @Override public boolean dispatchGenericMotionEvent(MotionEvent event) {
        int s = event.getSource();
        if (((s & InputDevice.SOURCE_JOYSTICK) == InputDevice.SOURCE_JOYSTICK || (s & InputDevice.SOURCE_GAMEPAD) == InputDevice.SOURCE_GAMEPAD)
                && ExternalActivity.externalControllerMotion(event)) return true;
        return super.dispatchGenericMotionEvent(event);
    }

    @Override protected void onCreate(Bundle state) {
        setTheme(android.R.style.Theme_Material_NoActionBar_Fullscreen);
        super.onCreate(state);
        requestWindowFeature(Window.FEATURE_NO_TITLE);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE | WindowManager.LayoutParams.FLAG_FULLSCREEN);
        if (Build.VERSION.SDK_INT >= 30) {
            getWindow().setDecorFitsSystemWindows(false);
        }
        getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_FULLSCREEN | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION |
            View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION);
        pad = ExternalActivity.createCarPad(this);
        if (pad == null) { finish(); return; }
        current = this;
        setContentView(pad);
        pad.addOnLayoutChangeListener((v, l, t, r, b, ol, ot, oright, ob) -> {
            if (started && current == this) ExternalActivity.carPadSize(r - l, b - t, getResources().getDisplayMetrics().densityDpi);
        });
    }

    @Override protected void onStart() {
        super.onStart();
        started = true;
        if (pad != null) pad.post(() -> { if (started && current == this) { hideBars(); ExternalActivity.carPadSize(pad.getWidth(), pad.getHeight(), getResources().getDisplayMetrics().densityDpi); } });
        ExternalActivity.carPadVisible(true);
    }

    @Override protected void onStop() {
        started = false;
        if (current == this) {
            if (pad != null) ExternalActivity.releaseCarPad(pad);
            ExternalActivity.carPadSize(0, 0, 0);
            ExternalActivity.carPadVisible(false);
        }
        super.onStop();
    }

    @Override protected void onDestroy() {
        if (current == this) current = null;
        super.onDestroy();
    }

    static void close() { if (current != null) current.finishAndRemoveTask(); }
    static boolean isOpen() { return current != null && current.started && !current.isFinishing(); }
}
