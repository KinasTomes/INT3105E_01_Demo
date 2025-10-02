from flask import Blueprint, redirect, url_for, flash, render_template

from app.models import db, Book, Member, Loan
from . import main_bp

@main_bp.get('/')
def dashboard():
    book_count = Book.query.count()
    member_count = Member.query.count()
    active_loans = Loan.query.filter_by(returned_at=None).count()
    return render_template('dashboard.html', book_count=book_count, member_count=member_count, active_loans=active_loans)

@main_bp.get('/seed')
def seed():
    if Book.query.count() == 0:
        db.session.add_all([
            Book(title='Lập trình Python', author='Nguyễn Văn A', year=2023, total_copies=3, available_copies=3),
            Book(title='Cấu trúc dữ liệu', author='Trần Thị B', year=2021, total_copies=2, available_copies=2),
            Book(title='Máy học cơ bản', author='Lê Văn C', year=2022, total_copies=1, available_copies=1),
        ])
    if Member.query.count() == 0:
        db.session.add_all([
            Member(name='Quang Hưng', email='hung@example.com'),
            Member(name='Minh Anh', email='minhanh@example.com'),
        ])
    db.session.commit()
    flash('Đã tạo dữ liệu mẫu')
    return redirect(url_for('main.dashboard'))