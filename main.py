from flask import Flask, request, redirect, render_template_string, make_response
import uuid
import json
import os
import re

app = Flask(__name__)
DB_FILE = 'db.json'

# Загрузка базы
if os.path.exists(DB_FILE):
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        db = json.load(f)
else:
    db = {}

def save_db():
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

# Тексты для локализации
LANG = {
    'en': {
        'title': "One-time URL Shortener",
        'input_placeholder': "Paste your URL",
        'create_button': "Create",
        'your_link': "Your link:",
        'link_not_found': "Link not found.",
        'link_used': "Link has already been used.",
        'enter_valid_url': "Please enter a valid URL.",
        'url_prefix_alert': "Please enter a full URL starting with http:// or https://",
        'how_it_works': "How it works:",
        'step1': "1. Paste the URL above.",
        'step2': "2. Click Create to get a shortened link.",
        'step3': "3. Use the shortened link while it's active!",
        'language': "Language",
    },
    'ru': {
        'title': "Одноразовый сокращатель ссылок",
        'input_placeholder': "Вставьте ссылку",
        'create_button': "Создать",
        'your_link': "Ваша ссылка:",
        'link_not_found': "Ссылка не найдена.",
        'link_used': "Ссылка уже использована.",
        'enter_valid_url': "Введите корректную ссылку.",
        'url_prefix_alert': "Пожалуйста, вставьте полный URL, начинающийся с http:// или https://",
        'how_it_works': "Как это работает:",
        'step1': "1. Вставьте ссылку в поле выше.",
        'step2': "2. Нажмите \"Создать\", чтобы получить сокращенную ссылку.",
        'step3': "3. Используйте сокращенную ссылку, пока она активна!",
        'language': "Язык",
    },
    'az': {
        'title': "Tək istifadəlik URL qısaldıcı",
        'input_placeholder': "Linki yapışdırın",
        'create_button': "Yarat",
        'your_link': "Sizin linkiniz:",
        'link_not_found': "Link tapılmadı.",
        'link_used': "Link artıq istifadə olunub.",
        'enter_valid_url': "Zəhmət olmasa düzgün link daxil edin.",
        'url_prefix_alert': "Zəhmət olmasa http:// və ya https:// ilə başlayan tam URL daxil edin",
        'how_it_works': "İş prinsipi:",
        'step1': "1. Yuxarıdakı sahəyə link yapışdırın.",
        'step2': "2. Qısaldılmış link almaq üçün Yarat düyməsini basın.",
        'step3': "3. Link aktiv olduğu müddətcə istifadə edin!",
        'language': "Dil",
    }
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
      background-color: #000000;
      color: #ffffff;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: Arial, sans-serif;
    }
    .container {
      background-color: #121212;
      padding: 2rem;
      border-radius: 0.5rem;
      box-shadow: 0 0 10px #555;
      width: 100%;
      max-width: 480px;
      text-align: center;
    }
    input, button, select {
      border-radius: 0.375rem;
      border: 1px solid #444;
      padding: 0.5rem 1rem;
      font-size: 1rem;
      background-color: #222;
      color: #eee;
      transition: box-shadow 0.3s ease;
    }
    input:focus, select:focus {
      outline: none;
      box-shadow: 0 0 5px #888;
      border-color: #888;
      background-color: #333;
    }
    button {
      cursor: pointer;
      background-color: #fff;
      color: #000;
      border: none;
      margin-top: 1rem;
      width: 100%;
    }
    button:hover {
      background-color: #eee;
    }
    a {
      color: #9a9;
      text-decoration: underline;
      word-break: break-word;
    }
    .message {
      margin-top: 1rem;
      padding: 1rem;
      border-radius: 0.5rem;
    }
    .success {
      background-color: #004400;
      color: #aaffaa;
    }
    .error {
      background-color: #440000;
      color: #ffaaaa;
    }
    .lang-select {
      margin-bottom: 1rem;
      text-align: right;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="lang-select">
      <form method="GET" id="langForm">
        <label for="lang">{{ texts.language }}: </label>
        <select name="lang" id="lang" onchange="document.getElementById('langForm').submit()">
          <option value="en" {% if lang == 'en' %}selected{% endif %}>English</option>
          <option value="ru" {% if lang == 'ru' %}selected{% endif %}>Русский</option>
          <option value="az" {% if lang == 'az' %}selected{% endif %}>Azərbaycanca</option>
        </select>
      </form>
    </div>
    <h1 style="margin-bottom: 1rem;">🔗 {{ texts.title }}</h1>

    <form method="POST" action="/create{% if lang %}?lang={{ lang }}{% endif %}" id="linkForm">
      <input
        type="url"
        name="url"
        placeholder="{{ texts.input_placeholder }}"
        required
        pattern="https?://.+"
        title="{{ texts.url_prefix_alert }}"
        autocomplete="off"
      />
      <button type="submit">{{ texts.create_button }}</button>
    </form>

    {% if result %}
      <div class="message success" role="alert">
        ✅ {{ texts.your_link }} <br/>
        <a href="{{ result }}" target="_blank" rel="noopener noreferrer">{{ result }}</a>
      </div>
    {% endif %}

    {% if error %}
      <div class="message error" role="alert">
        ⚠️ {{ error }}
      </div>
    {% endif %}

    <div style="margin-top: 2rem; font-size: 0.9rem; color: #aaa; text-align: left;">
      <h2>{{ texts.how_it_works }}</h2>
      <ol style="padding-left: 1rem;">
        <li>{{ texts.step1 }}</li>
        <li>{{ texts.step2 }}</li>
        <li>{{ texts.step3 }}</li>
      </ol>
    </div>
  </div>
</body>
</html>
'''

def get_lang():
    # Получаем язык из параметров GET, потом из куки, иначе 'en'
    lang = request.args.get('lang')
    if lang not in LANG:
        lang = request.cookies.get('lang', 'en')
    if lang not in LANG:
        lang = 'en'
    return lang

@app.route('/', methods=['GET'])
def index():
    lang = get_lang()
    texts = LANG[lang]
    resp = make_response(render_template_string(HTML_TEMPLATE, result=None, error=None, texts=texts, lang=lang))
    resp.set_cookie('lang', lang, max_age=30*24*60*60)  # Запомнить на 30 дней
    return resp

@app.route('/create', methods=['POST'])
def create():
    lang = get_lang()
    texts = LANG[lang]

    url = request.form.get('url', '').strip()

    # Простая валидация URL
    if not url or not re.match(r'^https?://.+', url):
        resp = make_response(render_template_string(HTML_TEMPLATE, error=texts['enter_valid_url'], result=None, texts=texts, lang=lang))
        resp.set_cookie('lang', lang, max_age=30*24*60*60)
        return resp

    token = str(uuid.uuid4())[:8]
    db[token] = {"url": url, "used": False}
    save_db()
    short_url = request.host_url + token

    resp = make_response(render_template_string(HTML_TEMPLATE, result=short_url, error=None, texts=texts, lang=lang))
    resp.set_cookie('lang', lang, max_age=30*24*60*60)
    return resp

@app.route('/<token>')
def follow(token):
    lang = get_lang()
    texts = LANG[lang]

    if token not in db:
        resp = make_response(render_template_string(HTML_TEMPLATE, error=texts['link_not_found'], result=None, texts=texts, lang=lang))
        resp.set_cookie('lang', lang, max_age=30*24*60*60)
        return resp
    if db[token]['used']:
        resp = make_response(render_template_string(HTML_TEMPLATE, error=texts['link_used'], result=None, texts=texts, lang=lang))
        resp.set_cookie('lang', lang, max_age=30*24*60*60)
        return resp

    db[token]['used'] = True
    save_db()
    return redirect(db[token]['url'])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
