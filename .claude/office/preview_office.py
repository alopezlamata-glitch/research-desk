"""Vista previa aproximada de ~/.pixel-agents/layout.json con los sprites reales de Pixel Agents.

No reproduce el tintado exacto de los suelos: sirve para revisar la distribución, los pasillos y si
el nombre de cada zona queda libre de muebles.
Uso: uv run python .claude/office/preview_office.py <dir assets de pixel-agents> <salida.png>
"""

import colorsys
import json
import sys
from pathlib import Path

import numpy as np
from matplotlib import image as mpimg
from matplotlib import pyplot as plt

T = 16
assets, out = Path(sys.argv[1]), Path(sys.argv[2])
layout = json.loads((Path.home() / ".pixel-agents" / "layout.json").read_text(encoding="utf-8"))
cols, rows = layout["cols"], layout["rows"]
canvas = np.zeros((rows * T, cols * T, 4))
canvas[..., 3] = 1
canvas[..., :3] = 0.1

sprites = {p.stem: mpimg.imread(p) for p in (assets / "furniture").glob("*/*.png")}


def tint(color):
    if color is None:
        return (0.5, 0.5, 0.5)
    light = min(max(0.55 + color["b"] / 250, 0.05), 0.95)
    return colorsys.hls_to_rgb(color["h"] / 360, light, color["s"] / 100)


for i, t in enumerate(layout["tiles"]):
    r, c = divmod(i, cols)
    if t == 255:
        continue
    rgb = (0.17, 0.2, 0.28) if t == 0 else tint(layout["tileColors"][i])
    canvas[r * T:(r + 1) * T, c * T:(c + 1) * T, :3] = rgb
    if t != 0:  # rejilla sutil
        canvas[r * T, c * T:(c + 1) * T, :3] *= 0.92

for f in sorted(layout["furniture"], key=lambda f: f["row"]):
    name, mirror = f["type"].split(":")[0], f["type"].endswith(":left")
    img = sprites.get(name)
    if img is None:
        print("sin sprite:", name)
        continue
    if mirror:
        img = img[:, ::-1]
    h, w = img.shape[:2]
    y, x = f["row"] * T, f["col"] * T
    y0, x0 = max(y, 0), max(x, 0)
    sub = img[y0 - y:min(h, rows * T - y), x0 - x:min(w, cols * T - x)]
    if sub.shape[2] == 3:
        sub = np.dstack([sub, np.ones(sub.shape[:2])])
    a = sub[..., 3:4]
    region = canvas[y0:y0 + sub.shape[0], x0:x0 + sub.shape[1], :3]
    region[:] = region * (1 - a) + sub[..., :3] * a

fig, ax = plt.subplots(figsize=(cols / 3, rows / 3), dpi=110)
ax.imshow(canvas, interpolation="nearest")
area_tiles = layout.get("areaTiles") or []
for area in layout.get("areas", []):
    cells = [divmod(i, cols) for i, a in enumerate(area_tiles) if a == area["label"]]
    if cells:
        rr, cc = np.mean(cells, axis=0)
        ax.text((cc + 0.5) * T, (rr + 0.5) * T, area["label"], color=area["color"],
                ha="center", va="center", fontsize=13, fontweight="bold")
ax.axis("off")
fig.savefig(out, bbox_inches="tight", facecolor="#1a1a2e")
print(out)
