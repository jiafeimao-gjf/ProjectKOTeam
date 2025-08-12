from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class IdeaHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    idea = db.Column(db.Text, nullable=False)
    params = db.Column(db.String(500))
    user_id = db.Column(db.Integer)
