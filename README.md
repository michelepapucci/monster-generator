# Monster Generator

Deterministic procedural monster generator built from a sprite sheet + XML atlas.

This library composes modular creature parts (body, arms, legs, eyes, mouth, details) into a fully rendered PNG image.

Designed for:
- Virtual pets
- Game prototypes
- Procedural character systems

---

## ✨ Features

- Deterministic generation from a seed
- Multiple emotional states (happy, sad, ill, dead, etc.)
- Pure Python
- CLI support
- Installable as a reusable library
- No external services required

---

## 📦 Installation

### Development install

From the repository root:

```bash
pip install -e .
```

this installs 'monster-generator' as a command-line tool.

## CLI Usage

### Generate a single monster image

```bash
monster-generator generate \
  --seed test123 \
  --state happy \
  --out happy.png
```

### Generate all states variant

```bash
monster-generator bundle \
  --seed test123 \
  --outdir variants/
```

The default states generated are:
- normal
- happy
- sad
- hungry
- ill
- dead

### CLI Options

`generate`

| Option        | Description                |
| ------------- | -------------------------- |
| `--seed`      | Deterministic seed string  |
| `--state`     | Monster state              |
| `--out`       | Output PNG file            |
| `--canvas`    | Canvas size (default 512)  |
| `--scale`     | Scale multiplier for parts |
| `--print-dna` | Print the generated DNA    |

`bundle`

| Option        | Description            |
| ------------- | ---------------------- |
| `--seed`      | Deterministic seed     |
| `--states`    | Comma-separated states |
| `--outdir`    | Output folder          |
| `--canvas`    | Canvas size            |
| `--scale`     | Scale multiplier       |
| `--print-dna` | Print DNA              |

## Python API Usage

### Basic Usage

```python
from monster_generator import MonsterFactory

mf = MonsterFactory()

img = mf.render(
    seed="group-123",
    state="happy",
)

img.save("monster.png")
```

## Generate all states variants

```python
from monster_generator import MonsterFactory

mf = MonsterFactory()

bundle = mf.bundle(
    seed="group-123",
    outdir="variants"
)

print(bundle["paths"])
```

Output:
```
{
  "normal": "variants/group-123_normal.png",
  "happy": "variants/group-123_happy.png",
  ...
}
```

# 🧬 Deterministic Generation

Each seed produces the same monster every time:

```python
mf.render("abc") == mf.render("abc")  # True
```


# 🙏 Credits

Monster Generator by Michele Papucci

Sprite assets by Kenney at 
https://kenney.nl/

Assets licensed under CC0 1.0 Universal.  
Please consider supporting Kenney if you use these assets.

## 📜 License

MIT License
See LICENSE file for details.