#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Vadym Stupakov"
__email__ = "vadim.stupakov@gmail.com"

from asyncio.log import logger
from functools import cached_property
from pathlib import Path
from collections import defaultdict
import json
import logging
import os
from pprint import pprint
import re
import shutil
from hashlib import sha256
from pathlib import Path
from datetime import datetime
from typing import List
from tqdm import tqdm
from PIL import Image

from photo import Photo, cut_title
from utils import set_file_created_time

loggert = logging.getLogger(__name__)


class Organizer:
    def __init__(self, src_dir: Path, dst_dir: Path, dry_run=False) -> None:
        self._src_dir = src_dir.resolve()
        self._dst_dir = dst_dir.resolve()
        self._dry_run = dry_run

    @cached_property
    def google_photos_jsnon_map(self):
        jsons = list(self._src_dir.rglob(f"*.json"))
        metadata = {}
        for f in tqdm(iterable=jsons, desc="Collecting Google Photos metadata"):
            f: Path
            d = json.load(f.read_text())
            filename = cut_title(d["title"])
            metadata[filename] = d

        return metadata

    def organize(self):
        for f in tqdm(iterable=self.get_all_media(self._src_dir), desc="Organizing"):
            if "edited-" in Path(f).stem:
                logger.info(f"Skipping edited: '{f.as_posix()}'")
                continue

            with Photo(f) as p:
                date = p.date_taken

                if "screenshot" in f.as_posix().lower():
                    dst_path = self._dst_dir / f"Screenshots"
                else:
                    dst_path = self._dst_dir / f"{date.year}/{date.month}"

                if not self._dry_run:
                    dst_path.mkdir(parents=True, exist_ok=True)

                src = f.as_posix()
                dst = (dst_path / p.full_name).as_posix()

            try:
                if not self._dry_run:
                    shutil.move(src, dst)
            except:
                logger.exception("")
            else:
                logger.info(f"Moved: '{src}' -> '{dst}'")

            try:
                if not self._dry_run:
                    set_file_created_time(Path(dst), date.timestamp())
            except:
                logger.exception("")
            else:
                logger.info(f"Set creation time: '{date}' to '{dst}'")

    def move_non_media_files(self, non_media_dst: Path):
        non_media_dst = Path(non_media_dst)
        non_media_dst.mkdir(parents=True, exist_ok=True)

        p = self._dst_dir
        media = set(self.get_all_media(p))
        all = set(f for f in p.rglob(f"*") if f.is_file())
        non_media = all - media

        for f in non_media:
            dst = non_media_dst / f.name
            try:
                if not self._dry_run:
                    shutil.move(f.as_posix(), dst.as_posix())
            except:
                logger.exception("")
            else:
                logger.info(f"Moved non media file: '{f.as_posix()}' -> '{dst.as_posix()}'")

    def deduplicate(self):
        directory = self._dst_dir

        hashes = set()
        for f in tqdm(iterable=self.get_all_media(directory), desc="Deduplication"):
            data = f.read_bytes()
            digest = sha256(data).digest()
            if digest in hashes:
                try:
                    if not self._dry_run:
                        f.unlink()
                except:
                    logger.exception("")
                else:
                    logger.info(f"Found dublicate: '{f}'. Removed")
            else:
                hashes.add(digest)

    def remove_empty_folders(self):
        walk = list(os.walk(self._dst_dir.resolve().as_posix()))
        for path, _, _ in tqdm(iterable=walk[::-1], desc="Removing empty dirs"):
            if len(os.listdir(path)) == 0:
                try:
                    if not self._dry_run:
                        Path(path).rmdir()
                except PermissionError:
                    logger.info(f"Found empty dir: '{path}'. PermissionError! Can't remove")
                else:
                    logger.info(f"Found empty dir: '{path}'. Removed.")

    @staticmethod
    def get_all_media(img_root_dir: os.PathLike) -> List[Path]:
        img_root_dir = Path(img_root_dir)
        extensions = ["jpg", "png", "gif", "heic", "mp4", "mpg"]

        ret = []
        for e in extensions:
            ret.extend(list(img_root_dir.rglob(f"*.{e}")))

        return ret
