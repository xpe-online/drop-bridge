from flask import Flask, request, render_template_string
from datetime import datetime
from vercel_blob import put, get
import json
import os
from html import escape  # 导入 escape 函数

app = Flask(__name__)
token = 'chinoimomochat'

# 留言存储的文件名
MESSAGES_BLOB_JSON = 'messages.json'

async def load_messages():
    """从 Blob Storage 加载留言"""
    try:
        blob = await get(MESSAGES_BLOB_JSON)
        if blob:
            messages = json.loads(blob.content)
        else:
            messages = []
    except Exception as e:
        print(f"Error loading messages: {e}")
        messages = []
    return messages

async def save_messages(messages):
    """将留言保存到 Blob Storage"""
    try:
        await put(MESSAGES_BLOB_JSON, json.dumps(messages), content_type='application/json', access='public') # access 设置为 public 才能公开访问
    except Exception as e:
        print(f"Error saving messages: {e}")

@app.route('/')
async def index():  # 将 index 函数改为异步函数
    """显示留言板首页"""
    messages = await load_messages()
    messages_html = ""
    for message in reversed(messages):
        messages_html += f"<p><b>{escape(message['username'])}</b>: {escape(message['content'])} <i>({message['timestamp']})</i></p>"

    form = '''
    <form method="POST" action="/add_message">
        <label for="username">用户名:</label><br>
        <input type="text" id="username" name="username"><br>
        <label for="content">留言内容:</label><br>
        <textarea id="content" name="content"></textarea><br>
        <input type="submit" value="提交">
    </form>
    '''
    return render_template_string(f"<h1>留言板</h1>{messages_html}{form}")
    

@app.route('/add_message', methods=['POST'])
async def add_message(): # 将 add_message 函数改为异步函数
    """添加新留言"""
    username = request.form['username']
    content = request.form['content']
    key = request.form['key']
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if not username or not content:
        return 'Invalid input', 400
    
    if key != token:
            return 'Invalid input', 400

    messages = await load_messages()
    messages.append({'username': username, 'content': content, 'timestamp': timestamp})
    await save_messages(messages)

    return '''
        <script>
            alert('留言已添加！');
            window.location.href = '/';
        </script>
    '''

if __name__ == '__main__':
    app.run(debug=True)
