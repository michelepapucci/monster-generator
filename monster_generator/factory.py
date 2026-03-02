from __future__ import annotations

import os
from dataclasses import asdict
from importlib import resources
from pathlib import Path
from typing import Iterable, Optional, Dict, Any

from PIL import Image

from .atlas import SpriteAtlas
from .dna import build_catalog, pick_dna
from .renderer import ComposeConfig, compose_monster


def _asset_path(filename: str) -> str:
    return str(resources.files("monster_generator").joinpath("assets", filename))


class MonsterFactory:
    """
    Main importable API for other projects.
    """
    def __init__(self, sheet_path: Optional[str] = None, xml_path: Optional[str] = None):
        self.sheet_path = sheet_path or _asset_path("spritesheet_default.png")
        self.xml_path = xml_path or _asset_path("spritesheet_default.xml")

        self.atlas = SpriteAtlas(self.sheet_path, self.xml_path)
        self.catalog = build_catalog(self.atlas)

    def dna(self, seed: str):
        return pick_dna(seed, self.catalog)

    def render(
        self,
        seed: str,
        state: str = "normal",
        canvas: int = 512,
        scale: float = 1.0,
    ) -> Image.Image:
        dna = pick_dna(seed, self.catalog)
        cfg = ComposeConfig(canvas=canvas, scale=scale)
        return compose_monster(self.atlas, dna, state, self.catalog, cfg)

    def bundle(
        self,
        seed: str,
        outdir: str,
        states: Iterable[str] = ("normal", "happy", "sad", "hungry", "ill", "dead"),
        canvas: int = 512,
        scale: float = 1.0,
        filename_prefix: Optional[str] = None,
    ) -> Dict[str, Any]:
        out = Path(outdir)
        out.mkdir(parents=True, exist_ok=True)

        dna = pick_dna(seed, self.catalog)
        cfg = ComposeConfig(canvas=canvas, scale=scale)

        prefix = filename_prefix or seed
        paths: Dict[str, str] = {}

        for st in states:
            img = compose_monster(self.atlas, dna, st, self.catalog, cfg)
            fname = f"{prefix}_{st}.png".replace(os.sep, "_")
            p = out / fname
            img.save(p)
            paths[st] = str(p)

        return {"seed": seed, "dna": asdict(dna), "paths": paths}