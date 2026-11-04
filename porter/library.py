"""Read-only discovery of prepared game packs; this does not launch games."""
import json
import re
from pathlib import Path

from porter.datapack import read_manifest


def discover(root):
    """Return recognized packs and rejected directory names in a library folder."""
    games, rejected = [], []
    for path in sorted(Path(root).iterdir()):
        if path.is_symlink() or not path.is_dir():
            continue
        manifest = read_manifest(path)
        if not isinstance(manifest, dict):
            rejected.append(path.name)
            continue
        title = manifest.get('title_id')
        name = manifest.get('name')
        if (not isinstance(title, str) or not re.fullmatch(r'[0-9a-fA-F]{16}', title)
                or not isinstance(name, str) or not name.strip()
                or not all((path / part).is_dir() for part in ('mods', 'RomFS'))
                or not (path / 'shaders.dmsv').is_file()):
            rejected.append(path.name)
            continue
        games.append({'title_id': title.upper(), 'name': name, 'directory': path.name,
                      'version': manifest.get('display', '')})
    return games, rejected


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    args = parser.parse_args()
    games, rejected = discover(args.root)
    print(json.dumps({'games': games, 'rejected': rejected}, ensure_ascii=False, indent=2))
