import ast
import os
import unittest
from pathlib import Path
from unittest.mock import patch


class SerialShaderScanTest(unittest.TestCase):
    def test_serial_scans_all_groups_in_order_with_initialization(self):
        path = Path(__file__).resolve().parents[1] / 'nxnative/dm/gfx/tools/shader_split.py'
        tree = ast.parse(path.read_text())
        func = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'scan_jobs')
        init = []
        env = {'os': os, '_pool_init': lambda *args: init.append(args), 'scan_file': lambda x: x * 2}
        exec(compile(ast.Module(body=[func], type_ignores=[]), str(path), 'exec'), env)
        with patch.dict(os.environ, {'DM_SHADER_SERIAL': '1'}):
            self.assertEqual(env['scan_jobs']((([1, 2], 1), ([], 16), ([3], 1)), 'common', 'trees', 'dicts', 2), [2, 4, 6])
        self.assertEqual(init, [('common', 'trees', 'dicts')])


if __name__ == '__main__': unittest.main()
