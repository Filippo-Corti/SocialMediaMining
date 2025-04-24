from dataclasses import dataclass

from atproto_client.models.app.bsky.actor.defs import ProfileViewBasic
from atproto_client.models.app.bsky.feed.defs import PostView


@dataclass
class BSAccount:
    id : str
    username : str
    display_name : str
    url : str

    @staticmethod
    def from_profile_view(profile : ProfileViewBasic):
        try:
            bs_account = BSAccount(
                id=profile.did,
                username=profile.handle,
                display_name=profile.display_name,
                url=f"https://bsky.app/profile/{profile.handle}",
            )
            return bs_account
        except:
            return None

@dataclass
class BSPost:
    id : str
    author : BSAccount
    in_reply_to_id : str | None
    created_at : str
    replies_count : int
    language : str
    content : str
    url : str
    uri : str

    @staticmethod
    def from_post_view(post : PostView):
        try:
            bs_post = BSPost(
                id=post.cid,
                author=BSAccount.from_profile_view(post.author),
                in_reply_to_id=post.record.reply.parent.cid if post.record.reply else None,
                created_at=post.record.created_at,
                replies_count=post.reply_count,
                language=post.record.langs[0] if post.record.langs else None,
                content=post.record.text,
                url=f"https://bsky.app/profile/{post.author.handle}/post/{post.uri.split("/")[-1]}",
                uri=post.uri,
            )
            return bs_post
        except:
            return None


