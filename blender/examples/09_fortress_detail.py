"""Toy fortress at the house level of detail (bkit.detail): the reference for 'cute, not cheap'."""
from pathlib import Path
import math
import sys

import bkit as b
import bkit.detail as d

out = Path(sys.argv[sys.argv.index('--') + 1])
m, M, rng = b.modelling, b.materials, d.rng
b.scene.new_scene(look="neutral", resolution=(1600, 1600))
parts = d.base_disc()
Z = 0.1
for x in (-3.1, 3.1):
    parts.append(d.tower(0.82, 2.7, (x, 1.55, Z)))
    parts.append(d.tower(0.7, 2.1, (x, -1.65, Z), flag=None))
parts.append(d.wall(5.0, 1.8, 0.62, (0, 1.55, Z)))
for x in (-3.1, 3.1):
    parts.append(d.wall(2.0, 1.8, 0.62, (x, -0.05, Z), 90))
for x in (-1.9, 1.9):
    parts.append(d.wall(1.3, 1.8, 0.62, (x, -1.65, Z)))
parts.append(d.gate(1.9, 2.25, (0, -1.65, Z)))
parts.append(d.house(2.5, 1.9, 1.7, (0, 0.35, Z)))
for size, loc, facing in [(1.15, (-2.3, -3.6, Z), -25), (0.85, (-0.9, -4.2, Z), 10), (1.0, (3.9, -3.0, Z), -40), (0.7, (4.6, -1.2, Z), -60)]:
    parts.append(d.duck(size, loc, facing))
parts.append(d.cannon((1.7, -4.0, Z), aim=150, s=1.5))
ball = M.make("toy_plastic", "#3A3F4C")
for p in ((2.9, -4.3, 0.17), (3.2, -4.25, 0.17), (3.05, -4.02, 0.17), (3.05, -4.2, 0.4)):
    parts.append(m.sphere(0.17, 20, 12, (p[0], p[1], Z + p[2]), ball, "ball"))
parts.append(d.cobbles([(0, -2.3 - 0.42 * i) for i in range(6)]))
parts.append(m.crate(0.7, (-3.9, -2.4, Z)))
parts.append(m.barrel(0.9, (-4.5, -1.5, Z)))
for i, (x, y, sz) in enumerate(((-4.6, 0.6, 0.9), (4.7, 0.9, 1.0), (-1.2, 3.6, 0.8), (1.8, 3.9, 0.9))):
    parts.append(m.bush(sz, seed=i + 1, location=(x, y, Z), color="#58B947", flowers=3))
for i in range(26):
    a, r = rng.uniform(0, 2 * math.pi), rng.uniform(3.9, 5.4)
    x, y = r * math.cos(a), r * math.sin(a) * 0.95
    if abs(x) < 1.2 and y < 0:
        continue
    parts.append(m.grass_tuft(rng.uniform(0.22, 0.38), 7, i + 3, (x, y, Z), rng.choice(("#4FAE3E", "#5DBB45"))))
    if i % 3 == 0:
        fx, fy = x + 0.25, y + 0.1
        parts.append(m.cylinder(0.012, 0.22, 6, 0, 1, (fx, fy, Z + 0.11), M.make("clay", "#4FAE3E"), "stem"))
        parts.append(m.sphere(0.07, 12, 8, (fx, fy, Z + 0.24), M.make("toy_plastic", rng.choice(("#FFFFFF", "#FF7AA8", "#FFD23F"))), "flower", scale=(1, 1, 0.55)))

subject = parts
L = b.lighting


def shot(name, cyc, worldc, az=28, el=20, lens=85, margin=0.68, target=None, distance=None):
    cam = b.scene.add_camera(subject, azimuth=az, elevation=el, lens=lens, margin=margin) if target is None else \
        b.scene.add_camera(target=target, distance=distance, azimuth=az, elevation=el, lens=lens)
    b.render.still(str(out / (name + ".png")), quality="hero")


c = b.scene.cyclorama(subject=subject, color="#63BDFA", name="CycBlue")
L.add_light("AREA", 5.2, "#FFE3BA", target=(0, 0, 2), azimuth=-30, elevation=48, distance=22, size=6, name="key")
L.add_light("AREA", 0.7, "#CFE2FF", target=(0, 0, 2), azimuth=88, elevation=14, distance=24, size=22, name="fill")
L.add_light("AREA", 4.0, "#FFFFFF", target=(0, 0, 2), azimuth=186, elevation=38, distance=22, size=7, name="rim")
L.add_light("AREA", 2.5, "#8FD0FF", target=(0, 16, 8), azimuth=28, elevation=60, distance=30, size=34, name="backwash")
b.scene.world_color("#F2F7FF", 0.7)
shot("hd-wide", None, None)
shot("hd-gate", None, None, az=18, el=12, lens=70, target=(0.6, -2.6, 1.2), distance=13)
shot("hd-roof", None, None, az=40, el=30, lens=85, target=(1.5, 0.6, 3.0), distance=13)
print("TRIS", sum(m.tri_count(o) for o in parts if o.type == "MESH"))
b.finish()
