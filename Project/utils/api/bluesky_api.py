import time
import random
from typing import Generator

from atproto import Client

from ..objects.bluesky import BSPost


class BlueSkyApi:

    def __init__(self, username: str, password: str) -> None:
        self.client = Client()
        self.client.login(
            login=username,
            password=password
        )

    def search_posts(
            self,
            keyword: str,
            limit: int,
            starting_offset: int = 0
    ) -> Generator[BSPost, None, None]:
        """Returns the latest posts associated with the given keyword"""
        offset = starting_offset
        count = 0
        while limit > count:
            result = self.client.app.bsky.feed.search_posts(
                params=dict(
                    q=keyword,
                    sort="top",
                    limit=100,
                    cursor=f"{offset}",
                )
            )

            posts = result.posts
            offset = result.cursor

            for post in posts:
                bs_post = BSPost.from_post_view(post)
                if bs_post:
                    yield bs_post
                count += 1
                if count > limit:
                    break

            sleep_time = random.randrange(start=1, stop=5)
            time.sleep(sleep_time)

    def get_comments(
            self,
            post_uri: str
    ) -> Generator[BSPost, None, None]:
        """Returns all the comments of the given post"""
        thread = self.client.app.bsky.feed.get_post_thread(
            params=dict(
                uri=post_uri,
                depth=1000,
                parent_height=1000,
            )
        )
        replies = thread.thread.replies
        for reply in replies:
            bs_post = BSPost.from_post_view(reply.post)
            if bs_post:
                yield bs_post