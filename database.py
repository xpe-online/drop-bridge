import sqlite3

def init_db():
        conn = sqlite3.connect('messages.db')
        cursor = conn.cursor()
        cursor.execute("""
                        CREATE TABLE IF NOT EXISTS messages (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                username TEXT,
                                                            content TEXT,
                                                                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                                                                )
                                                                                    """)

        conn.commit()
        conn.close()

        if __name__ == '__main__':
                init_db()

