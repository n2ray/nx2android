import json
import tempfile
import unittest
from pathlib import Path

from porter.library import discover


class LibraryTest(unittest.TestCase):
    def test_discovery_and_incomplete_packs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = root / 'octopath'
            pack.mkdir()
            (pack / 'mods').mkdir()
            (pack / 'RomFS').mkdir()
            (pack / 'shaders.dmsv').touch()
            (pack / 'nx2a-data.json').write_text(json.dumps({
                'title_id': '010057d006492000', 'name': 'Octopath', 'display': '1.0.3'}))
            (root / 'broken').mkdir()
            (root / 'broken' / 'nx2a-data.json').write_text('{')
            games, rejected = discover(root)
            self.assertEqual(games, [{'title_id': '010057D006492000', 'name': 'Octopath',
                                      'directory': 'octopath', 'version': '1.0.3'}])
            self.assertEqual(rejected, ['broken'])


if __name__ == '__main__':
    unittest.main()
