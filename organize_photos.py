#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Vadym Stupakov"
__email__ = "vadim.stupakov@gmail.com"

import logging
from collections import defaultdict
from hashlib import sha256
from pathlib import Path
from pprint import pprint

from organizer import Organizer

if __name__ == '__main__':
    log_file = Path.cwd().parent / "organize.log"
    log_file.unlink(missing_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s:%(message)s',
        handlers=[logging.FileHandler(log_file.as_posix(), mode="wt", encoding="utf8")]
    )

    org = Organizer(Path.cwd(), Path.cwd())

    org.organize()
    org.move_non_media_files(Path.cwd().parent / "non_media")
    org.remove_empty_folders()
    org.deduplicate()
