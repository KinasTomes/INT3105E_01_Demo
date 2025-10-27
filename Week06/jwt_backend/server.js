const express = require("express");
const jwt = require("jsonwebtoken");
const bodyParser = require("body-parser");

const app = express();
app.use(bodyParser.json());

// ------------------------
// JWT Configuration
// ------------------------
const SECRET_KEY = "hello-nigeria";
const ACCESS_TOKEN_EXPIRE_MINUTES = 30;

// Fake users & books database
const users = {
  admin: "admin123",
  user: "user123"
};

let books = [
  { id: 1, title: "Python Programming", author: "John Doe", year: 2023, isbn: "978-0123456789" },
  { id: 2, title: "Web Development", author: "Jane Smith", year: 2024, isbn: "978-0987654321" },
  { id: 3, title: "Data Science", author: "Bob Johnson", year: 2023, isbn: "978-1122334455" }
];

// ------------------------
// JWT Helper functions
// ------------------------
function createAccessToken(username) {
  return jwt.sign(
    { sub: username },
    SECRET_KEY,
    { expiresIn: `${ACCESS_TOKEN_EXPIRE_MINUTES}m` }
  );
}

function verifyToken(req, res, next) {
  const authHeader = req.headers["authorization"];
  if (!authHeader) {
    return res.status(401).json({ detail: "Authorization header missing" });
  }

  const token = authHeader.split(" ")[1];
  if (!token) {
    return res.status(401).json({ detail: "Bearer token missing" });
  }

  jwt.verify(token, SECRET_KEY, (err, decoded) => {
    if (err) {
      if (err.name === "TokenExpiredError") {
        return res.status(401).json({ detail: "Token has expired" });
      }
      return res.status(401).json({ detail: "Invalid token" });
    }
    req.username = decoded.sub;
    next();
  });
}

// ------------------------
// API Endpoints
// ------------------------

app.get("/", (req, res) => {
  res.json({
    message: "Book Management API with JWT (Node.js)",
    login: "POST /login with {username, password}",
    docs: "No Swagger here, but works the same way!"
  });
});

// 1️⃣ Login - Generate JWT
app.post("/login", (req, res) => {
  const { username, password } = req.body;

  if (!users[username] || users[username] !== password) {
    return res.status(401).json({ detail: "Incorrect username or password" });
  }

  const token = createAccessToken(username);
  res.json({ access_token: token, token_type: "bearer" });
});

// 2️⃣ Get all books
app.get("/books", verifyToken, (req, res) => {
  res.json(books);
});

// 3️⃣ Get one book
app.get("/books/:id", verifyToken, (req, res) => {
  const id = parseInt(req.params.id);
  const book = books.find((b) => b.id === id);
  if (!book) return res.status(404).json({ detail: "Book not found" });
  res.json(book);
});

// 4️⃣ Add new book
app.post("/books", verifyToken, (req, res) => {
  const { title, author, year, isbn } = req.body;
  const id = books.length ? Math.max(...books.map((b) => b.id)) + 1 : 1;
  const newBook = { id, title, author, year, isbn };
  books.push(newBook);
  res.status(201).json(newBook);
});

// 5️⃣ Update book
app.put("/books/:id", verifyToken, (req, res) => {
  const id = parseInt(req.params.id);
  const index = books.findIndex((b) => b.id === id);
  if (index === -1) return res.status(404).json({ detail: "Book not found" });

  books[index] = { ...books[index], ...req.body };
  res.json(books[index]);
});

// 6️⃣ Delete book
app.delete("/books/:id", verifyToken, (req, res) => {
  const id = parseInt(req.params.id);
  const index = books.findIndex((b) => b.id === id);
  if (index === -1) return res.status(404).json({ detail: "Book not found" });

  books.splice(index, 1);
  res.status(204).send();
});

// ------------------------
// Start server
// ------------------------
const PORT = 8000;
app.listen(PORT, () => {
  console.log(`=== Book Management API with JWT ===`);
  console.log(`Running on http://localhost:${PORT}`);
  console.log(`Login credentials: admin/admin123 or user/user123`);
});
