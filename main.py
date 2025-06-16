from flask import Flask, request, redirect
import uuid
import os

app = Flask(__name__)
db = {}  # В памяти (можно заменить на Redis)

@app.route('/')
def index():
    return '''
        <h2>Одноразовый сокращатель ссылок</h2>
        <form method="POST" action="/create">
            <input name="url" placeholder="Вставь ссылку" required>
            <button type="submit">Сократить</button>
        </form>
    '''

@app.route('/create', methods=['POST'])
def create():
    url = request.form.get('url')
    token = str(uuid.uuid4())[:8]
    db[token] = url
    host = request.host_url
    return f'Вот ваша одноразовая ссылка: <a href="{host}{token}">{host}{token}</a>'

@app.route('/<token>')
def redirect_once(token):
    if token not in db:
        return 'Ссылка уже использована или недействительна.', 404
    link = db.pop(token)
    return redirect(link)
