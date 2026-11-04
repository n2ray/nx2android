import importlib.util
import io
import unittest
import zlib
from pathlib import Path

path = Path(__file__).resolve().parents[1] / 'nxnative/dm/gfx/tools/uepak.py'
spec = importlib.util.spec_from_file_location('test_uepak', path)
uepak = importlib.util.module_from_spec(spec)
spec.loader.exec_module(uepak)


class LegacyZlibTest(unittest.TestCase):
    def read_block(self, raw, expected, method='Zlib'):
        pak = uepak.Pak.__new__(uepak.Pak)
        pak.f = io.BytesIO(raw)
        pak.key = None
        pak.entry = lambda _: {'method': method, 'raw': expected, 'block_size': expected,
                               'off': 0, 'encrypted': 0, 'blocks': [(0, len(raw))]}
        return pak.read('test')

    def test_valid_and_corrupt_blocks(self):
        payload = b'legacy shader data' * 64
        compressed = zlib.compress(payload)
        self.assertEqual(self.read_block(compressed, len(payload)), payload)
        with self.assertRaises(ValueError): self.read_block(compressed[:-1], len(payload))
        with self.assertRaises(ValueError): self.read_block(compressed + b'x', len(payload))
        with self.assertRaises(ValueError): self.read_block(compressed, len(payload) - 1)
        with self.assertRaises(ValueError): self.read_block(compressed, len(payload), 'LZ5')


if __name__ == '__main__': unittest.main()
