#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Vadym Stupakov"
__email__ = "vadim.stupakov@gmail.com"

from pathlib import Path
from win32_setctime import setctime
import os
import re

def set_file_created_time(file: Path, timestamp: float):
    setctime(file.as_posix(), timestamp)
    os.utime(file.as_posix(), (timestamp, timestamp))

year = "20[0-2][0-9]"
month = "[0-9]{2}"
day = "[0-9]{2}"
sep = "[\-,_,/]"
regexps = [
    # re.compile(f".*({year}{sep}{month}{sep}{day}).*"),
    # re.compile(f".*({year}{sep}{month}).*"),
    re.compile(f".*({year}){sep}.*")
]

def find_date_from_str(s: str):


    for r in regexps:
        found = r.match(s)
        if found is not None:
            return found.group(1)
