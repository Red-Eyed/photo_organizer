#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Vadym Stupakov"
__email__ = "vadim.stupakov@gmail.com"

from argparse import ArgumentParser
import logging
from collections import defaultdict
from pathlib import Path

from organizer import Organizer

if __name__ == '__main__':
    log_file = Path.cwd().parent / "organize.log"
    log_file.unlink(missing_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s:%(levelname)s:%(message)s',
        datefmt='%H:%M:%S',
        handlers=[logging.FileHandler(log_file.as_posix(), mode="wt", encoding="utf8")]
    )

    parser = ArgumentParser()
    parser.add_argument("--src", type=Path, default=Path.cwd())
    parser.add_argument("--dst", type=Path, default=Path.cwd())
    parser.add_argument("--non-media-path", type=Path, default=Path.cwd().parent)
    parser.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()

    org = Organizer(args.src, args.dst, args.dry_run)

    org.organize()
    org.move_non_media_files(Path.cwd().parent / "non_media")
    org.remove_empty_folders()
    org.deduplicate()
