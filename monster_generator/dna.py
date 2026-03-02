from __future__ import annotations

import hashlib
import random
import re
from dataclasses import dataclass
from typing import Dict, List, Optional

from .atlas import SpriteAtlas


@dataclass(frozen=True)
class MonsterDNA:
    color: str                 # blue/dark/green/red/white/yellow
    body: str                  # body_...png
    arm: str                   # arm_...png (we mirror for left)
    leg: str                   # leg_...png (duplicate)
    eye: str                   # eye_...png
    eyebrow: Optional[str]     # eyebrowA/B/C (optional)
    nose: Optional[str]        # nose_...png (optional)
    detail: Optional[str]      # detail_* (horn/ear/antenna/etc) optional
    mouth_open: str            # mouthA..J


def stable_int(seed: str) -> int:
    """Deterministic across python versions/platforms."""
    h = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    return int(h[:16], 16)


def build_catalog(atlas: SpriteAtlas) -> Dict[str, List[str]]:
    """
    Groups sprite names into categories based on filename.
    """
    names = sorted(atlas.boxes.keys())

    cat: Dict[str, List[str]] = {
        "body": [],
        "arm": [],
        "leg": [],
        "eye": [],
        "eyebrow": [],
        "mouth_open": [],
        "mouth_closed": [],
        "nose": [],
        "detail": [],
        "snot": [],
    }

    for n in names:
        base = n.replace(".png", "")
        if base.startswith("body_"):
            cat["body"].append(n)
        elif base.startswith("arm_"):
            cat["arm"].append(n)
        elif base.startswith("leg_"):
            cat["leg"].append(n)
        elif base.startswith("eye_"):
            cat["eye"].append(n)
        elif base.startswith("eyebrow"):
            cat["eyebrow"].append(n)
        elif base.startswith("mouth_closed_"):
            cat["mouth_closed"].append(n)
        elif re.fullmatch(r"mouth[A-J]", base):
            cat["mouth_open"].append(n)
        elif base.startswith("nose_"):
            cat["nose"].append(n)
        elif base.startswith("detail_"):
            cat["detail"].append(n)
        elif base.startswith("snot_"):
            cat["snot"].append(n)

    # Sanity checks for minimum viable generation
    for needed in ("body", "arm", "leg", "eye"):
        if not cat[needed]:
            raise ValueError(f"Missing required category: {needed}")

    return cat


def pick_dna(seed: str, catalog: Dict[str, List[str]]) -> MonsterDNA:
    rng = random.Random(stable_int(seed))

    # Choose a base color (ties body/arm/leg/detail together)
    colors = ["blue", "dark", "green", "red", "white", "yellow"]
    color = rng.choice(colors)

    def pick_with_color(items: List[str], prefix: str) -> str:
        filtered = [n for n in items if n.startswith(f"{prefix}{color}")]
        return rng.choice(filtered) if filtered else rng.choice(items)

    body = pick_with_color(catalog["body"], "body_")
    arm = pick_with_color(catalog["arm"], "arm_")
    leg = pick_with_color(catalog["leg"], "leg_")

    # Eyes: pick any
    eye = rng.choice(catalog["eye"])

    eyebrow = rng.choice(catalog["eyebrow"]) if catalog["eyebrow"] and rng.random() < 0.35 else None
    nose = rng.choice(catalog["nose"]) if catalog["nose"] and rng.random() < 0.35 else None

    # Details: prefer same color if possible
    detail = None
    if catalog["detail"] and rng.random() < 0.55:
        same = [n for n in catalog["detail"] if n.startswith(f"detail_{color}_")]
        detail = rng.choice(same) if same else rng.choice(catalog["detail"])

    mouth_open = rng.choice(catalog["mouth_open"]) if catalog["mouth_open"] else "mouthA.png"

    return MonsterDNA(
        color=color,
        body=body,
        arm=arm,
        leg=leg,
        eye=eye,
        eyebrow=eyebrow,
        nose=nose,
        detail=detail,
        mouth_open=mouth_open,
    )