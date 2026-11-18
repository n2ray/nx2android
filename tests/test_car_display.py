import pathlib
import subprocess
import tempfile
import unittest


class CarDisplayTest(unittest.TestCase):
    def test_display_and_driver_flags(self):
        root = pathlib.Path(__file__).resolve().parents[1]
        helper = root / 'nxnative/dm/android/java/org/nx2a/CarDisplay.java'
        code = '''package org.nx2a;
public class TestCarDisplay {
    public static void main(String[] args) {
        String pkg = "org.nx2a.sifu.test";
        assert CarDisplay.isOwnCarDisplay("NativeDisplay:ComponentInfo{" + pkg + "/org.nx2a.ExternalActivity}", pkg);
        assert !CarDisplay.isOwnCarDisplay("NativeDisplay:ComponentInfo{other/pkg.Activity}", pkg);
        assert !CarDisplay.isOwnCarDisplay("HDMI Screen", pkg);
        assert !CarDisplay.isOwnCarDisplay(null, pkg);
        assert CarDisplay.sysmemFlags(null).equals("sysmem");
        assert CarDisplay.sysmemFlags("nobin").equals("nobin,sysmem");
        assert CarDisplay.sysmemFlags("sysmem,nobin").equals("sysmem,nobin");
        assert CarDisplay.sysmemFlags("gmem,nobin").equals("gmem,nobin");
    }
}'''
        with tempfile.TemporaryDirectory() as temp:
            source = pathlib.Path(temp) / 'TestCarDisplay.java'
            source.write_text(code)
            subprocess.run(['javac', '-d', temp, str(helper), str(source)], check=True)
            subprocess.run(['java', '-ea', '-cp', temp, 'org.nx2a.TestCarDisplay'], check=True)


if __name__ == '__main__':
    unittest.main()
