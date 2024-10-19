from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookmarks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Bookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(512), nullable=False)
    title = db.Column(db.String(512))
    description = db.Column(db.String)
    screenshot = db.Column(db.String(512))  # Changed from LargeBinary to String
    tags = db.Column(db.String(256))
    category = db.Column(db.String(256))

if __name__ == "__main__":
    app.run()
