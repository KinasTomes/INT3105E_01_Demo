from flask import Flask, request, jsonify

app = Flask(__name__)

books = [
    {"id": 1, "title": "Python Programming", "author": "John Doe"},
    {"id": 2, "title": "Web Development", "author": "Jane Smith"},
]

@app.route('/')
def home():
    return '''
    <h1>Version 3: Uniform Interface</h1>
    <p><strong>Demo:</strong> Chuẩn HTTP methods, status codes, URIs</p>
    
    <h3>Uniform Interface principles:</h3>
    <ul>
        <li>Standard HTTP methods (GET, POST, PUT, DELETE)</li>
        <li>Proper status codes (200, 201, 204, 404, 400)</li>
        <li>Resource-based URIs (/api/books, /api/books/1)</li>
    </ul>
    
    <button onclick="getBooks()">GET Books</button>
    <button onclick="getBook(1)">GET Book #1</button>
    <button onclick="addBook()">POST New Book</button>
    <button onclick="updateBook(1)">PUT Update #1</button>
    <button onclick="deleteBook(2)">DELETE Book #2</button>
    
    <div id="result" style="margin-top:20px; padding:10px; background:#f0f0f0;"></div>
    
    <script>
    function getBooks() {
        fetch('/api/books')
        .then(r => { 
            result.innerHTML = '<b>Status: ' + r.status + '</b>';
            return r.json(); 
        })
        .then(data => result.innerHTML += '<pre>' + JSON.stringify(data, null, 2) + '</pre>');
    }
    
    function getBook(id) {
        fetch('/api/books/' + id)
        .then(r => { 
            result.innerHTML = '<b>Status: ' + r.status + '</b>';
            return r.json(); 
        })
        .then(data => result.innerHTML += '<pre>' + JSON.stringify(data, null, 2) + '</pre>');
    }
    
    function addBook() {
        fetch('/api/books', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({title: 'REST API', author: 'New Author'})
        })
        .then(r => { 
            result.innerHTML = '<b>Status: ' + r.status + ' (Created)</b><br>Location: ' + r.headers.get('Location');
            return r.json(); 
        })
        .then(data => result.innerHTML += '<pre>' + JSON.stringify(data, null, 2) + '</pre>');
    }
    
    function updateBook(id) {
        fetch('/api/books/' + id, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({title: 'Updated Title', author: 'Updated Author'})
        })
        .then(r => { 
            result.innerHTML = '<b>Status: ' + r.status + ' (OK)</b>';
            return r.json(); 
        })
        .then(data => result.innerHTML += '<pre>' + JSON.stringify(data, null, 2) + '</pre>');
    }
    
    function deleteBook(id) {
        fetch('/api/books/' + id, {method: 'DELETE'})
        .then(r => { 
            result.innerHTML = '<b>Status: ' + r.status + ' (No Content)</b><br>Book deleted successfully';
        });
    }
    </script>
    '''

@app.route('/api/books', methods=['GET'])
def get_books():
    # Standard GET - returns 200 OK
    return jsonify({'books': books}), 200

@app.route('/api/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = next((b for b in books if b['id'] == book_id), None)
    if not book:
        # Standard 404 Not Found
        return jsonify({'error': 'Book not found'}), 404
    return jsonify(book), 200

@app.route('/api/books', methods=['POST'])
def create_book():
    data = request.json
    if not data or not data.get('title'):
        # Standard 400 Bad Request
        return jsonify({'error': 'Title required'}), 400
    
    new_book = {
        'id': len(books) + 1,
        'title': data.get('title'),
        'author': data.get('author', 'Unknown')
    }
    books.append(new_book)
    
    # Standard 201 Created with Location header
    response = jsonify(new_book)
    response.status_code = 201
    response.headers['Location'] = f'/api/books/{new_book["id"]}'
    return response

@app.route('/api/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    book = next((b for b in books if b['id'] == book_id), None)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    book['title'] = data.get('title', book['title'])
    book['author'] = data.get('author', book['author'])
    
    # Standard 200 OK for successful update
    return jsonify(book), 200

@app.route('/api/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    global books
    book = next((b for b in books if b['id'] == book_id), None)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    
    books = [b for b in books if b['id'] != book_id]
    
    # Standard 204 No Content for successful delete
    return '', 204

if __name__ == '__main__':
    print("=== V3: Uniform Interface ===")
    print("Standard HTTP methods, status codes, URIs")
    print("http://localhost:5002")
    app.run(debug=True, port=5002)
