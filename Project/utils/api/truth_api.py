import math
import time
import random
from typing import Generator

from truthbrush import Api

from ..objects.truthsocial import TSPost


class TruthApi:

    def __init__(self, username : str, password : str) -> None:
        self.client = Api(
            username=username,
            password=password
        )

    def search_posts(
            self,
            keyword : str,
            limit : int,
            starting_max_id : str | None = None
    ) -> Generator[TSPost, None, None]:
        """Returns the latest posts associated with the given keyword"""
        max_id = starting_max_id
        count = 0
        while limit > count:
            json = self.client.search(
                searchtype="statuses",
                query=keyword,
                max_id=max_id,
            )

            json = list(json)

            if len(json) == 0:
                break

            posts = json[0].get('statuses', list())
            max_id = min((post.get('id', math.inf) for post in posts))

            for post in posts:
                ts_post = TSPost.from_json(post)
                if ts_post:
                    yield ts_post
                count+=1
                if count > limit:
                    break

            sleep_time = random.randrange(start=15, stop=60)
            time.sleep(sleep_time)

    def get_comments(
            self,
            post_id : str
    ) -> Generator[TSPost, None, None]:
        """Returns all the comments of the given post"""
        for post in self.client.pull_comments(
            post=f"{post_id}",
            include_all=True
        ):
            ts_post = TSPost.from_json(post)
            if ts_post:
                yield ts_post
