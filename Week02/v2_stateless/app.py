from flask import Flask, request, jsonify
import jwt
from datetime import datetime, timedelta

app = Flask(__name__)
SECRET_KEY = 'demo-secret-2024'

books = [
    {"id": 1, "title": "Python Programming", "author": "John Doe"},
    {"id": 2, "title": "Web Development", "author": "Jane Smith"},
]

users = {"admin": "pass123", "user": "pass456"}

def create_token(username):
    return jwt.encode({
        'user': username,
        'exp': datetime.utcnow() + timedelta(hours=1)
    }, SECRET_KEY, algorithm='HS256')

def verify_token(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except:
        return None

@app.route('/')
def home():
    return '''
    <h1>Version 2: Stateless with Token</h1>
    <p><strong>Demo:</strong> Server không lưu session, mọi request cần token</p>
    
    <h3>1. Login để lấy token:</h3>
    <button onclick="login('admin','pass123')">Login Admin</button>
    <button onclick="login('user','pass456')">Login User</button>
    
    <h3>2. Dùng token để request:</h3>
    <button onclick="getBooks()">Get Books</button>
    <button onclick="addBook()">Add Book</button>
    
    <div id="result" style="margin-top:20px; padding:10px; background:#f0f0f0;"></div>
    
    <script>
    let token = null;
    
    function login(user, pass) {
        fetch('/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username: user, password: pass})
        })
        .then(r => r.json())
        .then(data => {
            token = data.token;
            result.innerHTML = '<b>Token:</b> ' + token.substring(0,40) + '...';
        });
    }
    
    function getBooks() {
        if (!token) return alert('Login first!');
        fetch('/books', {
            headers: {'Authorization': 'Bearer ' + token}
        })
        .then(r => r.json())
        .then(data => result.innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>');
    }
    
    function addBook() {
        if (!token) return alert('Login first!');
        fetch('/books', {
            method: 'POST',
            headers: {
                'Authorization': 'Bearer ' + token,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({title: 'New Book', author: 'Test'})
        })
        .then(r => r.json())
        .then(data => result.innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>');
    }
    </script>
    '''

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = data.get('username')
    password = data.get('password')
    
    if user in users and users[user] == password:
        token = create_token(user)
        return jsonify({'token': token, 'user': user})
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/books', methods=['GET'])
def get_books():
    auth = request.headers.get('Authorization')
    if not auth or not auth.startswith('Bearer '):
        return jsonify({'error': 'Token required'}), 401
    
    token = auth.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        return jsonify({'error': 'Invalid token'}), 401
    
    return jsonify({'books': books, 'user': payload['user']})

@app.route('/books', methods=['POST'])
def add_book():
    auth = request.headers.get('Authorization')
    if not auth or not auth.startswith('Bearer '):
        return jsonify({'error': 'Token required'}), 401
    
    token = auth.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        return jsonify({'error': 'Invalid token'}), 401
    
    data = request.json
    new_book = {
        'id': len(books) + 1,
        'title': data.get('title'),
        'author': data.get('author')
    }
    books.append(new_book)
    return jsonify({'book': new_book, 'created_by': payload['user']}), 201

if __name__ == '__main__':
    print("=== V2: Stateless (JWT Token) ===")
    print("Server không lưu session - mọi request cần token")
    print("http://localhost:5001")
    app.run(debug=True, port=5001)
