# Library Management System

A web-based **Library Management System** built with **Python Flask, MySQL, HTML, CSS, and JavaScript**.

The system allows students to request and return books, while librarians can manage books, approve requests, manage students, and view transaction history.

## Requirements

* Python 3.x
* Flask
* MySQL
* MySQL Connector
* Werkzeug

## Installation

Install the required Python modules:

```bash
pip install flask mysql-connector-python werkzeug
```

## Database Setup

Create a MySQL database named:

```sql
CREATE DATABASE library_db;
```

Create the required tables for users, books, and transactions before running the application.

Update the MySQL connection details in `app.py` according to your MySQL setup.

## Run

Run the Flask application:

```bash
python app.py
```

Then open the application in your browser:

```text
http://127.0.0.1:5000
```

## Features

* Student and Librarian accounts
* User registration and login
* Password hashing
* Role-based access
* Add, edit, and delete books
* Search books by title or author
* Request books
* Approve book requests
* Return books
* Transaction history
* Student management
* User profile management
* Flash messages for notifications

## How It Works

### Student

Students can:

* Register and log in
* Search for books
* Request available books
* Return borrowed books
* View their transaction history
* Update their profile

### Librarian

Librarians can:

* Add new books
* Edit book information
* Delete books
* Approve student book requests
* Mark books as returned
* View all transaction history
* View registered students
* Manage their profile

## Project Structure

```text
Library-Management-System/
│
├── app.py
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── dashboard.html
│   ├── profile.html
│   ├── history.html
│   ├── edit_book.html
│   └── students.html
│
└── static/
    ├── style.css
    └── script.js
```

## Technologies Used

* **Python**
* **Flask**
* **MySQL**
* **HTML**
* **CSS**
* **JavaScript**
