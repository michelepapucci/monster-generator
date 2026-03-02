from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, Tuple

from PIL import Image, ImageOps

from .atlas import SpriteAtlas
from .dna import MonsterDNA, stable_int

BBox = Tuple[int, int, int, int]


@dataclass(frozen=True)
class ComposeConfig:
    canvas: int = 512
    scale: float = 1.0
    # Body center offset (slightly down looks better for Telegram)
    body_center_dx: int = 0
    body_center_dy: int = 20
    # Relative attachment (tuned heuristics, easy to tweak later)
    arm_attach_y: float = -0.12   # relative to body height
    arm_attach_x: float = 0.62    # relative to body width
    leg_attach_y: float = 0.46
    leg_attach_x: float = 0.22
    face_eye_y: float = -0.18
    face_mouth_y: float = 0.12
    face_nose_y: float = 0.02
    detail_y: float = -0.55


def _rescale(img: Image.Image, scale: float) -> Image.Image:
    if scale == 1.0:
        return img
    w, h = img.size
    return img.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.NEAREST)


def _paste_at(canvas: Image.Image, sprite: Image.Image, center_xy: Tuple[int, int], anchor_xy: Tuple[int, int]):
    """
    Paste sprite onto canvas so that sprite[anchor_xy] aligns to center_xy on the canvas.
    """
    x = int(center_xy[0] - anchor_xy[0])
    y = int(center_xy[1] - anchor_xy[1])
    canvas.alpha_composite(sprite, (x, y))


def compose_monster(
    atlas: SpriteAtlas,
    dna: MonsterDNA,
    state: str,
    catalog: Dict[str, list],
    cfg: ComposeConfig = ComposeConfig(),
) -> Image.Image:
    """
    Returns a composed RGBA image.
    States: normal, happy, sad, hungry, ill, dead
    """
    state = state.lower().strip()
    allowed = {"normal", "happy", "sad", "hungry", "ill", "dead"}
    if state not in allowed:
        raise ValueError(f"Unknown state '{state}'. Allowed: {sorted(allowed)}")

    canvas = Image.new("RGBA", (cfg.canvas, cfg.canvas), (0, 0, 0, 0))
    cx, cy = cfg.canvas // 2, cfg.canvas // 2

    body = _rescale(atlas.crop(dna.body), cfg.scale)
    arm = _rescale(atlas.crop(dna.arm), cfg.scale)
    leg = _rescale(atlas.crop(dna.leg), cfg.scale)
    eye = _rescale(atlas.crop(dna.eye), cfg.scale)

    eyebrow = _rescale(atlas.crop(dna.eyebrow), cfg.scale) if dna.eyebrow else None
    nose = _rescale(atlas.crop(dna.nose), cfg.scale) if dna.nose else None
    detail = _rescale(atlas.crop(dna.detail), cfg.scale) if dna.detail else None

    mouth_name = {
        "normal": "mouth_closed_teeth.png",
        "happy": "mouth_closed_happy.png",
        "sad": "mouth_closed_sad.png",
        "hungry": "mouth_closed_sad.png",
        "ill": "mouth_closed_sad.png",
        "dead": "mouth_closed_fangs.png",
    }[state]
    if mouth_name not in atlas.boxes:
        mouth = _rescale(atlas.crop(dna.mouth_open), cfg.scale)
    else:
        mouth = _rescale(atlas.crop(mouth_name), cfg.scale)

    eye_override = None
    if state == "happy" and "eye_closed_happy.png" in atlas.boxes:
        eye_override = "eye_closed_happy.png"
    elif state in {"sad", "hungry", "ill"} and "eye_sad.png" in atlas.boxes:
        eye_override = "eye_sad.png"
    elif state == "dead" and "eye_dead.png" in atlas.boxes:
        eye_override = "eye_dead.png"

    if eye_override:
        eye = _rescale(atlas.crop(eye_override), cfg.scale)

    body_center = (cx + cfg.body_center_dx, cy + cfg.body_center_dy)
    _paste_at(canvas, body, body_center, (body.width // 2, body.height // 2))

    if detail:
        detail_pos = (body_center[0], int(body_center[1] + cfg.detail_y * body.height))
        _paste_at(canvas, detail, detail_pos, (detail.width // 2, int(detail.height * 0.95)))

    arm_joint = (arm.width // 2, arm.width // 2)
    left_arm = ImageOps.mirror(arm)

    arm_y = int(body_center[1] + cfg.arm_attach_y * body.height)
    right_x = int(body_center[0] + cfg.arm_attach_x * body.width)
    left_x = int(body_center[0] - cfg.arm_attach_x * body.width)

    _paste_at(canvas, left_arm, (left_x, arm_y), arm_joint)
    _paste_at(canvas, arm, (right_x, arm_y), arm_joint)

    leg_joint = (leg.width // 2, int(leg.height * 0.12))
    leg_y = int(body_center[1] + cfg.leg_attach_y * body.height)
    leg_dx = int(cfg.leg_attach_x * body.width)

    _paste_at(canvas, leg, (body_center[0] - leg_dx, leg_y), leg_joint)
    _paste_at(canvas, leg, (body_center[0] + leg_dx, leg_y), leg_joint)

    eye_pos = (body_center[0], int(body_center[1] + cfg.face_eye_y * body.height))
    _paste_at(canvas, eye, eye_pos, (eye.width // 2, eye.height // 2))

    if eyebrow:
        brow_pos = (body_center[0], int(eye_pos[1] - 0.55 * eye.height))
        _paste_at(canvas, eyebrow, brow_pos, (eyebrow.width // 2, eyebrow.height // 2))

    if nose:
        nose_pos = (body_center[0], int(body_center[1] + cfg.face_nose_y * body.height))
        _paste_at(canvas, nose, nose_pos, (nose.width // 2, nose.height // 2))

    mouth_pos = (body_center[0], int(body_center[1] + cfg.face_mouth_y * body.height))
    _paste_at(canvas, mouth, mouth_pos, (mouth.width // 2, mouth.height // 2))

    if state == "ill" and catalog.get("snot"):
        rng = random.Random(stable_int(f"{dna.body}|{state}"))
        snot_name = rng.choice(catalog["snot"])
        snot = _rescale(atlas.crop(snot_name), cfg.scale)
        snot_pos = (mouth_pos[0] + int(0.18 * mouth.width), mouth_pos[1] - int(0.75 * mouth.height))
        _paste_at(canvas, snot, snot_pos, (snot.width // 2, snot.height // 2))

    if state == "dead":
        canvas = ImageOps.grayscale(canvas).convert("RGBA")
        alpha = canvas.split()[-1]
        canvas.putalpha(alpha)

    return canvas