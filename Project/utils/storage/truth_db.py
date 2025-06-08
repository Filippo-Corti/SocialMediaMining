import sqlite3

import networkx as nx
from typing import List

from ..objects.truthsocial import TSAccount, TSPost


class SQLiteTruthSaver:

    def __init__(self, db_name: str = 'db/truthsocial.db'):
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
            in_reply_to_id INTEGER,
            created_at TEXT,
            replies_count INTEGER,
            language TEXT,
            content TEXT,
            url TEXT,
            FOREIGN KEY (author_id) REFERENCES Accounts(id)
        )''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS CommentAnalysis (
            id INTEGER PRIMARY KEY,
            gemini_label TEXT,
            label TEXT,
            FOREIGN KEY (id) REFERENCES Posts(id)
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

    def insert_comment_analysis(self, comment_id : str, **labels) -> None:
        """Inserts or updates the comment analysis labels for the given comment"""
        # Prepare columns and values
        columns = list(labels.keys())
        values = [labels[col] for col in columns]

        # Check if the row already exists
        self.cursor.execute("SELECT id FROM CommentAnalysis WHERE id = ?", (comment_id,))
        exists = self.cursor.fetchone() is not None

        if exists:
            # UPDATE path
            set_clause = ", ".join([f"{col} = ?" for col in columns])
            sql = f"UPDATE CommentAnalysis SET {set_clause} WHERE id = ?"
            self.cursor.execute(sql, values + [comment_id])
        else:
            # INSERT path
            all_columns = ["id"] + columns
            placeholders = ", ".join(["?"] * len(all_columns))
            sql = f"INSERT INTO CommentAnalysis ({', '.join(all_columns)}) VALUES ({placeholders})"
            self.cursor.execute(sql, [comment_id] + values)

        self.conn.commit()

    def get_all_post_ids(self) -> List[str]:
        self.cursor.execute("SELECT id FROM Posts")
        rows = self.cursor.fetchall()
        return [row[0] for row in rows]

    def get_all_posts(self) -> List[TSPost]:
        self.cursor.execute("SELECT * FROM Posts LEFT JOIN CommentAnalysis ON Posts.id = CommentAnalysis.id WHERE gemini_label IS NULL")
        post_rows = self.cursor.fetchall()

        self.cursor.execute("SELECT * FROM Accounts")
        accounts = {
            row[0]: TSAccount(id=row[0], username=row[1], display_name=row[2], url=row[3])
            for row in self.cursor.fetchall()
        }

        posts = list()

        for row in post_rows:
            comment = TSPost(
                id=row[0],
                author=accounts.get(row[1]),
                in_reply_to_id=row[2],
                created_at=row[3],
                replies_count=row[4],
                language=row[5],
                content=row[6],
                url=row[7],
            )
            posts.append(comment)

        return posts

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

    def extract_network(self, top_k : int | None = None) -> nx.Graph:
        """Returns the reply network, with all tracked attributes for nodes and edges"""
        if not top_k:
            self.cursor.execute("SELECT * FROM Posts")
        else:
            self.cursor.execute("""
            SELECT * FROM Posts 
            WHERE author_id IN (
                SELECT author_id FROM Posts 
                GROUP BY author_id 
                ORDER BY COUNT(*) DESC
                LIMIT (?)
            )
            """, (top_k,))
        posts = {
            post_row[0]: post_row
            for post_row in self.cursor.fetchall()
        }
        self.cursor.execute("SELECT * FROM Accounts")
        accounts = {
            account_row[0]: account_row
            for account_row in self.cursor.fetchall()
        }

        self.cursor.execute("""
            SELECT
                C.author_id,
                AVG(CA.label) AS avg_label
            FROM Posts C
            JOIN CommentAnalysis CA ON C.id = CA.id
            GROUP BY C.author_id
        """)
        accounts_stance = {
            account_row[0]: account_row[1]
            for account_row in self.cursor.fetchall()
        }


        edges = list()

        node_attributes = {}
        for account_id, account in accounts.items():
            node_attributes[account_id] = dict(
                id=account_id,
                username=account[1],
                display_name=account[2],
                url=account[3],
                posts_count=0,
                average_stance=accounts_stance.get(account_id, 0)
            )

        edge_attributes = {}
        for post_id, post in posts.items():
            replier_id = post[1]
            replied_to_post = post[2]

            node_attributes[replier_id]['posts_count'] += 1

            if not replied_to_post:
                continue

            if int(replied_to_post) not in posts:
                continue

            replied_to_id = posts[int(replied_to_post)][1]

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
                language=post[5],
                content=post[6],
                url=post[7]
            )

        G = nx.from_edgelist(edges, create_using=nx.DiGraph())
        nx.set_node_attributes(G, node_attributes)
        nx.set_edge_attributes(G, edge_attributes)

        return G

