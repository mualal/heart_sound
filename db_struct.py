import sqlite3


class Database:
    def __init__(self, db):
        self.conn = sqlite3.connect(db)
        self.cur = self.conn.cursor()
        self.cur.execute("CREATE TABLE IF NOT EXISTS rhythms (id INTEGER PRIMARY KEY, name text, filepath text)")
        self.conn.commit()

    def fetch(self):
        self.cur.execute("SELECT * FROM rhythms")
        rows = self.cur.fetchall()
        return rows

    def insert(self, name, file_path):
        self.cur.execute("INSERT INTO rhythms VALUES (NULL, ?, ?)", (name, file_path))
        self.conn.commit()

    def remove(self, id):
        self.cur.execute("DELETE FROM rhythms WHERE id=?", (id,))
        self.conn.commit()

    def update(self, id, name, file_path):
        self.cur.execute("UPDATE rhythms SET name = ?, file_path = ? WHERE id = ?", (name, file_path, id))
        self.conn.commit()

    def __del__(self):
        self.conn.close()


db = Database('heart_rhythms.db')
