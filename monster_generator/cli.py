from __future__ import annotations

import argparse
import os

from .factory import MonsterFactory


def main() -> int:
    p = argparse.ArgumentParser(prog="monster-generator", description="Generate monsters from sprite atlas.")
    sub = p.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("generate", help="Generate one monster image.")
    g.add_argument("--seed", required=True)
    g.add_argument("--state", default="normal")
    g.add_argument("--out", required=True)
    g.add_argument("--canvas", type=int, default=512)
    g.add_argument("--scale", type=float, default=1.0)
    g.add_argument("--print-dna", action="store_true")

    b = sub.add_parser("bundle", help="Generate multiple state variants.")
    b.add_argument("--seed", required=True)
    b.add_argument("--states", default="normal,happy,sad,hungry,ill,dead")
    b.add_argument("--outdir", required=True)
    b.add_argument("--canvas", type=int, default=512)
    b.add_argument("--scale", type=float, default=1.0)
    b.add_argument("--print-dna", action="store_true")

    args = p.parse_args()
    mf = MonsterFactory()

    if args.cmd == "generate":
        img = mf.render(args.seed, state=args.state, canvas=args.canvas, scale=args.scale)
        os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
        img.save(args.out)
        if args.print_dna:
            print(mf.dna(args.seed))
        return 0

    states = [s.strip() for s in args.states.split(",") if s.strip()]
    os.makedirs(args.outdir, exist_ok=True)
    result = mf.bundle(args.seed, outdir=args.outdir, states=states, canvas=args.canvas, scale=args.scale)
    if args.print_dna:
        print(result["dna"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())