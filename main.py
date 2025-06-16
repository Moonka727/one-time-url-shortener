from flask import Flask, request, redirect, render_template_string
import uuid
import json
import os

app = Flask(__name__)
DB_FILE = 'db.json'

# Загружаем базу из файла или создаем пустую
if os.path.exists(DB_FILE):
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        db = json.load(f)
else:
    db = {}

def save_db():
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

# HTML с Tailwind, стилями и JS в одном шаблоне
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8" />
  <title>Одноразовый сокращатель ссылок</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    body {
      background-color: #1a1a2e; /* Dark background */
    }
    .bg-white {
      background-color: #2e2e3a; /* Darker card background */
      box-shadow: 0 0 20px rgba(128, 0, 128, 0.5); /* Purple glow */
    }
    .bg-blue-500 {
      background-color: #6f2c91; /* Purple button */
    }
    .bg-blue-600 {
      background-color: #7a4bba; /* Darker purple on hover */
    }
    .text-blue-600 {
      color: #9a4fba; /* Lighter purple for links */
    }
    .text-green-600 {
      color: #00ff7f; /* Bright green for active status */
    }
    .text-red-600 {
      color: #ff4d4d; /* Bright red for used status */
    }
    .bg-green-100 {
      background-color: rgba(0, 255, 127, 0.1); /* Light green background */
    }
    .bg-red-100 {
      background-color: rgba(255, 77, 77, 0.1); /* Light red background */
    }
    h1, h2 {
      text-shadow: 0 0 10px rgba(128, 0, 128, 0.7); /* Glowing text */
    }
    input {
      transition: all 0.3s ease;
    }
    input:focus {
      outline: none;
      box-shadow: 0 0 5px rgba(128, 0, 128, 0.7); /* Input glow on focus */
    }
  </style>
</head>
<body class="min-h-screen flex items-center justify-center">
  <div class="bg-white p-6 rounded shadow-md w-full max-w-lg text-center">
    <h1 class="text-2xl font-bold mb-4">🔗 Одноразовый сокращатель ссылок</h1>
    <form method="POST" action="/create" class="flex flex-col gap-3" id="linkForm">
      <input name="url" placeholder="Вставьте ссылку" required class="p-2 border rounded w-full" />
      <button type="submit" class="bg-blue-500 text-white py-2 rounded hover:bg-blue-600">Создать</button>
    </form>

    {% if result %}
      <div class="mt-4 p-3 bg-green-100 text-green-800 rounded break-words">
        ✅ Ваша ссылка: <a class="underline text-blue-600" href="{{ result }}">{{ result }}</a>
      </div>
    {% endif %}

    {% if error %}
      <div class="mt-4 p-3 bg-red-100 text-red-800 rounded">
        ⚠️ {{ error }}
      </div>
    {% endif %}
    
    <div class="mt-6">
      <h2 class="text-lg font-semibold">Как это работает:</h2>
      <p class="text-gray-300 mt-2">1. Вставьте ссылку в поле выше.</p>
      <p class="text-gray-300">2. Нажмите "Создать", чтобы получить сокращенную ссылку.</p>
      <p class="text-gray-300">3. Используйте сокращенную ссылку, пока она активна!</p>
    </div>
  </div>

  <script>
    document.getElementById('linkForm').addEventListener('submit', function(event) {
      const url = this.url.value.trim();
      if (!url.startsWith('http://') && !url.startsWith('https://')) {
        event.preventDefault();
        alert('Пожалуйста, вставьте полный URL, начинающийся с http:// или https://');
      }
    });
  </script>
</body>
</html>
'''

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_TEMPLATE, result=None, error=None)

@app.route('/create', methods=['POST'])
def create():
    url = request.form.get('url')
    if not url:
        return render_template_string(HTML_TEMPLATE, error="Введите корректную ссылку.", result=None)
    token = str(uuid.uuid4())[:8]
    db[token] = {"url": url, "used": False}
    save_db()
    short_url = request.host_url + token
    return render_template_string(HTML_TEMPLATE, result=short_url, error=None)

@app.route('/<token>')
def follow(token):
    if token not in db:
        return render_template_string(HTML_TEMPLATE, error="Ссылка не найдена.", result=None)
    if db[token]['used']:
        return render_template_string(HTML_TEMPLATE, error="Ссылка уже использована.", result=None)
    db[token]['used'] = True
    save_db()
    return redirect(db[token]['url'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
