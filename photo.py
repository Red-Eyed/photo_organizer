#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Vadym Stupakov"
__email__ = "vadim.stupakov@gmail.com"

from functools import cached_property, lru_cache
import logging
from datetime import datetime
from pathlib import Path
from tkinter.messagebox import NO
from PIL import Image
import json

from utils import find_date_from_str

logger = logging.getLogger(__name__)


class Photo:
    _JSON_CACHE = {}

    def __init__(self, photo: Path) -> None:
        self._photo = photo
        self._img = None

    @property
    def exif(self):
        ret = {}
        if self._img is not None:
            try:
                ret = self._img.getexif()
            except:
                logger.exception("")

        return ret

    @cached_property
    def full_name(self):
        # if this is google photo and related json is present - return full name
        if self.gphotos_json is not None:
            return self.gphotos_json["title"]
        else:
            return self._photo.name

    @property
    def gphotos_json(self):
        f = self._photo
        try:
            return self._JSON_CACHE[f.name]
        except KeyError:
            for json_file in f.parent.glob("*.json"):
                d = json.loads(json_file.read_text())
                filename = cut_title(d["title"])
                self._JSON_CACHE[filename] = d

        return self._JSON_CACHE.get(f.name)

    def _get_timestamp(self):
        timestamp = None

        try:
            for tag in [0x0132, 0x9003, 0x9004]:
                timestamp = self.exif.get(tag)
                if timestamp is not None:
                    break

            if timestamp is None:
                # try to parse date taken fron the json google photos if exist
                if self.gphotos_json is not None:
                    timestamp = float(self.gphotos_json["photoTakenTime"]["timestamp"])
        except:
            logger.exception("")

        return timestamp

    @property
    def date_taken(self) -> datetime:
        timestamp = self._get_timestamp()
        date = datetime.fromtimestamp(0.0)

        try:
            if isinstance(timestamp, float):
                date = datetime.fromtimestamp(timestamp)
            elif isinstance(timestamp, str):
                if "0000:00:00 00:00:00" in timestamp:
                    date = datetime.fromtimestamp(0.0)
                else:
                    date = datetime.strptime(timestamp, '%Y:%m:%d %H:%M:%S')
            else:
                parsed = find_date_from_str(self._photo.as_posix())
                if parsed:
                    date = datetime.strptime(parsed, '%Y')
                else:
                    logger.warning(f"Can't find date taken for '{self._photo}'")
        except:
            logger.error(f"Exception at file: '{self._photo.as_posix()}'")
            logger.exception("")

        return date

    def parse_gphoto_json(self) -> dict:
        photo_json = self._photo.parent / (cut_title(self._photo.name) + ".json")
        if photo_json.exists():
            data = json.loads(photo_json.read_text())
        else:
            data = None
            logger.warning(f"File '{photo_json}' does not exist")

        return data

    def __enter__(self):
        try:
            self._img = Image.open(self._photo.resolve().as_posix())
        except:
            logger.exception("")

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self._img is not None:
            self._img.close()


def cut_title(title: str, len_=51):
    ext = "." + title.split(".")[-1]
    cut = title[:51]
    if cut.endswith(ext):
        cut = cut
    else:
        cut = cut[:51 - len(ext)] + ext

    assert len(cut) <= len_

    return cut
