"""SOLMARA — travel poster for a place that isn't there.

Reads poster.png (the generated Solmara artwork: the white lighthouse on
the black cliff above the glowing turquoise sea) and writes it to
/output/entry.png at exactly 1024x1024, deterministic, under the 1 MiB cap.
"""

import os
from pathlib import Path

from PIL import Image

SIZE = 1024
MAX_BYTES = 1_048_576


def build() -> Path:
    here = Path(__file__).resolve().parent
    src = here / "poster.png"
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "entry.png"

    img = Image.open(src).convert("RGB")
    # Centre-crop to square, then resize to exactly 1024x1024.
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    img = img.crop((left, top, left + side, top + side))
    img = img.resize((SIZE, SIZE), Image.LANCZOS)

    # Flat gouache-style art: a 256-colour adaptive palette keeps it
    # visually identical while staying far under the 1 MiB cap.
    # Step down the palette only if a level is still over the cap.
    for colors in (256, 128, 64):
        pal = img.quantize(colors=colors, method=Image.Quantize.MEDIANCUT,
                           dither=Image.Dither.NONE)
        pal.save(out_path, format="PNG", optimize=True)
        if out_path.stat().st_size <= MAX_BYTES:
            break

    final = Image.open(out_path)
    assert final.size == (SIZE, SIZE), f"bad size {final.size}"
    assert out_path.stat().st_size <= MAX_BYTES, "entry.png over 1 MiB"

    return out_path


if __name__ == "__main__":
    path = build()
    print(f"wrote {path} ({path.stat().st_size} bytes)")
