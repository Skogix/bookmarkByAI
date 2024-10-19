import os
import time
import requests
from typing import Optional, Tuple
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from flask import Flask, request, render_template, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'  # Change this to a random key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookmarks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

chrome_options = Options()
chrome_options.add_argument("--headless")

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

class Bookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255), nullable=False)
    tags = db.Column(db.String(255))
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    screenshot = db.Column(db.String(255))  # Updated to String instead of LargeBinary

def create_db():
    with app.app_context():
        db.create_all()
        print("database and tables created.")

class BookmarkForm(FlaskForm):
    url = StringField('URL', validators=[DataRequired()])
    submit = SubmitField('Add Bookmark')

class SearchForm(FlaskForm):
    search_term = StringField('Search Term', validators=[DataRequired()])
    submit = SubmitField('Search')

def fetch_metadata(url: str) -> str:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.title.string if soup.title else 'No Title'
    except requests.RequestException as e:
        print(f"Request to {url} failed: {e}")
        return 'No Title'

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

def capture_screenshot(url: str) -> Optional[str]:
    try:
        driver = webdriver.Chrome(service=ChromeService(), options=chrome_options)
        driver.set_page_load_timeout(30)
        driver.get(url)
        time.sleep(3)  # Wait for JavaScript to load content fully
        screenshot = driver.get_screenshot_as_png()
        driver.quit()
        
        if not os.path.exists('static/screenshots'):
            os.makedirs('static/screenshots')
        
        screenshot_filename = f"screenshot_{int(time.time())}.png"
        screenshot_path = os.path.join('static/screenshots', screenshot_filename)
        
        with open(screenshot_path, 'wb') as f:
            f.write(screenshot)
        
        return screenshot_filename
    except Exception as e:
        print(f"Error capturing screenshot: {e}")
        return None

def analyze_bookmark(url: str) -> Optional[str]:
    metadata = fetch_metadata(url)
    prompt = f"Analyze this bookmark with metadata title '{metadata}' and URL: {url}.\nProvide tags, a description, and categorize it."
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
            json={
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 150,
                "n": 1,
                "stop": None,
                "temperature": 0.7,
            },
            timeout=10
        )
        response.raise_for_status()
        analysis = response.json()["choices"][0]["message"]["content"].strip()
        return analysis if analysis else None
    except requests.RequestException as e:
        print(f"Request to OpenAI API failed: {e}")
        return None

def parse_analysis(analysis: str) -> Tuple[str, str, str]:
    lines = analysis.split("\n")
    tags = lines[0].replace("Tags: ", "")
    description = lines[1].replace("Description: ", "")
    category = lines[2].replace("Category: ", "")
    return tags, description, category

@app.route('/')
def index():
    bookmarks = Bookmark.query.all()
    return render_template('index.html', bookmarks=bookmarks, form=SearchForm())

@app.route('/add', methods=['GET', 'POST'])
def add_bookmark():
    form = BookmarkForm()
    if form.validate_on_submit():
        url = form.url.data
        analysis = analyze_bookmark(url)
        if analysis:
            tags, description, category = parse_analysis(analysis)
            screenshot_filename = capture_screenshot(url)
            new_bookmark = Bookmark(url=url, tags=tags, description=description, category=category, screenshot=screenshot_filename)
            db.session.add(new_bookmark)
            db.session.commit()
            flash('Bookmark added successfully!', 'success')
        else:
            flash('Failed to analyze the bookmark.', 'danger')
        return redirect(url_for('index'))
    return render_template('add_bookmark.html', form=form)

@app.route('/search', methods=['POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        search_term = form.search_term.data
        bookmarks = Bookmark.query.filter(
            (Bookmark.tags.contains(search_term)) |
            (Bookmark.description.contains(search_term)) |
            (Bookmark.category.contains(search_term))
        ).all()
        return render_template('index.html', bookmarks=bookmarks, form=form)
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete_bookmark(id):
    bookmark = Bookmark.query.get_or_404(id)
    db.session.delete(bookmark)
    db.session.commit()
    flash('Bookmark deleted successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/view/<int:id>')
def view_bookmark(id):
    bookmark = Bookmark.query.get_or_404(id)
    return render_template('view_bookmark.html', bookmark=bookmark)

if __name__ == '__main__':
    app.run(debug=True, port = 5001)
