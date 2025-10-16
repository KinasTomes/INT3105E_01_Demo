from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import hashlib

app = Flask(__name__)

books = [
    {"id": 1, "title": "Python Programming", "author": "John Doe", "updated": "2024-01-01T10:00:00Z"},
    {"id": 2, "title": "Web Development", "author": "Jane Smith", "updated": "2024-01-02T10:00:00Z"},
]

def generate_etag(data):
    return hashlib.md5(str(data).encode()).hexdigest()

@app.route('/')
def home():
    return '''
    <h1>Version 4: Full REST (with Cache)</h1>
    <p><strong>Demo:</strong> V3 + Cache headers (ETag, Cache-Control)</p>
    
    <h3>Cache principles:</h3>
    <ul>
        <li>ETag for conditional requests</li>
        <li>Cache-Control headers</li>
        <li>304 Not Modified responses</li>
    </ul>
    
    <button onclick="getBooks()">GET Books (cacheable)</button>
    <button onclick="getBooksCached()">GET Books (with ETag)</button>
    <button onclick="getBook(1)">GET Book #1 (cacheable)</button>
    
    <div id="result" style="margin-top:20px; padding:10px; background:#f0f0f0;"></div>
    
    <script>
    let lastETag = null;
    
    function getBooks() {
        fetch('/api/books')
        .then(r => { 
            result.innerHTML = '<b>Status: ' + r.status + '</b><br>';
            result.innerHTML += '<b>Cache-Control:</b> ' + r.headers.get('Cache-Control') + '<br>';
            result.innerHTML += '<b>ETag:</b> ' + r.headers.get('ETag') + '<br>';
            lastETag = r.headers.get('ETag');
            return r.json(); 
        })
        .then(data => result.innerHTML += '<pre>' + JSON.stringify(data, null, 2) + '</pre>');
    }
    
    function getBooksCached() {
        if (!lastETag) return alert('Get books first to receive ETag');
        
        fetch('/api/books', {
            headers: {'If-None-Match': lastETag}
        })
        .then(r => { 
            if (r.status === 304) {
                result.innerHTML = '<b>Status: 304 Not Modified</b><br>Cache hit! Server returned no data.';
            } else {
                result.innerHTML = '<b>Status: ' + r.status + '</b><br>Cache miss! Fresh data received.';
                return r.json();
            }
        })
        .then(data => {
            if (data) result.innerHTML += '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
        });
    }
    
    function getBook(id) {
        fetch('/api/books/' + id)
        .then(r => { 
            result.innerHTML = '<b>Status: ' + r.status + '</b><br>';
            result.innerHTML += '<b>ETag:</b> ' + r.headers.get('ETag') + '<br>';
            result.innerHTML += '<b>Last-Modified:</b> ' + r.headers.get('Last-Modified');
            return r.json(); 
        })
        .then(data => result.innerHTML += '<pre>' + JSON.stringify(data, null, 2) + '</pre>');
    }
    </script>
    '''

@app.route('/api/books', methods=['GET'])
def get_books():
    # Check ETag for cache validation
    if_none_match = request.headers.get('If-None-Match')
    
    response_data = {'books': books}
    etag = generate_etag(response_data)
    
    # Return 304 if ETag matches (cache is still valid)
    if if_none_match == etag:
        return '', 304
    
    response = jsonify(response_data)
    response.headers['ETag'] = etag
    response.headers['Cache-Control'] = 'public, max-age=300'  # 5 minutes
    return response, 200

@app.route('/api/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = next((b for b in books if b['id'] == book_id), None)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    
    # Check cache headers
    if_none_match = request.headers.get('If-None-Match')
    etag = generate_etag(book)
    
    if if_none_match == etag:
        return '', 304
    
    response = jsonify(book)
    response.headers['ETag'] = etag
    response.headers['Last-Modified'] = book.get('updated', datetime.utcnow().isoformat() + 'Z')
    response.headers['Cache-Control'] = 'public, max-age=600'  # 10 minutes
    return response, 200

@app.route('/api/books', methods=['POST'])
def create_book():
    data = request.json
    if not data or not data.get('title'):
        return jsonify({'error': 'Title required'}), 400
    
    new_book = {
        'id': len(books) + 1,
        'title': data.get('title'),
        'author': data.get('author', 'Unknown'),
        'updated': datetime.utcnow().isoformat() + 'Z'
    }
    books.append(new_book)
    
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
    
    # Check If-Match for optimistic locking
    if_match = request.headers.get('If-Match')
    current_etag = generate_etag(book)
    
    if if_match and if_match != current_etag:
        return jsonify({'error': 'Resource modified'}), 412
    
    book['title'] = data.get('title', book['title'])
    book['author'] = data.get('author', book['author'])
    book['updated'] = datetime.utcnow().isoformat() + 'Z'
    
    response = jsonify(book)
    response.headers['ETag'] = generate_etag(book)
    return response, 200

@app.route('/api/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    global books
    book = next((b for b in books if b['id'] == book_id), None)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    
    books = [b for b in books if b['id'] != book_id]
    return '', 204

if __name__ == '__main__':
    print("=== V4: Full REST with Cache ===")
    print("V3 + ETag, Cache-Control, 304 Not Modified")
    print("http://localhost:5003")
    app.run(debug=True, port=5003)
