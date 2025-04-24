import sqlite3
from typing import List

from ..objects.truthsocial import TSAccount, TSPost


class SQLiteTruthSaver:

    def __init__(self, db_name: str = 'truthsocial.db'):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def close(self):
        self.conn.close()

    def _create_tables(self):

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Accounts (
            id TEXT PRIMARY KEY,
            username TEXT,
            display_name TEXT,
            url TEXT
        )''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Posts (
            id INTEGER PRIMARY KEY,
            author_id TEXT,
            in_reply_to_id TEXT,
            created_at TEXT,
            replies_count INTEGER,
            language TEXT,
            content TEXT,
            url TEXT,
            FOREIGN KEY (author_id) REFERENCES Accounts(id)
        )''')

        self.conn.commit()

    def _insert_account(self, account : TSAccount) -> None:
        """Inserts TruthSocial account into DB"""
        try:
            self.cursor.execute(
                '''
                    INSERT INTO Accounts (id, username, display_name, url)
                    VALUES (?, ?, ?, ?)
                    ''',
                (
                    account.id,
                    account.username,
                    account.display_name,
                    account.url
                )
            )
        except sqlite3.Error as e:
            pass

    def insert_post(self, post : TSPost) -> None:
        """Inserts TruthSocial post and author's account into DB"""
        try:
            self.cursor.execute(
                '''
                    INSERT INTO Posts (id, author_id, in_reply_to_id, created_at, replies_count, language, content, url)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''',
                (
                    post.id,
                    post.author.id,
                    post.in_reply_to_id,
                    post.created_at,
                    post.replies_count,
                    post.language,
                    post.content,
                    post.url
                )
            )
            self._insert_account(post.author)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")

    def get_all_post_ids(self) -> List[str]:
        self.cursor.execute("SELECT id FROM Posts")
        rows = self.cursor.fetchall()
        return [row[0] for row in rows]

    def get_post_by_id(self, post_id : str) -> TSPost:
        self.cursor.execute("SELECT * FROM Posts WHERE id = ?", (post_id,))
        post_row = self.cursor.fetchone()
        author_id = post_row[1]
        self.cursor.execute("SELECT * FROM Accounts WHERE id = ?", (author_id,))
        account_row = self.cursor.fetchone()
        return TSPost(
            id=post_row[0],
            author=TSAccount(
                id=account_row[0],
                username=account_row[1],
                display_name=account_row[2],
                url=account_row[3]
            ),
            in_reply_to_id=post_row[2],
            created_at=post_row[3],
            replies_count=post_row[4],
            language=post_row[5],
            content=post_row[6],
            url=post_row[7]
        )

    def clear_database(self) -> None:
        """Deletes all rows from the database"""
        try:
            self.cursor.execute('DELETE FROM Posts')
            self.cursor.execute('DELETE FROM Accounts')
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
