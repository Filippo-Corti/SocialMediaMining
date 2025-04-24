from dataclasses import dataclass
from typing import Any

@dataclass
class YTVideo:
    id : str
    channel_title : str
    title : str
    url : str

    @staticmethod
    def from_json(json: dict[str, Any]): # Json is a searchResult or a video
        try:
            video_id = json['id'] if json['kind'] == "youtube#video" else json['id']['videoId']
            video = YTVideo(
                id=video_id,
                channel_title = json['snippet']['channelTitle'],
                title = json['snippet']['title'],
                url=f"https://www.youtube.com/watch?v={video_id}",
            )
            return video
        except:
            return None

@dataclass
class YTAccount:
    id : str
    display_name : str
    url : str

    @staticmethod
    def from_json(json: dict[str, Any]): # Json is a comment
        try:
            account = YTAccount(
                id=json['snippet']['authorChannelId']['value'],
                display_name=json['snippet']['authorDisplayName'],
                url=json['snippet']['authorChannelUrl']
            )
            return account
        except Exception as e:
            return None

@dataclass
class YTComment:
    id : str
    video_id : str
    parent_id : str # The top level comment of the thread (it may be itself)
    author : YTAccount
    in_reply_to_id : str | None # The comment it's replying to (could be the parent_id or could be a different one)
    created_at : str
    content : str

    @staticmethod
    def from_json(json : dict[str, Any], video_id : str, in_reply_to_id : str | None = None): # json is a comment
        try:
            comment = YTComment(
                id=json['id'],
                video_id=video_id,
                parent_id=json['snippet'].get('parentId', json['id']),
                author=YTAccount.from_json(json),
                in_reply_to_id=in_reply_to_id,
                created_at=json['snippet']['updatedAt'],
                content=json['snippet']['textDisplay']
            )
            return comment
        except Exception as e:
            print(f"Failed to translate into YTComment: {e} ")
            return None

