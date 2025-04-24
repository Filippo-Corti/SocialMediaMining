from dataclasses import dataclass
from typing import List


@dataclass
class YTComment:
    id: str
    author_id: str
    author_name: str
    content: str
    date: str
    like_count: int


@dataclass
class YTThread:
    video_id: str
    reply_count: int
    top_level_comment: YTComment
    replies: List[YTComment]
