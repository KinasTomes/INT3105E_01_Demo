from datetime import datetime, timedelta
from flask import request, jsonify

from app.models import db, Book, Member, Loan
from . import api_bp

@api_bp.get('/books')
def api_books_list():
    books = Book.query.all()
    return jsonify([b.to_dict() for b in books])

@api_bp.post('/books')
def api_books_create():
    data = request.get_json(force=True)
    title = (data.get('title') or '').strip()
    author = (data.get('author') or '').strip()
    year = data.get('year')
    total = int(data.get('total_copies') or 1)
    if not title or not author:
        return jsonify({'error': 'title & author required'}), 400
    b = Book(title=title, author=author, year=year, total_copies=total, available_copies=total)
    db.session.add(b)
    db.session.commit()
    return jsonify(b.to_dict()), 201

@api_bp.post('/borrow')
def api_borrow():
    data = request.get_json(force=True)
    book_id = int(data.get('book_id'))
    member_id = int(data.get('member_id'))
    days = int(data.get('days', 14))
    book = Book.query.get(book_id)
    member = Member.query.get(member_id)
    if not book or not member:
        return jsonify({'error': 'invalid book or member'}), 400
    if book.available_copies < 1:
        return jsonify({'error': 'no copies available'}), 409
    loan = Loan(book_id=book.id, member_id=member.id,
                borrowed_at=datetime.utcnow(),
                due_date=datetime.utcnow() + timedelta(days=max(1, days)))
    db.session.add(loan)
    book.available_copies -= 1
    db.session.commit()
    return jsonify(loan.to_dict()), 201

@api_bp.post('/return/<int:loan_id>')
def api_return(loan_id):
    loan = Loan.query.get_or_404(loan_id)
    if loan.returned_at:
        return jsonify({'error': 'already returned'}), 409
    loan.returned_at = datetime.utcnow()
    loan.book.available_copies = max(0, loan.book.available_copies + 1)
    db.session.commit()
    return jsonify(loan.to_dict())