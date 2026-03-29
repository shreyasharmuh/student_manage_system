from flask import Flask, render_template, request, redirect
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "shreyash_sharma" # Change this to a random secret key

# Create DB + Table
def init_db():
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            course TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Home route (READ data)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == 'admin123':
            session['user'] = username
            return redirect(url_for('index'))
        else:
            return "Invalid Credentials"

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/')
def index():
    if 'user' not in session:
     return redirect(url_for('login'))

    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    total_students = len(students)
    courses = set([s[3] for s in students])
    total_courses = len(courses)
    latest_student = students[-1][1] if students else "None"

    conn.close()

    return render_template(
        'index.html',
        students=students,
        total_students=total_students,
        total_courses=total_courses,
        latest_student=latest_student
    )
# Add Student (INSERT)
@app.route('/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name'].title()
        age = request.form['age']
        course = request.form['course'].upper()

        conn = sqlite3.connect('students.db')
        c = conn.cursor()
        c.execute("INSERT INTO students (name, age, course) VALUES (?, ?, ?)",
                  (name, age, course))
        conn.commit()
        conn.close()

        return redirect('/')

    return render_template('add.html')

@app.route('/delete/<int:id>')
def delete_student(id):
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    c.execute("DELETE FROM students WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    conn = sqlite3.connect('students.db')
    c = conn.cursor()

    if request.method == 'POST':
        name = request.form['name'].title()
        age = request.form['age']
        course = request.form['course'].upper()

        c.execute("UPDATE students SET name=?, age=?, course=? WHERE id=?",
                  (name, age, course, id))
        conn.commit()
        conn.close()
        return redirect('/')

    c.execute("SELECT * FROM students WHERE id=?", (id,))
    student = c.fetchone()
    conn.close()

    return render_template('edit.html', student=student)

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)