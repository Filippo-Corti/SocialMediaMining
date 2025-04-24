from dataclasses import dataclass
from typing import Any

@dataclass
class TSAccount:
    id : str
    username : str
    display_name : str
    url : str

    @staticmethod
    def from_json(json: dict[str, Any]):
        try:
            account = json['account']
            ts_account = TSAccount(
                id=account['id'],
                username=account['username'],
                display_name=account['display_name'],
                url=account['url'],
            )
            return ts_account
        except:
            return None

@dataclass
class TSPost:
    id : str
    author : TSAccount
    in_reply_to_id : str | None
    created_at : str
    replies_count : int
    language : str
    content : str
    url : str

    @staticmethod
    def from_json(json : dict[str, Any]):
        try:
            post = TSPost(
                id=json['id'],
                author=TSAccount.from_json(json),
                in_reply_to_id=json['in_reply_to_id'],
                created_at=json['created_at'],
                replies_count=json['replies_count'],
                language=json['language'],
                content=json['content'],
                url=json['url'],
            )
            return post
        except:
            return None


