"""书籍封面配置：slug、配色、展示文案。"""
from __future__ import annotations

BOOK_COVER_SPECS: list[dict[str, str | list[str]]] = [
    {
        "slug": "bei-tao-yan-de-yong-qi",
        "title": "被讨厌的勇气",
        "author": "岸见一郎",
        "colors": ["#c44536", "#e8a598"],
        "accent": "#fff8f0",
    },
    {
        "slug": "xiao-wang-zi",
        "title": "小王子",
        "author": "圣埃克苏佩里",
        "colors": ["#1b3a5f", "#4a90c2"],
        "accent": "#ffd166",
    },
    {
        "slug": "fei-bao-li-gou-tong",
        "title": "非暴力沟通",
        "author": "马歇尔·卢森堡",
        "colors": ["#6a4c93", "#c77dff"],
        "accent": "#f8f0ff",
    },
    {
        "slug": "yuan-ze",
        "title": "原则",
        "author": "瑞·达利欧",
        "colors": ["#14213d", "#fca311"],
        "accent": "#e5e5e5",
    },
    {
        "slug": "huo-zhe",
        "title": "活着",
        "author": "余华",
        "colors": ["#7f1d1d", "#b45309"],
        "accent": "#fef3c7",
    },
    {
        "slug": "zheng-mian-guan-jiao",
        "title": "正面管教",
        "author": "简·尼尔森",
        "colors": ["#2d6a4f", "#95d5b2"],
        "accent": "#fffbeb",
    },
    {
        "slug": "xin-liu",
        "title": "心流",
        "author": "米哈里",
        "colors": ["#0077b6", "#90e0ef"],
        "accent": "#ffffff",
    },
    {
        "slug": "jie-you-za-huo-dian",
        "title": "解忧杂货店",
        "author": "东野圭吾",
        "colors": ["#bc6c25", "#dda15e"],
        "accent": "#fff1e6",
    },
    {
        "slug": "shen-du-gong-zuo",
        "title": "深度工作",
        "author": "卡尔·纽波特",
        "colors": ["#03045e", "#48cae4"],
        "accent": "#caf0f8",
    },
    {
        "slug": "wo-men-sa",
        "title": "我们仨",
        "author": "杨绛",
        "colors": ["#9d8189", "#f4acb7"],
        "accent": "#fff5f7",
    },
]

TITLE_TO_COVER: dict[str, str] = {
    spec["title"]: f"/placeholders/books/{spec['slug']}.svg" for spec in BOOK_COVER_SPECS
}


def cover_path_by_title(title: str, fallback_id: int = 1) -> str:
    if title in TITLE_TO_COVER:
        return TITLE_TO_COVER[title]
    idx = ((fallback_id - 1) % len(BOOK_COVER_SPECS)) + 1
    return f"/placeholders/books/{BOOK_COVER_SPECS[idx - 1]['slug']}.svg"
