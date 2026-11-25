#!/usr/bin/env python3
"""Copy the pre-rendered front page to the grader's output location.

Pure Python standard library only: no PIL, no network. Deterministic:
every run writes the exact bytes of news-frontpage.png.

Output path:
  - $MAKEFUN_OUTPUT_DIR/entry.png when MAKEFUN_OUTPUT_DIR is set
    (this is the path the make.fun grader expects), otherwise
  - /output/entry.png
The source image is resolved relative to this file, never relative to
the current working directory, so the script works from any cwd and
from a read-only repo mount.
"""

import os
import shutil
import sys

SOURCE_NAME = "news-frontpage.png"
OUTPUT_NAME = "entry.png"
DEFAULT_OUTPUT_DIR = "/output"


def output_path():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or DEFAULT_OUTPUT_DIR
    return os.path.join(out_dir, OUTPUT_NAME)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, SOURCE_NAME)
    dst = output_path()
    parent = os.path.dirname(dst)
    if parent:
        os.makedirs(parent, exist_ok=True)
    shutil.copyfile(src, dst)
    print("wrote", dst)
    return 0


if __name__ == "__main__":
    sys.exit(main())
