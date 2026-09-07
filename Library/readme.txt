## Database Setup

Create the MySQL database:

```sql
CREATE DATABASE library_db;
USE library_db;
```

### Create Users Table

```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role ENUM('student', 'librarian') NOT NULL,
    full_name VARCHAR(100),
    email VARCHAR(100)
);
```

### Create Books Table

```sql
CREATE TABLE books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'available',
    requested_by INT DEFAULT NULL,
    issued_to INT DEFAULT NULL,
    FOREIGN KEY (requested_by) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (issued_to) REFERENCES users(id) ON DELETE SET NULL
);
```

### Create Transactions Table

```sql
CREATE TABLE transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT NOT NULL,
    user_id INT NOT NULL,
    action VARCHAR(50) NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

After creating the database and tables, update the MySQL connection details in `app.py`:

```python
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="your_password",
        database="library_db"
    )
```

Then run the Flask application:

```bash
python app.py
```

Open the application in your browser:

```text
http://127.0.0.1:5000
```
