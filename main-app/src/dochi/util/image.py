import base64
import math
from typing import List, Optional
from typing_extensions import Literal
import struct
import imghdr


# https://stackoverflow.com/questions/8032642/how-to-obtain-image-size-using-standard-python-class-without-using-external-lib
def test_jpeg(h, f):
    # SOI APP2 + ICC_PROFILE
    if h[0:4] == "\xff\xd8\xff\xe2" and h[6:17] == b"ICC_PROFILE":
        return "jpeg"
    # SOI APP14 + Adobe
    if h[0:4] == "\xff\xd8\xff\xee" and h[6:11] == b"Adobe":
        return "jpeg"
    # SOI DQT
    if h[0:4] == "\xff\xd8\xff\xdb":
        return "jpeg"


imghdr.tests.append(test_jpeg)


def get_image_size(fname):
    """Determine the image type of fhandle and return its size.
    from draco"""
    with open(fname, "rb") as fhandle:
        head = fhandle.read(24)
        if len(head) != 24:
            return
        what = imghdr.what(None, head)
        if what == "png":
            check = struct.unpack(">i", head[4:8])[0]
            if check != 0x0D0A1A0A:
                return
            width, height = struct.unpack(">ii", head[16:24])
        elif what == "gif":
            width, height = struct.unpack("<HH", head[6:10])
        elif what == "jpeg":
            try:
                fhandle.seek(0)  # Read 0xff next
                size = 2
                ftype = 0
                while not 0xC0 <= ftype <= 0xCF or ftype in (0xC4, 0xC8, 0xCC):
                    fhandle.seek(size, 1)
                    byte = fhandle.read(1)
                    while ord(byte) == 0xFF:
                        byte = fhandle.read(1)
                    ftype = ord(byte)
                    size = struct.unpack(">H", fhandle.read(2))[0] - 2
                # We are at a SOFn block
                fhandle.seek(1, 1)  # Skip `precision' byte.
                height, width = struct.unpack(">HH", fhandle.read(4))
            except Exception:  # IGNORE:W0703
                return
        else:
            return
        return width, height


def to_base64(path: str, t: Literal["png", "jpg"] = "png") -> str:
    return f"data:image/{t};base64," + base64.b64encode(open(path, "rb").read()).decode(
        "utf-8"
    )


# svg renderer
def render_svg(
    width: float,
    height: float,
    min_x: float = 0,
    min_y: float = 0,
    *,
    defs: List[str] = [],
    inner: List[str] = [],
) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" style="isolation:isolate" viewBox="{min_x} {min_y} {width} {height}" width="{width}pt" height="{height}pt"><defs>{"".join(defs)}</defs>{"".join(inner)}</svg>"""


def get_hash(o) -> str:
    return hex(hash(o))[2:]


# clip path generator
def get_clip_path(path: str) -> str:
    return (
        f'<clipPath id="_clipPath_{get_hash(path)}">'
        f'<path d="{path}" />'
        f"</clipPath>"
    )


# image def generator
def get_image_def(path: str, t: Literal["png", "jpg"] = "png") -> str:
    (iw, ih) = get_image_size(path)
    return f'<image width="{iw}" height="{ih}" href="{to_base64(path, t)}" id="img_{get_hash(path)}" />'


# image use generator
def use_image(path: str, t: Literal["png", "jpg"] = "png", *, width: Optional[float] = None, height: Optional[float] = None, tx: float = 0, ty: float = 0) -> str:
    (iw, ih) = get_image_size(path)
    sx = 1 if width is None else width / iw
    sy = 1 if height is None else height / ih
    return f'<use href="#img_{get_hash(path)}" transform="matrix({sx}, 0, 0, {sy}, {tx}, {ty})" />'


# Rounded square generator
def get_rounded_square_path(
    w: float, h: float, r: float, cx: float = 0, cy: float = 0
) -> str:
    tx = cx - w / 2
    ty = cy - h / 2
    d = 0.448
    return (
        f"M {tx + r} {ty} "
        f"L {tx + w - r} {ty} "
        f"C {tx + w - d * r} {ty} {tx + w} {d * r + ty} {tx + w} {r + ty} "
        f"L {tx + w} {h - r + ty} "
        f"C {tx + w} {h - d * r + ty} {tx + w - d * r} {h + ty} {tx + w - r} {h + ty} "
        f"L {tx + r} {h + ty} "
        f"C {tx + d * r} {h + ty} {tx} {h - d * r + ty} {tx} {h - r + ty} "
        f"L {tx} {r + ty} "
        f"C {tx} {d * r + ty} {tx + d * r} {ty} {tx + r} {ty} Z"
    )


# Squircle generator
def get_squircle_path(
    w: float,
    h: float,
    cx: float = 0,
    cy: float = 0,
    exponent: float = 4,
    resolution: int = 48,
) -> str:
    points = [
        (
            w / 2 * (math.cos(t) ** (2 / exponent)),
            h / 2 * (math.sin(t) ** (2 / exponent)),
        )
        for t in range(0, math.pi / 2, math.pi / (2 * resolution))
    ]
    # 1st quadrant to 1st & 2nd quadrants
    points = points + [(-y, x) for (x, y) in points]
    # 1st & 2nd quadrants to 1st - 4th quadrants
    points = points + [(-x, -y) for (x, y) in points] + [points[0]]

    return (
        "".join(
            ("M" if i == 0 else "L") + f" {x + cx} {y + cy}"
            for (i, (x, y)) in enumerate(points)
        )
        + "Z"
    )
