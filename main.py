from flask import Flask, request, redirect, render_template_string
import uuid
import json
import os

app = Flask(__name__)
DB_FILE = 'db.json'

if os.path.exists(DB_FILE):
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        db = json.load(f)
else:
    db = {}

def save_db():
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

# Мультиязычные тексты
LANGS = {
    'en': {
        'title': 'One-Time URL Shortener',
        'placeholder': 'Paste your URL',
        'create_btn': 'Create',
        'how_it_works': 'How it works:',
        'step1': '1. Paste the link above.',
        'step2': '2. Click "Create" to get a shortened link.',
        'step3': '3. Use the shortened link while it is active!',
        'url_label': 'Your link:',
        'error_input': 'Please enter a valid URL.',
        'error_not_found': 'Link not found.',
        'error_used': 'Link already used.',
        'alert_invalid_url': 'Please enter a full URL starting with http:// or https://',
        'lang_name': {'en': 'English', 'ru': 'Русский', 'az': 'Azərbaycan'},
    },
    'ru': {
        'title': 'Одноразовый сокращатель ссылок',
        'placeholder': 'Вставьте ссылку',
        'create_btn': 'Создать',
        'how_it_works': 'Как это работает:',
        'step1': '1. Вставьте ссылку в поле выше.',
        'step2': '2. Нажмите "Создать", чтобы получить сокращенную ссылку.',
        'step3': '3. Используйте сокращенную ссылку, пока она активна!',
        'url_label': 'Ваша ссылка:',
        'error_input': 'Введите корректную ссылку.',
        'error_not_found': 'Ссылка не найдена.',
        'error_used': 'Ссылка уже использована.',
        'alert_invalid_url': 'Пожалуйста, вставьте полный URL, начинающийся с http:// или https://',
        'lang_name': {'en': 'English', 'ru': 'Русский', 'az': 'Azərbaycan'},
    },
    'az': {
        'title': 'Bir dəfəlik URL qısaldıcı',
        'placeholder': 'Linki yapışdırın',
        'create_btn': 'Yarat',
        'how_it_works': 'Necə işləyir:',
        'step1': '1. Yuxarıdakı linki yapışdırın.',
        'step2': '2. Qısaldılmış link almaq üçün "Yarat" düyməsini basın.',
        'step3': '3. Qısaldılmış link aktiv olduqda istifadə edin!',
        'url_label': 'Sizin linkiniz:',
        'error_input': 'Düzgün link daxil edin.',
        'error_not_found': 'Link tapılmadı.',
        'error_used': 'Link artıq istifadə olunub.',
        'alert_invalid_url': 'Zəhmət olmasa, http:// və ya https:// ilə başlayan tam URL daxil edin',
        'lang_name': {'en': 'English', 'ru': 'Русский', 'az': 'Azərbaycan'},
    },
}

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="{{ lang }}">
<head>
  <meta charset="UTF-8" />
  <title>{{ texts.title }}</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    body {
      background-color: #121212;
      color: #ffffff;
      font-family: 'Arial', sans-serif;
    }
    .bg-card {
      background-color: #1e1e1e;
      border-radius: 0.5rem;
      box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
    }
    .bg-primary {
      background-color: #6f2c91;
    }
    .bg-primary-hover {
      background-color: #7a4bba;
    }
    .text-primary {
      color: #9a4fba;
    }
    .text-success {
      color: #00ff7f;
    }
    .text-danger {
      color: #ff4d4d;
    }
    .bg-success {
      background-color: rgba(0, 255, 127, 0.1);
      color: #00ff7f;
    }
    .bg-danger {
      background-color: rgba(255, 77, 77, 0.1);
      color: #ff4d4d;
    }
    h1, h2 {
      margin-bottom: 1rem;
    }
    input, select {
      transition: all 0.3s ease;
      background-color: #222222;
      border: 1px solid #555555;
      color: #ffffff;
      padding: 0.5rem;
      border-radius: 0.25rem;
    }
    input:focus, select:focus {
      outline: none;
      border-color: #6f2c91;
    }
    button {
      transition: background-color 0.3s ease;
    }
    button:hover {
      background-color: #7a4bba;
    }
  </style>
</head>
<body class="min-h-screen flex items-center justify-center">
  <div class="bg-card p-6 w-full max-w-lg text-center">
    <h1 class="text-2xl font-bold">🔗 {{ texts.title }}</h1>

    <form method="POST" action="/create?lang={{ lang }}" class="flex flex-col gap-3" id="linkForm">
      <input name="url" placeholder="{{ texts.placeholder }}" required class="w-full" />
      <button type="submit" class="bg-primary text-white py-2 rounded">{{ texts.create_btn }}</button>
    </form>

    <div class="mt-4">
      <label for="language-select" class="mr-2 font-semibold">🌐 Language:</label>
      <select id="language-select" name="language-select" onchange="changeLanguage()">
        {% for code, name in texts.lang_name.items() %}
          <option value="{{ code }}" {% if code == lang %}selected{% endif %}>{{ name }}</option>
        {% endfor %}
      </select>
    </div>

    {% if result %}
      <div class="mt-4 p-3 bg-success rounded break-words">
        ✅ {{ texts.url_label }} <a class="underline text-primary" href="{{ result }}">{{ result }}</a>
      </div>
    {% endif %}

    {% if error %}
      <div class="mt-4 p-3 bg-danger rounded">
        ⚠️ {{ error }}
      </div>
    {% endif %}

    <div class="mt-6 text-left">
      <h2 class="text-lg font-semibold">{{ texts.how_it_works }}</h2>
      <p class="mt-2">{{ texts.step1 }}</p>
      <p>{{ texts.step2 }}</p>
      <p>{{ texts.step3 }}</p>
    </div>
  </div>

  <script>
    document.getElementById('linkForm').addEventListener('submit', function(event) {
      const url = this.url.value.trim();
      if (!url.startsWith('http://') && !url.startsWith('https://')) {
        event.preventDefault();
        alert('{{ texts.alert_invalid_url }}');
      }
    });

    function changeLanguage() {
      const select = document.getElementById('language-select');
      const lang = select.value;
      const url = new URL(window.location.href);
      url.searchParams.set('lang', lang);
      window.location.href = url.toString();
    }
  </script>
</body>
</html>
'''

@app.route('/', methods=['GET'])
def index():
    lang = request.args.get('lang', 'en').lower()
    if lang not in LANGS:
        lang = 'en'
    return render_template_string(HTML_TEMPLATE, texts=LANGS[lang], result=None, error=None, lang=lang)

@app.route('/create', methods=['POST'])
def create():
    lang = request.args.get('lang', 'en').lower()
    if lang not in LANGS:
        lang = 'en'

    url = request.form.get('url')
    if not url:
        return render_template_string(HTML_TEMPLATE, texts=LANGS[lang], error=LANGS[lang]['error_input'], result=None, lang=lang)

    token = str(uuid.uuid4())[:8]
    db[token] = {"url": url, "used": False}
    save_db()
    short_url = request.host_url + token
    return render_template_string(HTML_TEMPLATE, texts=LANGS[lang], result=short_url, error=None, lang=lang)

@app.route('/<token>')
def follow(token):
    if token not in db:
        # Возьмём язык из параметров или по умолчанию английский
        lang = request.args.get('lang', 'en').lower()
        if lang not in LANGS:
            lang = 'en'
        return render_template_string(HTML_TEMPLATE, texts=LANGS[lang], error=LANGS[lang]['error_not_found'], result=None, lang=lang)

    if db[token]['used']:
        lang = request.args.get('lang', 'en').lower()
        if lang not in LANGS:
            lang = 'en'
        return render_template_string(HTML_TEMPLATE, texts=LANGS[lang], error=LANGS[lang]['error_used'], result=None, lang=lang)

    db[token]['used'] = True
    save_db()
    return redirect(db[token]['url'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
