import json
import os
from pathlib import Path
from shutil import move
from tempfile import NamedTemporaryFile

import scrapy
from itemadapter import ItemAdapter

from kingston.items import *


class KingstonPipeline:
    def process_item(self, item: object, spider: scrapy.Spider):
        basepath = os.path.abspath(os.path.join("..", "items"))
        fullpath = None

        if isinstance(item, Memory):
            fname = item['_model'] + ".json"
            basepath = os.path.abspath(os.path.join(basepath, "Memory", item['_manufacturer']))
            fullpath = os.path.abspath(os.path.join(basepath, fname))

        if fullpath is not None:
            if not isinstance(item, dict):
                return

            Path(basepath).mkdir(parents=True, exist_ok=True)

            if os.path.isfile(fullpath):
                spider.logger.warning(f"file '{fullpath}' exists, skipping!")
                return

            # Save to temporary file
            tmpf = NamedTemporaryFile("w", prefix="kingston-item-", suffix=".json", encoding="utf8", delete=False)
            with tmpf as f:
                json.dump(item, f)
                f.flush()
                spider.logger.info(f"saved as {f.name}")

            # Rename and move the temporary file to actual file
            newpath = move(tmpf.name, fullpath)
            spider.logger.info(f"renamed {tmpf.name} to {newpath}")