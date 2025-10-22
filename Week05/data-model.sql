CREATE TABLE Book (
    book_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    isbn VARCHAR(20) UNIQUE,
    publish_year INT,
    category_id INT REFERENCES Category(category_id),
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE BookCopy (
    copy_id SERIAL PRIMARY KEY,
    book_id INT REFERENCES Book(book_id),
    shelf_location VARCHAR(100),
    status VARCHAR(20) DEFAULT 'available', -- available, loaned, lost
    barcode VARCHAR(50) UNIQUE
);

CREATE TABLE Author (
    author_id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    biography TEXT
);

CREATE TABLE Book_Author (
    book_id INT REFERENCES Book(book_id),
    author_id INT REFERENCES Author(author_id),
    PRIMARY KEY (book_id, author_id)
);

CREATE TABLE Category (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    description TEXT
);

CREATE TABLE Reader (
    reader_id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    address TEXT,
    membership_level VARCHAR(50), -- normal, premium, etc.
    join_date DATE DEFAULT CURRENT_DATE
);

CREATE TABLE Loan (
    loan_id SERIAL PRIMARY KEY,
    reader_id INT REFERENCES Reader(reader_id),
    copy_id INT REFERENCES BookCopy(copy_id),
    staff_id INT REFERENCES Staff(staff_id),
    loan_date DATE DEFAULT CURRENT_DATE,
    due_date DATE,
    return_date DATE,
    status VARCHAR(20) DEFAULT 'ongoing' -- ongoing, returned, overdue
);

CREATE TABLE Staff (
    staff_id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(100) UNIQUE,
    role VARCHAR(50) -- librarian, admin
);

CREATE TABLE Review (
    review_id SERIAL PRIMARY KEY,
    reader_id INT REFERENCES Reader(reader_id),
    book_id INT REFERENCES Book(book_id),
    rating INT CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
