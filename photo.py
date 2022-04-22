#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Vadym Stupakov"
__email__ = "vadim.stupakov@gmail.com"

from datetime import datetime
from pathlib import Path
from PIL import Image
import json


class Photo:
    def __init__(self, photo: Path) -> None:
        self._photo = photo
        self._img = None

    @property
    def exif(self):
        if self._img is None:
            self._img.getexif()
        else:
            return {}

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
                # try to parse date taken fron json google photos if exist
                from_json = self.parse_gphoto_json()
                if from_json is not None:
                    raw_date = float(from_json["photoTakenTime"]["timestamp"])

        except:
            pass
        finally:
            if raw_date is None:
                raw_date = p.stat().st_ctime

        if isinstance(raw_date, float):
            date = datetime.fromtimestamp(raw_date)
        elif isinstance(raw_date, str):
            date = datetime.strptime(raw_date, '%Y:%m:%d %H:%M:%S')
        else:
            raise RuntimeError(f"Invalid format! {raw_date}")

        return date

    def parse_gphoto_json(self) -> dict:
        photo_json = self._photo.parent / (cut_title(self._photo.name) + ".json")
        if photo_json.exists():
            data = json.loads(photo_json.read_text())
        else:
            data = None

        return data

    def __enter__(self):
        try:
            self._img = Image.open(self._photo.resolve().as_posix())
        except:
            pass

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