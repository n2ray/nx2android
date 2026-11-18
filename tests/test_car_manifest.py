import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APK = ROOT / 'nxnative/dm/android/apk'


class CarManifest(unittest.TestCase):
    def test_opt_in_adds_private_phone_activity(self):
        code = '''import sys
sys.path.insert(0, sys.argv.pop(1))
import mkapk
app = next(n for n in mkapk.MANIFEST[2] if n[0] == "application")
acts = [n for n in app[2] if n[0] == "activity"]
car = [a for a in acts if (True,"name","org.nx2a.CarPadActivity") in a[1]]
assert len(car) == 1 and (True,"exported",False) in car[0][1]
assert "android.intent.category.CAR_LAUNCHER" in str(acts[0])
'''
        result = subprocess.run([sys.executable, '-c', code, str(APK), 'host.so', 'app.apk', '--dex', 'classes.dex',
                                 '--activity', 'org.nx2a.ExternalActivity', '--android-auto'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_rejects_non_external_activity(self):
        result = subprocess.run([sys.executable, str(APK / 'mkapk.py'), 'host.so', 'app.apk', '--android-auto'],
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('requires an external display activity', result.stderr)

if __name__ == '__main__':
    unittest.main()
