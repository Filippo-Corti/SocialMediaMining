import sqlite3
import networkx as nx
from typing import List

from ..objects.bluesky import BSAccount, BSPost


class SQLiteBlueSkySaver:

    def __init__(self, db_name: str = 'db/bluesky.db'):
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
            id TEXT PRIMARY KEY,
            author_id TEXT,
            in_reply_to_id TEXT,
            created_at TEXT,
            replies_count INTEGER,
            language TEXT,
            content TEXT,
            url TEXT,
            uri TEXT,
            FOREIGN KEY (author_id) REFERENCES Accounts(id)
        )''')

        self.conn.commit()

    def _insert_account(self, account : BSAccount) -> None:
        """Inserts Bluesky account into DB"""
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

    def insert_post(self, post : BSPost) -> None:
        """Inserts Bluesky post and author's account into DB"""
        try:
            self.cursor.execute(
                '''
                    INSERT INTO Posts (id, author_id, in_reply_to_id, created_at, replies_count, language, content, url, uri)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''',
                (
                    post.id,
                    post.author.id,
                    post.in_reply_to_id,
                    post.created_at,
                    post.replies_count,
                    post.language,
                    post.content,
                    post.url,
                    post.uri
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

    def get_post_by_id(self, post_id : str) -> BSPost:
        self.cursor.execute("SELECT * FROM Posts WHERE id = ?", (post_id,))
        post_row = self.cursor.fetchone()
        author_id = post_row[1]
        self.cursor.execute("SELECT * FROM Accounts WHERE id = ?", (author_id,))
        account_row = self.cursor.fetchone()
        return BSPost(
            id=post_row[0],
            author=BSAccount(
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
            url=post_row[7],
            uri=post_row[8]
        )

    def clear_database(self) -> None:
        """Deletes all rows from the database"""
        try:
            self.cursor.execute('DELETE FROM Posts')
            self.cursor.execute('DELETE FROM Accounts')
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")

    def extract_network(self) -> nx.Graph:
        """Returns the reply network, with all tracked attributes for nodes and edges"""
        self.cursor.execute("SELECT * FROM Posts")
        posts = {
            post_row[0]: post_row
            for post_row in self.cursor.fetchall()
        }
        self.cursor.execute("SELECT * FROM Accounts")
        accounts = {
            account_row[0]: account_row
            for account_row in self.cursor.fetchall()
        }

        edges = list()

        node_attributes = {}
        for account_id, account in accounts.items():
            node_attributes[account_id] = dict(
                id=account_id,
                username=account[1],
                display_name=account[2] if account[2] else "",
                url=account[3]
            )

        edge_attributes = {}
        for post_id, post in posts.items():
            replier_id = post[1]
            replied_to_post = post[2]

            if not replied_to_post or replied_to_post not in posts:
                continue

            replied_to_id = posts[replied_to_post][1]

            edge = (replier_id, replied_to_id)
            edges.append(edge)

            if edge not in edge_attributes:
                edge_attributes[edge] = dict()

            post_idx = len(edge_attributes[edge])

            edge_attributes[edge][f"post{post_idx}"] = dict(
                id=post_id,
                author_id=post[1],
                in_reply_to_id=post[2],
                created_at=post[3],
                replies_count=post[4],
                language=post[5] if post[5] else "",
                content=post[6],
                url=post[7],
                uri=post[8]
            )

        G = nx.from_edgelist(edges, create_using=nx.DiGraph())
        nx.set_node_attributes(G, node_attributes)
        nx.set_edge_attributes(G, edge_attributes)

        return G
