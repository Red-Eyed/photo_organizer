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

logger = logging.getLogger(__name__)


@lru_cache(maxsize=100000)
def _all_jsons(file: str):
    ret = {}
    for json_file in Path(file).parent.glob("*.json"):
        d = json.loads(json_file.read_text())
        filename = cut_title(d["title"])
        ret[filename] = d

    return ret


class Photo:
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

    @cached_property
    def gphotos_json(self):
        jsons = _all_jsons(self._photo.as_posix())
        try:
            return jsons[self._photo.name]
        except KeyError:
            return None

    @property
    def date_taken(self):
        raw_date = None
        p = self._photo

        try:
            for tag in [0x0132, 0x9003, 0x9004]:
                raw_date = self.exif.get(tag)
                if raw_date is not None:
                    break

            if raw_date is None:
                # try to parse date taken fron the json google photos if exist
                if self.gphotos_json is not None:
                    raw_date = float(self.gphotos_json["photoTakenTime"]["timestamp"])
        except:
            logger.exception("")
        finally:
            if raw_date is None:
                raw_date = p.stat().st_ctime

        date = datetime.fromtimestamp(0.)
        try:
            if isinstance(raw_date, float):
                date = datetime.fromtimestamp(raw_date)
            elif isinstance(raw_date, str):
                date = datetime.strptime(raw_date, '%Y:%m:%d %H:%M:%S')
            else:
                raise RuntimeError(f"Invalid format! {raw_date}")
        except:
            logger.error(f"Exception at file: {self._photo.as_posix()}")
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
