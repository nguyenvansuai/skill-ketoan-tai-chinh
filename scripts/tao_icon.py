#!/usr/bin/env python3
"""Tạo icon 512×512 cho plugin: python3 scripts/tao_icon.py "HC" "NS" "#1F4E79"  (cần Pillow)."""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

dong1, dong2, mau = (sys.argv[1:4] + ["", "", "#1F4E79"][len(sys.argv[1:4]):])[:3]
S = 512
img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
d.rounded_rectangle([0, 0, S - 1, S - 1], radius=96, fill=mau)
d.rounded_rectangle([28, 28, S - 29, S - 29], radius=76, outline="white", width=6)
font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
for text, y in [(dong1, 150), (dong2, 330)]:
    if not text:
        continue
    size = 170
    f = ImageFont.truetype(font_path, size)
    while d.textlength(text, font=f) > S - 110:
        size -= 6
        f = ImageFont.truetype(font_path, size)
    d.text((S / 2, y), text, font=f, fill="white", anchor="mm")
out = Path(__file__).resolve().parent.parent / ".claude-plugin" / "icon.png"
img.save(out)
print(out)
