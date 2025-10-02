from datetime import datetime, timedelta
from flask import request, redirect, url_for, flash, render_template

from app.models import db, Book, Member, Loan
from . import loans_bp

@loans_bp.get('/')
def list_loans():
    loans = Loan.query.order_by(Loan.id.desc()).all()
    return render_template('loans/list.html', loans=loans)

@loans_bp.route('/borrow', methods=['GET','POST'])
def borrow():
    if request.method == 'POST':
        book_id = request.form.get('book_id', type=int)
        member_id = request.form.get('member_id', type=int)
        days = request.form.get('days', type=int, default=14)
        book = Book.query.get(book_id)
        member = Member.query.get(member_id)
        if not book or not member:
            flash('Chọn sách và thành viên hợp lệ')
        elif book.available_copies < 1:
            flash('Sách đã hết bản để mượn')
        else:
            loan = Loan(book_id=book.id, member_id=member.id,
                        borrowed_at=datetime.utcnow(),
                        due_date=datetime.utcnow() + timedelta(days=max(1, days)))
            db.session.add(loan)
            book.available_copies -= 1
            db.session.commit()
            flash('Đã tạo phiếu mượn')
            return redirect(url_for('loans.list_loans'))
    books = Book.query.order_by(Book.title).all()
    members = Member.query.order_by(Member.name).all()
    return render_template('loans/borrow.html', books=books, members=members)

@loans_bp.route('/return/<int:loan_id>', methods=['POST'])
def return_loan(loan_id):
    loan = Loan.query.get_or_404(loan_id)
    if loan.returned_at is None:
        loan.returned_at = datetime.utcnow()
        loan.book.available_copies = max(0, loan.book.available_copies + 1)
        db.session.commit()
        flash('Đã trả sách')
    else:
        flash('Phiếu mượn đã được đóng trước đó')
    return redirect(url_for('loans.list_loans'))