"""
inventory.py

all commands related to inventory and items
(do not include store or shopping)
"""

import math
import os
from typing import List
from ...database import model, get
from ...util import image


def render_inventory(items: List[model.Item], page: int = 1) -> dict:
    # debug
    WIDTH = 6
    HEIGHT = 4
    NUM = WIDTH * HEIGHT

    items.sort(key=lambda item: item.item_type)
    tot_page = math.ceil(len(items) / NUM)

    if (page < 1 or page > tot_page) and items != []:
        # invalid page
        return {"content": "그런 칸은 없어 :pleading_face:", "delete": False}

    items = items[(page - 1) * NUM : page * NUM]

    item_types = set([item.item_type for item in items])
    item_infos = dict(
        [(item_type, get.item_info(item_type)) for item_type in item_types]
    )
    item_types = set(
        [item_type for item_type in item_types if item_infos[item_type] is not None]
    )

    append_ellipsis = lambda t: t if len(t) < 9 else t[:7] + "…"
    get_text_scale = (
        lambda l: "1,0,0,1"
        if l < 5
        else "0.83, 0, 0, 0.87"
        if l < 7
        else "0.72, 0, 0, 0.82"
    )
    text_style = "font-family:Noto Sans CJK KR;font-style:normal;fill:#80745A;fill-opacity:1;stroke:#80745A;stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1"
    text_attr = 'dominant-baseline="middle" text-anchor="middle"'

    svg = image.render_svg(
        240 + WIDTH * 196,
        240 + HEIGHT * 196,
        defs=[
            image.get_image_def(
                f"{os.environ.get('ASSETS_PATH', '')}/items/{item_infos[item_type].image}"
            )
            for item_type in item_types
        ],
        inner=[
            # wrapper
            f"""<path d="{image.get_squircle_path(240 + WIDTH * 196, 240 + HEIGHT * 196, 120 + WIDTH * 98, 120 + HEIGHT * 98)}" fill="rgb(255,250,228)" />""",
            # pagination
            *(
                [
                    f"""<text style="font-size:48px;font-family:Noto Sans CJK KR;font-style:normal;fill:#80745A;fill-opacity:1;stroke:#80745A;stroke-width:2px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1" {text_attr} transform="matrix(1,0,0,1,{120 + WIDTH * 98},{HEIGHT * 196 + 160})">{page} / {tot_page}</text>"""
                ]
                if tot_page > 0
                else []
            ),
            # placeholders
            *[
                f"""<circle vector-effect="non-scaling-stroke" cx="{218 + (n % WIDTH) * 196}" cy="{218 + (n // WIDTH) * 196 - 30}" r="32" fill="rgb(237,226,202)" />"""
                for n in range(NUM)
                if n >= len(items)
            ],
            # item images
            *[
                image.use_image(
                    f"{os.environ.get('ASSETS_PATH', '')}/items/{item_infos[item.item_type].image}",
                    height=144,
                    tx=218 + (n % WIDTH) * 196,
                    ty=218 + (n // WIDTH) * 196 - 38,
                )
                for n, item in enumerate(items)
            ],
            # item labels
            *[
                f"""<text style="font-size:36px;{text_style}" {text_attr} transform="matrix({get_text_scale(len(
                    item_infos[item.item_type].alias.split("|")[0]
                ))},{218 + (n % WIDTH) * 196},{218 + (n // WIDTH) * 196 + 54})">{
                    append_ellipsis(item_infos[item.item_type].alias.split("|")[0])
                }</text>"""
                for n, item in enumerate(items)
            ],
            # the numbers of each item
            *[
                f"""<text style="font-size:64px;font-family:Noto Sans CJK KR;font-style:normal;fill:rgb(255,250,228);fill-opacity:1;stroke:rgb(255,250,228);stroke-width:20px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1" {text_attr} transform="matrix(1,0,0,1,{218 + (n % WIDTH) * 196 + 56},{218 + (n // WIDTH) * 196 - 6})">{
                    item.amount
                }</text>"""
                f"""<text style="font-size:64px;font-family:Noto Sans CJK KR;font-style:normal;fill:#80745A;fill-opacity:1;stroke:#80745A;stroke-width:3px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1" {text_attr} transform="matrix(1,0,0,1,{218 + (n % WIDTH) * 196 + 56},{218 + (n // WIDTH) * 196 - 6})">{
                    item.amount
                }</text>"""
                for n, item in enumerate(items)
            ],
        ],
    )

    content = (
        "가방이 비어 있어!"
        if tot_page == 0
        else ""
        if tot_page == 1
        else f"지금은 {page}번째 칸을 보고 있어. 다른 칸을 보고 싶으면 '돛 가방 (페이지 수)'로 알려줘!"
    )

    return {"content": content, "svg": svg, "delete": True}
