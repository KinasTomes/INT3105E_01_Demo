from flask import request, redirect, url_for, flash, render_template

from app.models import db, Member, Loan
from . import members_bp

@members_bp.get('/')
def list_members():
    members = Member.query.order_by(Member.id.desc()).all()
    return render_template('members/list.html', members=members)

@members_bp.route('/new', methods=['GET','POST'])
def new_member():
    if request.method == 'POST':
        name = request.form.get('name','').strip()
        email = request.form.get('email','').strip()
        if not name or not email:
            flash('Vui lòng nhập tên và email')
        elif Member.query.filter_by(email=email).first():
            flash('Email đã tồn tại')
        else:
            m = Member(name=name, email=email)
            db.session.add(m)
            db.session.commit()
            flash('Đã thêm thành viên')
            return redirect(url_for('members.list_members'))
    return render_template('members/new.html')

@members_bp.route('/<int:member_id>/edit', methods=['GET','POST'])
def edit_member(member_id):
    m = Member.query.get_or_404(member_id)
    if request.method == 'POST':
        name = request.form.get('name','').strip()
        email = request.form.get('email','').strip()
        if not name or not email:
            flash('Dữ liệu không hợp lệ')
        else:
            # ensure unique email
            existed = Member.query.filter(Member.email==email, Member.id!=m.id).first()
            if existed:
                flash('Email đã được sử dụng')
            else:
                m.name = name
                m.email = email
                db.session.commit()
                flash('Đã cập nhật thành viên')
                return redirect(url_for('members.list_members'))
    return render_template('members/edit.html', member=m)

@members_bp.route('/<int:member_id>/delete', methods=['POST', 'DELETE'])
def delete_member(member_id):
    m = Member.query.get_or_404(member_id)
    if Loan.query.filter(Loan.member_id==m.id, Loan.returned_at.is_(None)).first():
        flash('Không thể xóa: thành viên đang có sách mượn')
        return redirect(url_for('members.list_members'))
    db.session.delete(m)
    db.session.commit()
    flash('Đã xóa thành viên')
    return redirect(url_for('members.list_members'))