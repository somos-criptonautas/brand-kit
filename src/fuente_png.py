"""Ink coverage of the 2023 lockup PNG: the only surviving source of the lettering."""
from pathlib import Path
import numpy as np
from PIL import Image

SRC = Path(__file__).parent / 'fuente' / 'logo-original-2023.png'
X0, X1 = 185, 815          # name only, symbol excluded


def coverage():
    a = np.array(Image.open(SRC).convert('RGBA')).astype(float)
    alpha = a[..., 3] / 255
    lum = a[..., :3].mean(2)
    solid = lum[alpha > 0.99]
    ink = np.median(solid[solid < 80])         # lettering colour, not pure black
    c = alpha * np.clip((255 - lum) / (255 - ink), 0, 1)
    return c[:, X0:X1], ink
