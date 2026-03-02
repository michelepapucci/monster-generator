from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Dict, Tuple

from PIL import Image

BBox = Tuple[int, int, int, int]  # x, y, w, h


class SpriteAtlas:
    def __init__(self, sheet_path: str, xml_path: str):
        self.sheet_path = sheet_path
        self.xml_path = xml_path
        self.sheet = Image.open(sheet_path).convert("RGBA")
        self.boxes: Dict[str, BBox] = self._parse_xml(xml_path)

    @staticmethod
    def _parse_xml(xml_path: str) -> Dict[str, BBox]:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        boxes: Dict[str, BBox] = {}
        for sub in root.iter("SubTexture"):
            a = sub.attrib
            name = a["name"]
            boxes[name] = (int(a["x"]), int(a["y"]), int(a["width"]), int(a["height"]))
        if not boxes:
            raise ValueError("No SubTexture entries found in XML.")
        return boxes

    def crop(self, name: str) -> Image.Image:
        if name not in self.boxes:
            raise KeyError(f"Sprite not found in atlas: {name}")
        x, y, w, h = self.boxes[name]
        return self.sheet.crop((x, y, x + w, y + h))