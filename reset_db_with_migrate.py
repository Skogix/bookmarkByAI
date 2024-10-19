from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookmarks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Bookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255), nullable=False)
    tags = db.Column(db.String(255))
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    screenshot = db.Column(db.String(255))

if __name__ == "__main__":
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("Database tables dropped and recreated.")
