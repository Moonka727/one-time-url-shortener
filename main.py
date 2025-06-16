from flask import Flask, request, redirect, render_template_string
from flask_sqlalchemy import SQLAlchemy
import uuid
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Link(db.Model):
    id = db.Column(db.String(8), primary_key=True)
    original_url = db.Column(db.String(2048), nullable=False)
    used = db.Column(db.Boolean, default=False)

with app.app_context():
    db.create_all()

# Multilingual texts
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
    # Add other languages here...
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
      background-color: #222222;
      border: 1px solid #555555;
      color: #ffffff;
      padding: 0.5rem;
      border-radius: 0.25rem;
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
    new_link = Link(id=token, original_url=url)
    db.session.add(new_link)
    db.session.commit()

    short_url = request.host_url + token
    return render_template_string(HTML_TEMPLATE, texts=LANGS[lang], result=short_url, error=None, lang=lang)

@app.route('/<token>')
def follow(token):
    lang = request.args.get('lang', 'en').lower()
    if lang not in LANGS:
        lang = 'en'

    link = Link.query.get(token)
    if not link:
        return render_template_string(HTML_TEMPLATE, texts=LANGS[lang], error=LANGS[lang]['error_not_found'], result=None, lang=lang)

    if link.used:
        return render_template_string(HTML_TEMPLATE, texts=LANGS[lang], error=LANGS[lang]['error_used'], result=None, lang=lang)

    link.used = True
    db.session.commit()
    return redirect(link.original_url)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
