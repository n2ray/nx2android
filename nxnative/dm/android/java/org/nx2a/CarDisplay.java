package org.nx2a;

final class CarDisplay {
    private CarDisplay() {}

    static boolean isOwnCarDisplay(String name, String packageName) {
        return name != null && packageName != null && !packageName.isEmpty()
            && name.startsWith("NativeDisplay:ComponentInfo{" + packageName + "/") && name.endsWith("}");
    }

    static String sysmemFlags(String current) {
        if (current == null || current.isEmpty()) return "sysmem";
        for (String flag : current.split(","))
            if (flag.trim().equals("sysmem") || flag.trim().equals("gmem")) return current;
        return current + ",sysmem";
    }
}
