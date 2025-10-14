from flask import Flask, request, jsonify, make_response
from datetime import datetime, timedelta
import hashlib

app = Flask(__name__)

books = [
    {"id": 1, "title": "Python Programming", "author": "John Doe", "available": True, "updated": "2024-01-01T10:00:00Z"},
    {"id": 2, "title": "Web Development", "author": "Jane Smith", "available": True, "updated": "2024-01-02T10:00:00Z"},
    {"id": 3, "title": "Data Science", "author": "Bob Johnson", "available": False, "updated": "2024-01-03T10:00:00Z"}
]

def generate_etag(data):
    return hashlib.md5(str(data).encode()).hexdigest()

def add_cache_headers(response, max_age=300):
    response.headers['Cache-Control'] = f'public, max-age={max_age}'
    response.headers['Expires'] = (datetime.utcnow() + timedelta(seconds=max_age)).strftime('%a, %d %b %Y %H:%M:%S GMT')
    return response

@app.route('/')
def home():
    return '''
    <h1>Library System - Cacheable + Uniform Interface</h1>
    <h2>Added Principles:</h2>
    <ul>
        <li><strong>Cacheable:</strong> Cache-Control, ETags, Last-Modified</li>
        <li><strong>Uniform Interface:</strong> Standard HTTP methods, status codes, resource URIs</li>
    </ul>
    <h2>Uniform Interface:</h2>
    <ul>
        <li>GET /api/books - List books</li>
        <li>GET /api/books/{id} - Get book</li>
        <li>POST /api/books - Create book</li>
        <li>PUT /api/books/{id} - Update book</li>
        <li>DELETE /api/books/{id} - Delete book</li>
    </ul>
    '''

# Uniform Interface: Consistent resource URIs under /api
@app.route('/api/books', methods=['GET'])
def get_books():
    # Cacheable: ETags for conditional requests
    if_none_match = request.headers.get('If-None-Match')
    
    author_filter = request.args.get('author')
    available_filter = request.args.get('available')
    
    result = books[:]
    
    if author_filter:
        result = [b for b in result if author_filter.lower() in b['author'].lower()]
    
    if available_filter:
        is_available = available_filter.lower() == 'true'
        result = [b for b in result if b['available'] == is_available]
    
    response_data = {
        "books": result,
        "count": len(result),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    # Generate ETag
    etag = generate_etag(response_data)
    
    # Check if client has cached version
    if if_none_match == etag:
        return '', 304  # Not Modified
    
    response = make_response(jsonify(response_data))
    response.headers['ETag'] = etag
    response.headers['Last-Modified'] = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    
    # Cacheable: Set cache headers
    return add_cache_headers(response, max_age=300)  # 5 minutes

@app.route('/api/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = next((b for b in books if b['id'] == book_id), None)
    if not book:
        return jsonify({"error": "Book not found", "code": "BOOK_NOT_FOUND"}), 404
    
    # Cacheable: Check conditional headers
    if_modified_since = request.headers.get('If-Modified-Since')
    if_none_match = request.headers.get('If-None-Match')
    
    etag = generate_etag(book)
    last_modified = book.get('updated', datetime.utcnow().isoformat() + "Z")
    
    if if_none_match == etag:
        return '', 304
    
    response = make_response(jsonify(book))
    response.headers['ETag'] = etag
    response.headers['Last-Modified'] = datetime.strptime(last_modified, '%Y-%m-%dT%H:%M:%SZ').strftime('%a, %d %b %Y %H:%M:%S GMT')
    
    return add_cache_headers(response, max_age=600)  # 10 minutes

@app.route('/api/books', methods=['POST'])
def create_book():
    # Uniform Interface: Proper HTTP status codes
    data = request.json
    if not data or not data.get('title') or not data.get('author'):
        return jsonify({
            "error": "Validation failed", 
            "message": "Title and author are required",
            "code": "VALIDATION_ERROR"
        }), 400
    
    new_book = {
        "id": max([b['id'] for b in books], default=0) + 1,
        "title": data['title'],
        "author": data['author'],
        "available": data.get('available', True),
        "updated": datetime.utcnow().isoformat() + "Z"
    }
    books.append(new_book)
    
    # Uniform Interface: 201 Created with Location header
    response = make_response(jsonify(new_book), 201)
    response.headers['Location'] = f'/api/books/{new_book["id"]}'
    return response

@app.route('/api/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    book = next((b for b in books if b['id'] == book_id), None)
    if not book:
        return jsonify({"error": "Book not found", "code": "BOOK_NOT_FOUND"}), 404
    
    data = request.json
    if not data:
        return jsonify({"error": "No data provided", "code": "NO_DATA"}), 400
    
    # Check ETag for optimistic concurrency control
    if_match = request.headers.get('If-Match')
    current_etag = generate_etag(book)
    
    if if_match and if_match != current_etag:
        return jsonify({"error": "Resource has been modified", "code": "CONFLICT"}), 409
    
    # Update book
    book.update({
        "title": data.get('title', book['title']),
        "author": data.get('author', book['author']),
        "available": data.get('available', book['available']),
        "updated": datetime.utcnow().isoformat() + "Z"
    })
    
    response = make_response(jsonify(book))
    response.headers['ETag'] = generate_etag(book)
    return response

@app.route('/api/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    global books
    book = next((b for b in books if b['id'] == book_id), None)
    if not book:
        return jsonify({"error": "Book not found", "code": "BOOK_NOT_FOUND"}), 404
    
    books = [b for b in books if b['id'] != book_id]
    return '', 204  # No Content

# Uniform Interface: Consistent error handling
@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "error": "Method not allowed",
        "code": "METHOD_NOT_ALLOWED"
    }), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal server error",
        "code": "INTERNAL_ERROR"
    }), 500

if __name__ == '__main__':
    print("=== Version 3: Client-Server + Stateless + Cacheable + Uniform Interface ===")
    print("Added caching with ETags and Cache-Control headers")
    print("Uniform resource URIs and HTTP status codes")
    print("Server: http://localhost:5002")
    app.run(debug=True, port=5002)