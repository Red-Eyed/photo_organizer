#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Vadym Stupakov"
__email__ = "vadim.stupakov@gmail.com"

from pathlib import Path
from win32_setctime import setctime
import os


def set_file_created_time(file: Path, timestamp: float):
    setctime(file.as_posix(), timestamp)
    os.utime(file.as_posix(), (timestamp, timestamp))



