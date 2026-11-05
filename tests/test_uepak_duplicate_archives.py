import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

path = Path(__file__).resolve().parents[1] / 'nxnative/dm/gfx/tools/uepak.py'
spec = importlib.util.spec_from_file_location('uepak_duplicate_test', path)
uepak = importlib.util.module_from_spec(spec)
spec.loader.exec_module(uepak)


class DuplicateArchivesTest(unittest.TestCase):
    def test_base_and_update_archives_are_both_preserved(self):
        class Pak:
            files = ['ShaderArchive-Global-GLSL_SWITCH.ushaderbytecode']
            def __init__(self, path, key): self.data = Path(path).read_bytes()
            def read(self, path): return self.data

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base, update = root / 'base.pak', root / 'update.pak'
            base.write_bytes(b'base'); update.write_bytes(b'update')
            job, out = root / 'job', root / 'out'
            with patch.multiple(uepak, nso_image=lambda _: (b'', 0, 0),
                                io_shader_tocs=lambda _: [], archive_names=lambda _: [],
                                unreal_paks=lambda *a, **k: [base, update],
                                footer=lambda _: (False,), Pak=Pak,
                                archive=lambda _: {'shaders': [], 'code': 0},
                                lz4_shaders=lambda *a: None,
                                decoded_archive=lambda b, _: b):
                listing, count = uepak.job(str(root), 'main', str(job))
                self.assertEqual(count, 0)
                self.assertEqual(len({item['name'] for item in listing}), 2)
                uepak.finish(str(job), str(out))
                self.assertEqual({p.read_bytes() for p in out.iterdir()}, {b'base', b'update'})


if __name__ == '__main__': unittest.main()
