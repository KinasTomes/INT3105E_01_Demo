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

def add_hateoas_links(book):
    book_with_links = book.copy()
    book_with_links['_links'] = {
        'self': f'/api/books/{book["id"]}',
        'collection': '/api/books',
        'update': f'/api/books/{book["id"]}',
        'delete': f'/api/books/{book["id"]}'
    }
    return book_with_links

# Code-on-Demand: Dynamic client functionality
@app.route('/')
def home():
    return '''
    <h1>Library System - Full REST (6 Constraints)</h1>
    <h2>All REST Constraints:</h2>
    <ol>
        <li><strong>Client-Server:</strong> Separation of concerns</li>
        <li><strong>Stateless:</strong> No server-side session state</li>
        <li><strong>Cacheable:</strong> ETags, Cache-Control headers</li>
        <li><strong>Uniform Interface:</strong> Standard URIs and HTTP methods</li>
        <li><strong>Layered System:</strong> Proxy/middleware support</li>
        <li><strong>Code-on-Demand:</strong> Dynamic client scripts (this page!)</li>
    </ol>
    
    <h2>Interactive Client (Code-on-Demand):</h2>
    <button onclick="loadBooks()">Load Books</button>
    <button onclick="loadBook(1)">Load Book #1</button>
    <button onclick="createBook()">Create Book</button>
    <div id="result"></div>
    
    <script>
    // Code-on-Demand: Client functionality delivered from server
    async function apiCall(url, options = {}) {
        try {
            const response = await fetch(url, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });
            
            const data = await response.json();
            
            // Show response with headers for learning
            const result = {
                status: response.status,
                headers: Object.fromEntries(response.headers.entries()),
                data: data
            };
            
            document.getElementById('result').innerHTML = 
                '<h3>Response:</h3><pre>' + JSON.stringify(result, null, 2) + '</pre>';
                
        } catch (error) {
            document.getElementById('result').innerHTML = 
                '<h3>Error:</h3><pre>' + error.message + '</pre>';
        }
    }
    
    function loadBooks() {
        apiCall('/api/books');
    }
    
    function loadBook(id) {
        apiCall(`/api/books/${id}`);
    }
    
    function createBook() {
        const bookData = {
            title: "Dynamic Book " + new Date().getTime(),
            author: "Client Script",
            available: true
        };
        
        apiCall('/api/books', {
            method: 'POST',
            body: JSON.stringify(bookData)
        });
    }
    </script>
    '''

# Layered System: Middleware for logging and headers
@app.before_request
def before_request():
    print(f"[MIDDLEWARE] {request.method} {request.path} from {request.remote_addr}")

@app.after_request
def after_request(response):
    # Layered System: Add cross-cutting concerns
    response.headers['X-Powered-By'] = 'REST-Full-Service'
    response.headers['X-Request-ID'] = str(hash(f"{request.method}{request.path}{datetime.utcnow()}"))
    return response

@app.route('/api/books', methods=['GET'])
def get_books():
    if_none_match = request.headers.get('If-None-Match')
    
    author_filter = request.args.get('author')
    available_filter = request.args.get('available')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    result = books[:]
    
    if author_filter:
        result = [b for b in result if author_filter.lower() in b['author'].lower()]
    
    if available_filter:
        is_available = available_filter.lower() == 'true'
        result = [b for b in result if b['available'] == is_available]
    
    # Pagination
    start = (page - 1) * per_page
    end = start + per_page
    paginated_books = result[start:end]
    
    # HATEOAS: Add hypermedia links
    books_with_links = [add_hateoas_links(book) for book in paginated_books]
    
    response_data = {
        "books": books_with_links,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": len(result),
            "pages": (len(result) + per_page - 1) // per_page
        },
        "_links": {
            "self": f"/api/books?page={page}&per_page={per_page}",
            "first": f"/api/books?page=1&per_page={per_page}",
            "last": f"/api/books?page={((len(result) + per_page - 1) // per_page)}&per_page={per_page}"
        },
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    # Add next/prev links if applicable
    if page > 1:
        response_data["_links"]["prev"] = f"/api/books?page={page-1}&per_page={per_page}"
    if end < len(result):
        response_data["_links"]["next"] = f"/api/books?page={page+1}&per_page={per_page}"
    
    etag = generate_etag(response_data)
    
    if if_none_match == etag:
        return '', 304
    
    response = make_response(jsonify(response_data))
    response.headers['ETag'] = etag
    response.headers['Last-Modified'] = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    
    return add_cache_headers(response, max_age=300)

@app.route('/api/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = next((b for b in books if b['id'] == book_id), None)
    if not book:
        return jsonify({
            "error": "Book not found", 
            "code": "BOOK_NOT_FOUND",
            "_links": {
                "collection": "/api/books"
            }
        }), 404
    
    if_none_match = request.headers.get('If-None-Match')
    
    # HATEOAS: Add hypermedia links
    book_with_links = add_hateoas_links(book)
    
    etag = generate_etag(book_with_links)
    
    if if_none_match == etag:
        return '', 304
    
    response = make_response(jsonify(book_with_links))
    response.headers['ETag'] = etag
    response.headers['Last-Modified'] = datetime.strptime(book['updated'], '%Y-%m-%dT%H:%M:%SZ').strftime('%a, %d %b %Y %H:%M:%S GMT')
    
    return add_cache_headers(response, max_age=600)

@app.route('/api/books', methods=['POST'])
def create_book():
    data = request.json
    if not data or not data.get('title') or not data.get('author'):
        return jsonify({
            "error": "Validation failed", 
            "message": "Title and author are required",
            "code": "VALIDATION_ERROR",
            "_links": {
                "collection": "/api/books"
            }
        }), 400
    
    new_book = {
        "id": max([b['id'] for b in books], default=0) + 1,
        "title": data['title'],
        "author": data['author'],
        "available": data.get('available', True),
        "updated": datetime.utcnow().isoformat() + "Z"
    }
    books.append(new_book)
    
    # HATEOAS: Add links to created resource
    book_with_links = add_hateoas_links(new_book)
    
    response = make_response(jsonify(book_with_links), 201)
    response.headers['Location'] = f'/api/books/{new_book["id"]}'
    response.headers['ETag'] = generate_etag(new_book)
    return response

@app.route('/api/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    book = next((b for b in books if b['id'] == book_id), None)
    if not book:
        return jsonify({
            "error": "Book not found", 
            "code": "BOOK_NOT_FOUND",
            "_links": {
                "collection": "/api/books"
            }
        }), 404
    
    data = request.json
    if not data:
        return jsonify({
            "error": "No data provided", 
            "code": "NO_DATA",
            "_links": {
                "self": f"/api/books/{book_id}",
                "collection": "/api/books"
            }
        }), 400
    
    if_match = request.headers.get('If-Match')
    current_etag = generate_etag(book)
    
    if if_match and if_match != current_etag:
        return jsonify({
            "error": "Resource has been modified", 
            "code": "CONFLICT",
            "current_etag": current_etag,
            "_links": {
                "self": f"/api/books/{book_id}",
                "collection": "/api/books"
            }
        }), 409
    
    book.update({
        "title": data.get('title', book['title']),
        "author": data.get('author', book['author']),
        "available": data.get('available', book['available']),
        "updated": datetime.utcnow().isoformat() + "Z"
    })
    
    book_with_links = add_hateoas_links(book)
    
    response = make_response(jsonify(book_with_links))
    response.headers['ETag'] = generate_etag(book)
    return response

@app.route('/api/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    global books
    book = next((b for b in books if b['id'] == book_id), None)
    if not book:
        return jsonify({
            "error": "Book not found", 
            "code": "BOOK_NOT_FOUND",
            "_links": {
                "collection": "/api/books"
            }
        }), 404
    
    books = [b for b in books if b['id'] != book_id]
    return '', 204

# Layered System: Health check endpoint for monitoring layer
@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "v4.0.0",
        "constraints": [
            "client-server",
            "stateless", 
            "cacheable",
            "uniform-interface",
            "layered-system",
            "code-on-demand"
        ]
    })

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "error": "Method not allowed",
        "code": "METHOD_NOT_ALLOWED",
        "_links": {
            "api": "/api/books"
        }
    }), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal server error",
        "code": "INTERNAL_ERROR",
        "_links": {
            "health": "/health"
        }
    }), 500

if __name__ == '__main__':
    print("=== Version 4: Full REST Architecture (All 6 Constraints) ===")
    print("1. Client-Server: Separation of concerns")
    print("2. Stateless: No server-side session state") 
    print("3. Cacheable: ETags and cache headers")
    print("4. Uniform Interface: Standard HTTP methods and URIs")
    print("5. Layered System: Middleware and cross-cutting concerns")
    print("6. Code-on-Demand: Dynamic client scripts")
    print("Server: http://localhost:5003")
    app.run(debug=True, port=5003)