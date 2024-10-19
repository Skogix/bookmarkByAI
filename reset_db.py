from bookmark_assistant import app, db

def reset_database():
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("Database has been reset.")

if __name__ == "__main__":
    reset_database()
