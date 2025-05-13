from dataclasses import dataclass
from typing import Any

import networkx as nx


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

@dataclass
class YTThreadTree:
    value : YTComment
    children : list['YTThreadTree']

    def print(self, level: int = 0) -> None:
        indent = "  " * level
        author = self.value.author.display_name if self.value.author else "Unknown"
        print(f"{indent}- {author}: {self.value.content[:80]!r}")  # show up to 80 chars

        for child in self.children:
            YTThreadTree.print(child, level + 1)

    def convert_to_nxgraph(self) -> nx.Graph:
        G = nx.Graph()
        queue : list[YTThreadTree] = [self]
        while queue:
            curr = queue.pop(0)
            G.add_node(curr.value.id)
            for child in curr.children:
                G.add_edge(child.value.id, curr.value.id)
                queue.append(child)
        return G

    def get_size(self) -> int:
        """Returns the number of nodes in the tree"""
        return 1 + sum([child.get_size() for child in self.children])

    def get_unique_users(self) -> int:
        """Returns the number of unique users in the tree"""
        users = set()
        def list_users(node : YTThreadTree) -> None:
            users.add(node.value.author.id)
            for child in node.children:
                list_users(child)

        list_users(self)
        return len(users)


    def get_depth(self) -> int:
        """Returns the depth of the tree"""
        return 1 + max([child.get_depth() for child in self.children], default=0)

    def get_wiener_index(self) -> float:
        """Returns the wiener index of the tree (sum of shortest path lengths between each pair of nodes) """
        return nx.wiener_index(self.convert_to_nxgraph())

    def get_normalized_wiener_index(self) -> float:
        """Returns the normalized wiener index of the tree"""
        n = self.get_size()
        return 2 * self.get_wiener_index() / (n * (n - 1))

    def get_comments_per_user(self) -> float:
        return self.get_size() / self.get_unique_users()