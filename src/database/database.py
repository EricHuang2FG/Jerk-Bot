import sqlite3

PATH: str = "src/database/"

"""CREATE TABLE messages (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   username TEXT,
                   content TEXT,
                   timestamp TEXT DEFAULT CURRENT_TIMESTAMP
                   )"""


def log_message(username: str, text: str) -> None:
    with sqlite3.connect(PATH + "history.db") as conn:
        cursor: sqlite3.Cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO messages (username, content) VALUES (?, ?)", (username, text)
        )

        conn.commit()
