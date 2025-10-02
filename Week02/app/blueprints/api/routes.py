from datetime import datetime, timedelta
from flask import request, jsonify, url_for

from app.models import db, Book, Member, Loan
from . import api_bp

# ===========================
# Helper function to add HATEOAS links
# ===========================
def add_book_links(book_dict, book_id):
    """Add hypermedia links to book representation"""
    book_dict['_links'] = {
        'self': url_for('api.get_book', book_id=book_id, _external=True),
        'collection': url_for('api.api_books_list', _external=True),
        'update': url_for('api.update_book', book_id=book_id, _external=True),
        'delete': url_for('api.delete_book', book_id=book_id, _external=True),
    }
    return book_dict

def add_member_links(member_dict, member_id):
    """Add hypermedia links to member representation"""
    member_dict['_links'] = {
        'self': url_for('api.get_member', member_id=member_id, _external=True),
        'collection': url_for('api.api_members_list', _external=True),
        'update': url_for('api.update_member', member_id=member_id, _external=True),
        'delete': url_for('api.delete_member', member_id=member_id, _external=True),
    }
    return member_dict

def add_loan_links(loan_dict, loan_id):
    """Add hypermedia links to loan representation"""
    loan_dict['_links'] = {
        'self': url_for('api.get_loan', loan_id=loan_id, _external=True),
        'collection': url_for('api.api_loans_list', _external=True),
    }
    if loan_dict['is_active']:
        loan_dict['_links']['return'] = url_for('api.return_loan', loan_id=loan_id, _external=True)
    return loan_dict

# ===========================
# Books API - RESTful with HATEOAS
# ===========================
@api_bp.route('/books', methods=['GET'])
def api_books_list():
    """Get all books with pagination and hypermedia links"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    pagination = Book.query.paginate(page=page, per_page=per_page, error_out=False)
    books = pagination.items
    
    response = {
        'data': [add_book_links(b.to_dict(), b.id) for b in books],
        'meta': {
            'page': page,
            'per_page': per_page,
            'total_items': pagination.total,
            'total_pages': pagination.pages,
        },
        '_links': {
            'self': url_for('api.api_books_list', page=page, per_page=per_page, _external=True),
        }
    }
    
    if pagination.has_next:
        response['_links']['next'] = url_for('api.api_books_list', page=page+1, per_page=per_page, _external=True)
    if pagination.has_prev:
        response['_links']['prev'] = url_for('api.api_books_list', page=page-1, per_page=per_page, _external=True)
    
    return jsonify(response), 200, {'Content-Type': 'application/json'}

@api_bp.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """Get a single book by ID"""
    book = Book.query.get(book_id)
    if not book:
        return jsonify({
            'error': 'Not Found',
            'message': f'Book with id {book_id} does not exist'
        }), 404
    
    return jsonify(add_book_links(book.to_dict(), book.id)), 200, {'Content-Type': 'application/json'}

@api_bp.route('/books', methods=['POST'])
def api_books_create():
    """Create a new book"""
    if not request.is_json:
        return jsonify({
            'error': 'Bad Request',
            'message': 'Content-Type must be application/json'
        }), 400, {'Content-Type': 'application/json'}
    
    data = request.get_json()
    title = (data.get('title') or '').strip()
    author = (data.get('author') or '').strip()
    year = data.get('year')
    total = int(data.get('total_copies') or 1)
    
    if not title or not author:
        return jsonify({
            'error': 'Bad Request',
            'message': 'title and author are required fields'
        }), 400, {'Content-Type': 'application/json'}
    
    b = Book(title=title, author=author, year=year, total_copies=total, available_copies=total)
    db.session.add(b)
    db.session.commit()
    
    response = add_book_links(b.to_dict(), b.id)
    return jsonify(response), 201, {
        'Content-Type': 'application/json',
        'Location': url_for('api.get_book', book_id=b.id, _external=True)
    }

@api_bp.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    """Update an existing book"""
    book = Book.query.get(book_id)
    if not book:
        return jsonify({
            'error': 'Not Found',
            'message': f'Book with id {book_id} does not exist'
        }), 404, {'Content-Type': 'application/json'}
    
    if not request.is_json:
        return jsonify({
            'error': 'Bad Request',
            'message': 'Content-Type must be application/json'
        }), 400, {'Content-Type': 'application/json'}
    
    data = request.get_json()
    
    # Update fields if provided
    if 'title' in data:
        book.title = data['title'].strip()
    if 'author' in data:
        book.author = data['author'].strip()
    if 'year' in data:
        book.year = data['year']
    if 'total_copies' in data:
        total = int(data['total_copies'])
        delta = total - book.total_copies
        book.total_copies = total
        book.available_copies = max(0, book.available_copies + delta)
    
    db.session.commit()
    
    return jsonify(add_book_links(book.to_dict(), book.id)), 200, {'Content-Type': 'application/json'}

@api_bp.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    """Delete a book"""
    book = Book.query.get(book_id)
    if not book:
        return jsonify({
            'error': 'Not Found',
            'message': f'Book with id {book_id} does not exist'
        }), 404, {'Content-Type': 'application/json'}
    
    # Check for active loans
    active_loans = Loan.query.filter(Loan.book_id==book.id, Loan.returned_at.is_(None)).count()
    if active_loans > 0:
        return jsonify({
            'error': 'Conflict',
            'message': 'Cannot delete book with active loans'
        }), 409, {'Content-Type': 'application/json'}
    
    db.session.delete(book)
    db.session.commit()
    
    return '', 204

# ===========================
# Members API - RESTful with HATEOAS
# ===========================
@api_bp.route('/members', methods=['GET'])
def api_members_list():
    """Get all members with pagination and hypermedia links"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    pagination = Member.query.paginate(page=page, per_page=per_page, error_out=False)
    members = pagination.items
    
    response = {
        'data': [add_member_links(m.to_dict(), m.id) for m in members],
        'meta': {
            'page': page,
            'per_page': per_page,
            'total_items': pagination.total,
            'total_pages': pagination.pages,
        },
        '_links': {
            'self': url_for('api.api_members_list', page=page, per_page=per_page, _external=True),
        }
    }
    
    if pagination.has_next:
        response['_links']['next'] = url_for('api.api_members_list', page=page+1, per_page=per_page, _external=True)
    if pagination.has_prev:
        response['_links']['prev'] = url_for('api.api_members_list', page=page-1, per_page=per_page, _external=True)
    
    return jsonify(response), 200, {'Content-Type': 'application/json'}

@api_bp.route('/members/<int:member_id>', methods=['GET'])
def get_member(member_id):
    """Get a single member by ID"""
    member = Member.query.get(member_id)
    if not member:
        return jsonify({
            'error': 'Not Found',
            'message': f'Member with id {member_id} does not exist'
        }), 404
    
    return jsonify(add_member_links(member.to_dict(), member.id)), 200, {'Content-Type': 'application/json'}

@api_bp.route('/members', methods=['POST'])
def create_member():
    """Create a new member"""
    if not request.is_json:
        return jsonify({
            'error': 'Bad Request',
            'message': 'Content-Type must be application/json'
        }), 400, {'Content-Type': 'application/json'}
    
    data = request.get_json()
    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip()
    
    if not name or not email:
        return jsonify({
            'error': 'Bad Request',
            'message': 'name and email are required fields'
        }), 400, {'Content-Type': 'application/json'}
    
    # Check email uniqueness
    if Member.query.filter_by(email=email).first():
        return jsonify({
            'error': 'Conflict',
            'message': 'Email already exists'
        }), 409, {'Content-Type': 'application/json'}
    
    m = Member(name=name, email=email)
    db.session.add(m)
    db.session.commit()
    
    response = add_member_links(m.to_dict(), m.id)
    return jsonify(response), 201, {
        'Content-Type': 'application/json',
        'Location': url_for('api.get_member', member_id=m.id, _external=True)
    }

@api_bp.route('/members/<int:member_id>', methods=['PUT'])
def update_member(member_id):
    """Update an existing member"""
    member = Member.query.get(member_id)
    if not member:
        return jsonify({
            'error': 'Not Found',
            'message': f'Member with id {member_id} does not exist'
        }), 404, {'Content-Type': 'application/json'}
    
    if not request.is_json:
        return jsonify({
            'error': 'Bad Request',
            'message': 'Content-Type must be application/json'
        }), 400, {'Content-Type': 'application/json'}
    
    data = request.get_json()
    
    # Update fields if provided
    if 'name' in data:
        member.name = data['name'].strip()
    if 'email' in data:
        email = data['email'].strip()
        # Check email uniqueness
        existing = Member.query.filter(Member.email==email, Member.id!=member_id).first()
        if existing:
            return jsonify({
                'error': 'Conflict',
                'message': 'Email already exists'
            }), 409, {'Content-Type': 'application/json'}
        member.email = email
    
    db.session.commit()
    
    return jsonify(add_member_links(member.to_dict(), member.id)), 200, {'Content-Type': 'application/json'}

@api_bp.route('/members/<int:member_id>', methods=['DELETE'])
def delete_member(member_id):
    """Delete a member"""
    member = Member.query.get(member_id)
    if not member:
        return jsonify({
            'error': 'Not Found',
            'message': f'Member with id {member_id} does not exist'
        }), 404, {'Content-Type': 'application/json'}
    
    # Check for active loans
    active_loans = Loan.query.filter(Loan.member_id==member.id, Loan.returned_at.is_(None)).count()
    if active_loans > 0:
        return jsonify({
            'error': 'Conflict',
            'message': 'Cannot delete member with active loans'
        }), 409, {'Content-Type': 'application/json'}
    
    db.session.delete(member)
    db.session.commit()
    
    return '', 204

# ===========================
# Loans API - RESTful with HATEOAS
# ===========================
@api_bp.route('/loans', methods=['GET'])
def api_loans_list():
    """Get all loans with pagination and hypermedia links"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    active_only = request.args.get('active', 'false').lower() == 'true'
    
    query = Loan.query
    if active_only:
        query = query.filter(Loan.returned_at.is_(None))
    
    pagination = query.order_by(Loan.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
    loans = pagination.items
    
    response = {
        'data': [add_loan_links(l.to_dict(), l.id) for l in loans],
        'meta': {
            'page': page,
            'per_page': per_page,
            'total_items': pagination.total,
            'total_pages': pagination.pages,
            'active_only': active_only
        },
        '_links': {
            'self': url_for('api.api_loans_list', page=page, per_page=per_page, active=active_only, _external=True),
            'create': url_for('api.create_loan', _external=True),
        }
    }
    
    if pagination.has_next:
        response['_links']['next'] = url_for('api.api_loans_list', page=page+1, per_page=per_page, active=active_only, _external=True)
    if pagination.has_prev:
        response['_links']['prev'] = url_for('api.api_loans_list', page=page-1, per_page=per_page, active=active_only, _external=True)
    
    return jsonify(response), 200, {'Content-Type': 'application/json'}

@api_bp.route('/loans/<int:loan_id>', methods=['GET'])
def get_loan(loan_id):
    """Get a single loan by ID"""
    loan = Loan.query.get(loan_id)
    if not loan:
        return jsonify({
            'error': 'Not Found',
            'message': f'Loan with id {loan_id} does not exist'
        }), 404
    
    return jsonify(add_loan_links(loan.to_dict(), loan.id)), 200, {'Content-Type': 'application/json'}

@api_bp.route('/loans', methods=['POST'])
def create_loan():
    """Create a new loan (borrow a book)"""
    if not request.is_json:
        return jsonify({
            'error': 'Bad Request',
            'message': 'Content-Type must be application/json'
        }), 400, {'Content-Type': 'application/json'}
    
    data = request.get_json()
    book_id = data.get('book_id')
    member_id = data.get('member_id')
    days = int(data.get('days', 14))
    
    if not book_id or not member_id:
        return jsonify({
            'error': 'Bad Request',
            'message': 'book_id and member_id are required'
        }), 400, {'Content-Type': 'application/json'}
    
    book = Book.query.get(book_id)
    member = Member.query.get(member_id)
    
    if not book or not member:
        return jsonify({
            'error': 'Not Found',
            'message': 'Invalid book or member ID'
        }), 404, {'Content-Type': 'application/json'}
    
    if book.available_copies < 1:
        return jsonify({
            'error': 'Conflict',
            'message': 'No copies available for borrowing'
        }), 409, {'Content-Type': 'application/json'}
    
    loan = Loan(
        book_id=book.id,
        member_id=member.id,
        borrowed_at=datetime.utcnow(),
        due_date=datetime.utcnow() + timedelta(days=max(1, days))
    )
    db.session.add(loan)
    book.available_copies -= 1
    db.session.commit()
    
    response = add_loan_links(loan.to_dict(), loan.id)
    return jsonify(response), 201, {
        'Content-Type': 'application/json',
        'Location': url_for('api.get_loan', loan_id=loan.id, _external=True)
    }

@api_bp.route('/loans/<int:loan_id>/return', methods=['POST'])
def return_loan(loan_id):
    """Return a borrowed book"""
    loan = Loan.query.get(loan_id)
    if not loan:
        return jsonify({
            'error': 'Not Found',
            'message': f'Loan with id {loan_id} does not exist'
        }), 404, {'Content-Type': 'application/json'}
    
    if loan.returned_at:
        return jsonify({
            'error': 'Conflict',
            'message': 'Book has already been returned'
        }), 409, {'Content-Type': 'application/json'}
    
    loan.returned_at = datetime.utcnow()
    loan.book.available_copies = max(0, loan.book.available_copies + 1)
    db.session.commit()
    
    return jsonify(add_loan_links(loan.to_dict(), loan.id)), 200, {'Content-Type': 'application/json'}

# ===========================
# Error Handlers
# ===========================
@api_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested resource was not found'
    }), 404, {'Content-Type': 'application/json'}

@api_bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred'
    }), 500, {'Content-Type': 'application/json'}

@api_bp.errorhandler(400)
def bad_request(error):
    return jsonify({
        'error': 'Bad Request',
        'message': 'Invalid request data'
    }), 400, {'Content-Type': 'application/json'}