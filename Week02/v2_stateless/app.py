from flask import Flask, request, jsonify
import uuid

app = Flask(__name__)

# In-memory storage (shared across all sessions)
books = [
    {"id": 1, "title": "Python Programming", "author": "John Doe", "available": True},
    {"id": 2, "title": "Web Development", "author": "Jane Smith", "available": True},
    {"id": 3, "title": "Data Science", "author": "Bob Johnson", "available": False}
]

# Stateless: No server-side session storage
# Each request must contain all information needed to understand it

@app.route('/')
def home():
    return '''
    <h1>Library System - Stateless</h1>
    <h2>Stateless Principles:</h2>
    <ul>
        <li>No server-side session state</li>
        <li>Each request contains all needed information</li>
        <li>Server does not store client context between requests</li>
    </ul>
    <h2>Available Endpoints:</h2>
    <ul>
        <li>GET /books - Get all books</li>
        <li>GET /books/&lt;id&gt; - Get book by ID</li>
        <li>POST /books - Add new book</li>
        <li>PUT /books/&lt;id&gt; - Update book</li>
        <li>DELETE /books/&lt;id&gt; - Delete book</li>
    </ul>
    '''

@app.route('/books', methods=['GET'])
def get_books():
    # Stateless: All filtering parameters come from request
    author_filter = request.args.get('author')
    available_filter = request.args.get('available')
    
    result = books[:]
    
    if author_filter:
        result = [b for b in result if author_filter.lower() in b['author'].lower()]
    
    if available_filter:
        is_available = available_filter.lower() == 'true'
        result = [b for b in result if b['available'] == is_available]
    
    return jsonify({
        "books": result,
        "count": len(result),
        "filters_applied": {
            "author": author_filter,
            "available": available_filter
        }
    })

@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = next((b for b in books if b['id'] == book_id), None)
    if book:
        return jsonify(book)
    return jsonify({"error": "Book not found"}), 404

@app.route('/books', methods=['POST'])
def add_book():
    # Stateless: All data needed comes in the request
    data = request.json
    if not data or not data.get('title') or not data.get('author'):
        return jsonify({"error": "Title and author required"}), 400
    
    new_book = {
        "id": max([b['id'] for b in books], default=0) + 1,
        "title": data['title'],
        "author": data['author'],
        "available": data.get('available', True)
    }
    books.append(new_book)
    return jsonify(new_book), 201

@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    # Stateless: Complete resource state provided in request
    book = next((b for b in books if b['id'] == book_id), None)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Update all provided fields
    book.update({
        "title": data.get('title', book['title']),
        "author": data.get('author', book['author']),
        "available": data.get('available', book['available'])
    })
    
    return jsonify(book)

@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    global books
    books = [b for b in books if b['id'] != book_id]
    return '', 204

if __name__ == '__main__':
    print("=== Version 2: Client-Server + Stateless ===")
    print("No server-side session state")
    print("Each request contains all needed information")
    print("Server: http://localhost:5001")
    app.run(debug=True, port=5001)