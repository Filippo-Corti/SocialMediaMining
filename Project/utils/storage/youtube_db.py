import sqlite3
from collections import defaultdict

import networkx as nx

from ..objects.youtube import YTVideo, YTAccount, YTComment, YTThreadTree


class SQLiteYoutubeSaver:

    def __init__(self, db_name: str = 'db/youtube.db'):
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
            FOREIGN KEY (author_id) REFERENCES Accounts(id),
            FOREIGN KEY (video_id) REFERENCES Videos(id)
        )''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS CommentAnalysis (
            id TEXT PRIMARY KEY,
            bias TEXT,
            leaning TEXT,
            is_political INTEGER,
            sentiment TEXT,
            emotion TEXT,
            llm_label TEXT,
            label INTEGER,
            FOREIGN KEY (id) REFERENCES Comments(id)
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
            pass

    def insert_comment_analysis(self, comment_id : int, **labels) -> None:
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

    def get_all_comments(self) -> list[YTComment]:
        self.cursor.execute(f"""SELECT * FROM Comments""")
        comment_rows = self.cursor.fetchall()

        self.cursor.execute("SELECT * FROM Accounts")
        accounts = {
            row[0]: YTAccount(id=row[0], display_name=row[1], url=row[2])
            for row in self.cursor.fetchall()
        }

        comments = list()

        for row in comment_rows:
            comment = YTComment(
                id=row[0],
                video_id=row[1],
                parent_id=row[2],
                author=accounts.get(row[3]),
                in_reply_to_id=row[4],
                created_at=row[5],
                content=row[6],
            )
            comments.append(comment)

        return comments


    def get_threads(self, video_ids: list[str] | None = None) -> list[YTThreadTree]:
        if not video_ids:
            self.cursor.execute("SELECT id FROM Videos")
            video_ids = [row[0] for row in self.cursor.fetchall()]

        placeholders = ",".join(["?"] * len(video_ids))
        self.cursor.execute(f"""
            SELECT * FROM Comments
            WHERE video_id IN ({placeholders})
        """, video_ids)
        comment_rows = self.cursor.fetchall()

        self.cursor.execute("SELECT * FROM Accounts")
        accounts = {
            row[0]: YTAccount(id=row[0], display_name=row[1], url=row[2])
            for row in self.cursor.fetchall()
        }

        comment_map = {}
        children_map = defaultdict(list)

        for row in comment_rows:
            comment = YTComment(
                id=row[0],
                video_id=row[1],
                parent_id=row[2],
                author=accounts.get(row[3]),
                in_reply_to_id=row[4],
                created_at=row[5],
                content=row[6],
            )
            comment_map[comment.id] = comment
            if comment.in_reply_to_id:
                children_map[comment.in_reply_to_id].append(comment)

        def build_tree(root: YTComment) -> YTThreadTree:
            return YTThreadTree(
                value=root,
                children=[build_tree(child) for child in children_map.get(root.id, [])]
            )

        roots = [c for c in comment_map.values() if not c.in_reply_to_id]
        return [build_tree(root) for root in roots]

    def extract_network(
            self,
            video_ids : list[str] | None = None
    ) -> nx.Graph:
        """Returns the reply network, with all tracked attributes for nodes and edges"""
        if not video_ids:
            self.cursor.execute("SELECT id from Videos")
            video_ids = [row[0] for row in self.cursor.fetchall()]

        placeholders = ",".join(["?"] * len(video_ids))
        self.cursor.execute(f"""
        SELECT * FROM Comments
        WHERE video_id IN ({placeholders})
        """, video_ids)
        comments = {
            comment_row[0]: comment_row
            for comment_row in self.cursor.fetchall()
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
                url=account[2],
                comments_count=0
            )

        edge_attributes = {}
        for comment_id, comment in comments.items():
            replier_id = comment[3]
            replied_to_post = comment[4]

            node_attributes[replier_id]['comments_count'] += 1

            if not replied_to_post or replied_to_post not in comments:
                continue

            replied_to_id = comments[replied_to_post][3]

            edge = (replier_id, replied_to_id)
            edges.append(edge)

            if edge not in edge_attributes:
                edge_attributes[edge] = dict()

            comment_idx = len(edge_attributes[edge])

            edge_attributes[edge][f"comment{comment_idx}"] = dict(
                id=comment_id,
                video_id=comment[1],
                parent_id=comment[2],
                author_id=comment[3],
                in_reply_to_id=comment[4],
                created_at=comment[5],
                content=comment[6],
            )

        G = nx.from_edgelist(edges, create_using=nx.DiGraph())
        nx.set_node_attributes(G, node_attributes)
        nx.set_edge_attributes(G, edge_attributes)

        return G

