from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

# In-memory storage
books = [
    {"id": 1, "title": "Python Programming", "author": "John Doe", "available": True},
    {"id": 2, "title": "Web Development", "author": "Jane Smith", "available": True},
    {"id": 3, "title": "Data Science", "author": "Bob Johnson", "available": False}
]

# Simple Client-Server Demo
@app.route('/')
def home():
    return '''
    <h1>Library System - Client Server Demo</h1>
    <h2>Available Endpoints:</h2>
    <ul>
        <li>GET /books - Get all books</li>
        <li>GET /books/&lt;id&gt; - Get book by ID</li>
        <li>POST /books - Add new book</li>
    </ul>
    <h2>Test Client:</h2>
    <button onclick="loadBooks()">Load Books</button>
    <div id="result"></div>
    
    <script>
    function loadBooks() {
        fetch('/books')
            .then(response => response.json())
            .then(data => {
                document.getElementById('result').innerHTML = 
                    '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
            });
    }
    </script>
    '''

@app.route('/books', methods=['GET'])
def get_books():
    return jsonify(books)

@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = next((b for b in books if b['id'] == book_id), None)
    if book:
        return jsonify(book)
    return jsonify({"error": "Book not found"}), 404

@app.route('/books', methods=['POST'])
def add_book():
    data = request.json
    new_book = {
        "id": len(books) + 1,
        "title": data.get('title'),
        "author": data.get('author'),
        "available": True
    }
    books.append(new_book)
    return jsonify(new_book), 201

if __name__ == '__main__':
    print("=== Version 1: Client-Server Architecture ===")
    print("Server handles business logic, Client handles presentation")
    print("Server: http://localhost:5000")
    app.run(debug=True, port=5000)