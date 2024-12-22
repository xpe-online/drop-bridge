from flask import Flask, request, render_template_string
from datetime import datetime
import requests
import json
import os
from html import escape

app = Flask(__name__)
token = 'chinoimomochat'

# 留言存储的文件名
MESSAGES_BLOB_JSON = 'messages.json'
# Vercel Blob Storage 的 URL 和 Token (请替换成你自己的)
BLOB_STORE_URL = os.environ.get("BLOB_STORE_URL")
BLOB_STORE_TOKEN = os.environ.get("BLOB_READ_WRITE_TOKEN")

def get_blob_headers():
    """获取请求 Blob Storage 的 Headers"""
    return {
        'Authorization': f'Bearer {BLOB_STORE_TOKEN}',
        'Content-Type': 'application/json',
    }

def load_messages():
    """从 Blob Storage 加载留言"""
    try:
        response = requests.get(f'{BLOB_STORE_URL}/{MESSAGES_BLOB_JSON}', headers=get_blob_headers())
        response.raise_for_status()  # 检查 HTTP 状态码
        messages = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error loading messages: {e}")
        messages = []
    return messages

def save_messages(messages):
    """将留言保存到 Blob Storage"""
    try:
        response = requests.put(f'{BLOB_STORE_URL}/{MESSAGES_BLOB_JSON}', headers=get_blob_headers(), data=json.dumps(messages))
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error saving messages: {e}")

@app.route('/')
def index():
    """显示留言板首页"""
    messages = load_messages()
    messages_html = ""
    for message in reversed(messages):
        messages_html += f"<p><b>{escape(message['username'])}</b>: {escape(message['content'])} <i>({message['timestamp']})</i></p>"

    form = '''
    <form method="POST" action="/add_message">
        <label for="username">用户名:</label><br>
        <input type="text" id="username" name="username"><br>
        <label for="content">留言内容:</label><br>
        <textarea id="content" name="content"></textarea><br>
        <label for="username">密钥:</label><br>
        <input type="text" id="key" name="key"><br>
        <input type="submit" value="提交">
    </form>
    '''
    return render_template_string(f"<h1>留言板</h1>{messages_html}{form}")

@app.route('/add_message', methods=['POST'])
def add_message():
    """添加新留言"""
    username = request.form['username']
    content = request.form['content']
    key = request.form['key']
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if not username or not content:
        return 'Invalid input', 400

    if key != token:
        return 'Invalid token', 400

    messages = load_messages()
    messages.append({'username': username, 'content': content, 'timestamp': timestamp})
    save_messages(messages)

    return '''
        <script>
            alert('留言已添加！');
            window.location.href = '/';
        </script>
    '''

if __name__ == '__main__':
    app.run(debug=True)
