from flask import request, redirect, url_for, flash, render_template
from sqlalchemy import or_

from app.models import db, Book, Loan
from . import books_bp

@books_bp.get('/')
def list_books():
    q = request.args.get('q', '', type=str)
    query = Book.query
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Book.title.ilike(like), Book.author.ilike(like)))
    books = query.order_by(Book.id.desc()).all()
    return render_template('books/list.html', books=books, q=q)

@books_bp.route('/new', methods=['GET','POST'])
def new_book():
    if request.method == 'POST':
        title = request.form.get('title','').strip()
        author = request.form.get('author','').strip()
        year = request.form.get('year', type=int)
        total = request.form.get('total_copies', type=int, default=1)
        if not title or not author:
            flash('Vui lòng nhập Tiêu đề và Tác giả')
        else:
            total = max(total or 1, 1)
            b = Book(title=title, author=author, year=year, total_copies=total, available_copies=total)
            db.session.add(b)
            db.session.commit()
            flash('Đã thêm sách')
            return redirect(url_for('books.list_books'))
    return render_template('books/new.html')

@books_bp.route('/<int:book_id>/edit', methods=['GET','POST'])
def edit_book(book_id):
    b = Book.query.get_or_404(book_id)
    if request.method == 'POST':
        title = request.form.get('title','').strip()
        author = request.form.get('author','').strip()
        year = request.form.get('year', type=int)
        total = request.form.get('total_copies', type=int)
        if not title or not author or not total or total < 1:
            flash('Dữ liệu không hợp lệ')
        else:
            # Adjust available copies relative to total change
            delta = total - b.total_copies
            b.title = title
            b.author = author
            b.year = year
            b.total_copies = total
            b.available_copies = max(0, b.available_copies + delta)
            db.session.commit()
            flash('Đã cập nhật sách')
            return redirect(url_for('books.list_books'))
    return render_template('books/edit.html', book=b)

@books_bp.route('/<int:book_id>/delete', methods=['POST', 'DELETE'])
def delete_book(book_id):
    b = Book.query.get_or_404(book_id)
    if Loan.query.filter(Loan.book_id==b.id, Loan.returned_at.is_(None)).first():
        flash('Không thể xóa: sách đang có người mượn')
        return redirect(url_for('books.list_books'))
    db.session.delete(b)
    db.session.commit()
    flash('Đã xóa sách')
    return redirect(url_for('books.list_books'))