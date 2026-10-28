#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 CasX61
"""
Regenerate everything derived (strings, settings, skin) and package the addon
as an installable zip in dist/.

    python3 tools/build.py            # strings, settings, skin, zip
    python3 tools/build.py --media    # also re-render icons and textures
"""

import os
import re
import subprocess
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, 'tools')
ADDON_DIR = 'script.auradeck'
SKIP_DIRS = {'__pycache__'}
SKIP_FILES = {'.DS_Store'}


def run(script):
    subprocess.run([sys.executable, os.path.join(TOOLS, script)], check=True, cwd=TOOLS)


def version():
    with open(os.path.join(ROOT, ADDON_DIR, 'addon.xml'), encoding='utf-8') as handle:
        return re.search(r'<addon[^>]+version="([^"]+)"', handle.read()).group(1)


def package():
    dist = os.path.join(ROOT, 'dist')
    os.makedirs(dist, exist_ok=True)
    target = os.path.join(dist, f'{ADDON_DIR}-{version()}.zip')
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as archive:
        for folder, dirs, files in os.walk(os.path.join(ROOT, ADDON_DIR)):
            dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
            for name in sorted(files):
                if name in SKIP_FILES or name.endswith('.pyc'):
                    continue
                path = os.path.join(folder, name)
                archive.write(path, os.path.relpath(path, ROOT))
    return target


def main():
    if '--media' in sys.argv:
        run('make_media.py')
    run('i18n.py')
    run('make_settings.py')
    run('make_skin.py')
    print('package:', package())


if __name__ == '__main__':
    main()
