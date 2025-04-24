import time
import re
from typing import Generator, List

from googleapiclient.discovery import build

from ..objects.youtube import YTVideo, YTComment


class YoutubeApi:

    def __init__(self, api_key: str) -> None:
        self.youtube = build(
            serviceName="youtube",
            version="v3",
            developerKey=api_key
        )

    def search_videos(
            self,
            keyword: str,
            limit: int,
            published_after : str,
            published_before : str
    ) -> Generator[YTVideo, None, None]:
        """Returns the YouTube videos based on given params"""

        assert 0 < limit <= 50

        request = self.youtube.search().list(
            part="snippet",
            maxResults=limit,
            order="relevance",
            publishedAfter=published_after,
            publishedBefore=published_before,
            q=keyword,
            regionCode="US",
            relevanceLanguage="en",
            safeSearch="none",
            type="video"
        )
        response = request.execute()

        videos = response.get('items', list())

        for video in videos:
            yt_video = YTVideo.from_json(video)
            if yt_video:
                yield yt_video

    def get_video_by_id(self, video_id: str) -> YTVideo | None:
        """Returns a single YTVideo object given a video ID"""
        request = self.youtube.videos().list(
            part="snippet",
            id=video_id
        )
        response = request.execute()
        items = response.get('items', [])

        if not items:
            return None

        return YTVideo.from_json(items[0])

    def get_comments(
            self,
            video_id : str,
            threads_count : int
    ) -> Generator[YTComment, None, None]:
        """Returns all the comments and responses of the first threads_count threads of the given video"""
        top_level_comments : List[YTComment] = list()

        request = self.youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100,
            textFormat="plainText",
            order="relevance",
        )
        while request and len(top_level_comments) < threads_count:
            response = request.execute()
            time.sleep(0.1)
            for thread in response.get("items", list()):
                top_level_comment = YTComment.from_json(
                    json=thread['snippet']['topLevelComment'],
                    video_id=video_id,
                    in_reply_to_id=None
                )
                top_level_comments.append(top_level_comment)
            request = self.youtube.commentThreads().list_next(request, response)


        for top_level_comment in top_level_comments:
            yield top_level_comment

            latest_comment_id_per_author : dict[str, str] = dict()
            latest_comment_id_per_author[top_level_comment.author.display_name] = top_level_comment.id

            request = self.youtube.comments().list(
                part="snippet",
                parentId=top_level_comment.id,
                maxResults=100,
                textFormat="plainText"
            )
            while request:
                response = request.execute()
                time.sleep(0.1)
                for reply in response.get("items", list()):

                    in_reply_to_id = top_level_comment.id

                    mentions = re.findall(r'@(\w+)', reply['snippet']['textOriginal'])
                    if mentions:
                        mention = f"@{mentions[0]}"
                        for i in range(len(mention), 1, -1):
                            partial_mention = mention[:i]
                            if partial_mention in latest_comment_id_per_author:
                                in_reply_to_id = latest_comment_id_per_author[partial_mention]
                                break

                    reply_comment = YTComment.from_json(
                        json=reply,
                        video_id=video_id,
                        in_reply_to_id=in_reply_to_id,
                    )

                    latest_comment_id_per_author[reply_comment.author.display_name] = reply_comment.id

                    yield reply_comment

                request = self.youtube.comments().list_next(request, response)
