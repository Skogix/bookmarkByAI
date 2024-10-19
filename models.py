from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Bookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(512), nullable=False)
    title = db.Column(db.String(512))
    description = db.Column(db.String)
    screenshot = db.Column(db.String(512))  # Changed from LargeBinary to String
    tags = db.Column(db.String(256))
    category = db.Column(db.String(256))
