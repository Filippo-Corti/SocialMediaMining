import sqlite3
from typing import List

from ..objects.youtube import YTVideo, YTAccount, YTComment

class SQLiteYoutubeSaver:

    def __init__(self, db_name: str = 'youtube.db'):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self._create_table()

    def close(self):
        self.conn.close()

    def _create_table(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Videos (
            id TEXT PRIMARY KEY,
            channel_title TEXT,
            title TEXT,
            url TEXT
        )''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Accounts (
            id TEXT PRIMARY KEY,
            display_name TEXT,
            url TEXT
        )''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Comments (
            id TEXT PRIMARY KEY,
            video_id TEXT,
            parent_id TEXT,
            author_id TEXT,
            in_reply_to_id TEXT,
            created_at TEXT,
            content TEXT,
            FOREIGN KEY (author_id) REFERENCES Accounts(id)
        )''')

        self.conn.commit()

    def insert_video(self, video : YTVideo) -> None:
        """Inserts YT video into DB"""
        try:
            self.cursor.execute(
                '''
                    INSERT INTO Videos (id, channel_title, title, url)
                    VALUES (?, ?, ?, ?)
                    ''',
                (
                    video.id,
                    video.channel_title,
                    video.title,
                    video.url
                )
            )
            self.conn.commit()
        except sqlite3.Error as e:
            pass

    def _insert_account(self, account : YTAccount) -> None:
        """Inserts YT account into DB"""
        try:
            self.cursor.execute(
                '''
                    INSERT INTO Accounts (id, display_name, url)
                    VALUES (?, ?, ?)
                    ''',
                (
                    account.id,
                    account.display_name,
                    account.url
                )
            )
        except sqlite3.Error as e:
            pass

    def insert_comment(self, comment : YTComment) -> None:
        """Inserts YT comment and author's account into DB"""
        try:
            self.cursor.execute(
                '''
                    INSERT INTO Comments (id, video_id, parent_id, author_id, in_reply_to_id, created_at, content)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''',
                (
                    comment.id,
                    comment.video_id,
                    comment.parent_id,
                    comment.author.id,
                    comment.in_reply_to_id,
                    comment.created_at,
                    comment.content
                )
            )
            self._insert_account(comment.author)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")