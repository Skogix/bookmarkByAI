from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookmarks.db'
db = SQLAlchemy(app)

class Bookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    title = db.Column(db.String(200))
    content = db.Column(db.Text)

@app.route('/save', methods=['POST'])
def save_bookmark():
    data = request.json
    new_bookmark = Bookmark(url=data['url'], title=data.get('title'), content=data.get('content'))
    db.session.add(new_bookmark)
    db.session.commit()
    return jsonify({"message": "Bookmark saved successfully!"}), 201

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
