from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "super_secret_key"

def get_db():
    return mysql.connector.connect(host="localhost", user="root", password="root@123", database="library_db")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        db.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['role'] = user['role']
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials")
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    username, password, role = request.form['username'], request.form['password'], request.form['role']
    full_name, email = request.form['full_name'], request.form['email']
    admin_code = request.form.get('admin_code', '')

    if role == 'librarian' and admin_code != 'devil':
        flash("Invalid Librarian Code!")
        return redirect(url_for('index'))

    hashed_password = generate_password_hash(password)
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password, role, full_name, email) VALUES (%s, %s, %s, %s, %s)", 
                       (username, hashed_password, role, full_name, email))
        db.commit()
        flash("Registered successfully!")
    except:
        flash("Username already exists!")
    db.close()
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# --- COMMON: PROFILE MANAGEMENT ---
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session: return redirect(url_for('index'))
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    if request.method == 'POST':
        cursor.execute("UPDATE users SET full_name=%s, email=%s WHERE id=%s", 
                       (request.form['full_name'], request.form['email'], session['user_id']))
        db.commit()
        flash("Profile updated!")
        
    cursor.execute("SELECT * FROM users WHERE id=%s", (session['user_id'],))
    user = cursor.fetchone()
    db.close()
    return render_template('profile.html', user=user)

# --- CATALOG & SEARCH DASHBOARD ---
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session: return redirect(url_for('index'))
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # LIBRARIAN: Add Book
    if request.method == 'POST' and session['role'] == 'librarian':
        cursor.execute("INSERT INTO books (title, author) VALUES (%s, %s)", (request.form['title'], request.form['author']))
        db.commit()

    # SEARCH & FILTER (Works for both roles)
    search_query = request.args.get('search', '')
    if search_query:
        cursor.execute("""
            SELECT b.*, u1.username as requested_by_name, u2.username as issued_to_name 
            FROM books b 
            LEFT JOIN users u1 ON b.requested_by = u1.id 
            LEFT JOIN users u2 ON b.issued_to = u2.id 
            WHERE b.title LIKE %s OR b.author LIKE %s
        """, ('%' + search_query + '%', '%' + search_query + '%'))
    else:
        cursor.execute("""
            SELECT b.*, u1.username as requested_by_name, u2.username as issued_to_name 
            FROM books b 
            LEFT JOIN users u1 ON b.requested_by = u1.id 
            LEFT JOIN users u2 ON b.issued_to = u2.id
        """)
    books = cursor.fetchall()
    db.close()
    return render_template('dashboard.html', books=books, search_query=search_query)

# --- WORKFLOW: REQUEST -> ISSUE -> RETURN ---
@app.route('/request_book/<int:id>')
def request_book(id):
    if session.get('role') == 'student':
        db = get_db()
        db.cursor().execute("UPDATE books SET status='requested', requested_by=%s WHERE id=%s", (session['user_id'], id))
        db.commit()
        db.close()
    return redirect(url_for('dashboard'))

@app.route('/approve_book/<int:id>')
def approve_book(id):
    if session.get('role') == 'librarian':
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT requested_by FROM books WHERE id=%s", (id,))
        student_id = cursor.fetchone()['requested_by']
        
        # Update book status and add to transaction history
        cursor.execute("UPDATE books SET status='issued', issued_to=%s, requested_by=NULL WHERE id=%s", (student_id, id))
        cursor.execute("INSERT INTO transactions (book_id, student_id, action) VALUES (%s, %s, 'issued')", (id, student_id))
        db.commit()
        db.close()
    return redirect(url_for('dashboard'))

@app.route('/return_book/<int:id>')
def return_book(id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT issued_to FROM books WHERE id=%s", (id,))
    student_id = cursor.fetchone()['issued_to']
    
    # Reset book and log return in history
    cursor.execute("UPDATE books SET status='available', issued_to=NULL WHERE id=%s", (id,))
    cursor.execute("INSERT INTO transactions (book_id, student_id, action) VALUES (%s, %s, 'returned')", (id, student_id))
    db.commit()
    db.close()
    return redirect(url_for('dashboard'))

# --- HISTORY / TRANSACTIONS ---
@app.route('/history')
def history():
    if 'user_id' not in session: return redirect(url_for('index'))
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # Librarians see all history, Students only see their own
    if session['role'] == 'librarian':
        cursor.execute("SELECT t.*, b.title, u.username FROM transactions t JOIN books b ON t.book_id = b.id JOIN users u ON t.student_id = u.id ORDER BY t.transaction_date DESC")
    else:
        cursor.execute("SELECT t.*, b.title, u.username FROM transactions t JOIN books b ON t.book_id = b.id JOIN users u ON t.student_id = u.id WHERE t.student_id = %s ORDER BY t.transaction_date DESC", (session['user_id'],))
        
    logs = cursor.fetchall()
    db.close()
    return render_template('history.html', logs=logs)


# --- BOOK MANAGEMENT (EDIT & DELETE) ---
@app.route('/edit_book/<int:id>', methods=['GET', 'POST'])
def edit_book(id):
    if session.get('role') != 'librarian': 
        return redirect(url_for('dashboard'))
        
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    if request.method == 'POST':
        cursor.execute("UPDATE books SET title=%s, author=%s WHERE id=%s", 
                       (request.form['title'], request.form['author'], id))
        db.commit()
        db.close()
        flash("Book updated successfully!")
        return redirect(url_for('dashboard'))
        
    cursor.execute("SELECT * FROM books WHERE id=%s", (id,))
    book = cursor.fetchone()
    db.close()
    return render_template('edit_book.html', book=book)

@app.route('/delete_book/<int:id>')
def delete_book(id):
    if session.get('role') == 'librarian':
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM books WHERE id=%s", (id,))
        db.commit()
        db.close()
        flash("Book deleted!")
    return redirect(url_for('dashboard'))


@app.route('/students')
def students():
    if session.get('role') != 'librarian': 
        return redirect(url_for('dashboard'))
        
    db = get_db()
    cursor = db.cursor(dictionary=True)
    # Fetch all registered students
    cursor.execute("SELECT id, username, full_name, email FROM users WHERE role='student'")
    student_list = cursor.fetchall()
    db.close()
    return render_template('students.html', students=student_list)

if __name__ == '__main__':
    app.run(debug=True)