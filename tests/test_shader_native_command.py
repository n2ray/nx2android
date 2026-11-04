import ast
import unittest
from pathlib import Path


class TranslatorCommandTest(unittest.TestCase):
    def test_native_and_dotnet_commands(self):
        script = Path(__file__).resolve().parents[1] / 'nxnative/dm/android/tools/shader_vk.py'
        tree = ast.parse(script.read_text())
        func = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'translator_command')
        env = {}
        exec(compile(ast.Module(body=[func], type_ignores=[]), str(script), 'exec'), env)
        command = env['translator_command']
        self.assertEqual(command('dotnet', 'xlate.dll', None, 'jobs.json', 'out'), ['dotnet', 'xlate.dll', 'jobs.json', 'out'])
        self.assertEqual(command('dotnet', 'xlate.dll', '/app/xlate', 'jobs.json', 'out'), ['/app/xlate', 'jobs.json', 'out'])


if __name__ == '__main__': unittest.main()
