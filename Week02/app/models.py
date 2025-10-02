from datetime import datetime
from typing import Optional

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# ==========================
# Models
# ==========================
class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(120), nullable=False)
    year = db.Column(db.Integer, nullable=True)
    total_copies = db.Column(db.Integer, nullable=False, default=1)
    available_copies = db.Column(db.Integer, nullable=False, default=1)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'year': self.year,
            'total_copies': self.total_copies,
            'available_copies': self.available_copies,
        }

class Member(db.Model):
    __tablename__ = 'members'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'email': self.email}

class Loan(db.Model):
    __tablename__ = 'loans'
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    borrowed_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=False)
    returned_at = db.Column(db.DateTime, nullable=True)

    book = db.relationship('Book', backref='loans')
    member = db.relationship('Member', backref='loans')

    def is_active(self) -> bool:
        return self.returned_at is None

    def to_dict(self):
        return {
            'id': self.id,
            'book': self.book.to_dict() if self.book else None,
            'member': self.member.to_dict() if self.member else None,
            'borrowed_at': self.borrowed_at.isoformat() if self.borrowed_at else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'returned_at': self.returned_at.isoformat() if self.returned_at else None,
            'is_active': self.is_active(),
        }