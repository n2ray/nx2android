import ast
import functools
import unittest
from pathlib import Path


class SpinCacheTest(unittest.TestCase):
    def test_bounded_cache_redecodes_without_changing_results(self):
        script = Path(__file__).resolve().parents[1] / 'nxnative/dm/tools/patch_nso.py'
        tree = ast.parse(script.read_text())
        func = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'spin_ins')
        class Decoder:
            calls = 0
            def disasm(self, data, address):
                self.calls += 1
                return iter([(data, address)])
        decoder = Decoder()
        env = {'lru_cache': functools.lru_cache, 'md': decoder, 'IMG': bytearray(4 * 32770)}
        exec(compile(ast.Module(body=[func], type_ignores=[]), str(script), 'exec'), env)
        decode = env['spin_ins']
        first = decode(0)
        self.assertEqual(decode(0), first)
        self.assertEqual(decoder.calls, 1)
        for i in range(1, 32770): decode(i * 4)
        self.assertEqual(decode.cache_info().currsize, 32768)
        self.assertEqual(decode(0), first)
        self.assertEqual(decoder.calls, 32771)


if __name__ == '__main__': unittest.main()
