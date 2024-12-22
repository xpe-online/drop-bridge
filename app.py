from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from database import init_db
import os

app = Flask(__name__)
token = 'chinoimomochat'

# 初始化数据库 (如果不存在)
init_db()

def get_db_connection():
        conn = sqlite3.connect('messages.db')
        conn.row_factory = sqlite3.Row  # 让查询结果像字典一样访问
        return conn

@app.route('/')
def index():
        conn = get_db_connection()
        messages = conn.execute('SELECT * FROM messages ORDER BY created_at DESC').fetchall()
        conn.close()
        return render_template('index.html', messages=messages)

@app.route('/add_message', methods=['POST'])
def add_message():
        username = request.form.get('username')
        content = request.form['content']
        key = request.form.get('key')

        if key != token:
            return 'Token is required', 400

        if not content:
            return 'Content is required', 400

        conn = get_db_connection()
        conn.execute('INSERT INTO messages (username, content) VALUES (?, ?)', (username, content))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))

# 在 Vercel 上部署时，需要使用 Vercel 提供的环境变量 PORT
if __name__ == '__main__':
        app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

