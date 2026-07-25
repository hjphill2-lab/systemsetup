from flask import Flask, render_template, request, session, redirect
from database import get_connection

app = Flask(__name__)
app.secret_key = 'studentplanner-secret-key'

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check user credentials in the database
        db = get_connection()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM Users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        db.close()

        if user:
            session['UserID'] = user[0]  # Store UserID in session
            return render_template("home.html")
        else:
            return "Invalid username or password."
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        # Insert user data into the database
        db = get_connection()
        cursor = db.cursor()
        cursor.execute("INSERT INTO Users (username, password, email) VALUES (%s, %s, %s)", (username, password, email))
        db.commit()
        cursor.close()
        db.close()

        return "Registration successful!"
    return render_template('register.html')

@app.route('/home')
def home():
    return render_template("home.html")

@app.route('/add_assignment', methods=['GET', 'POST'])
def add_assignment():
    if request.method == 'POST':
        course_name = request.form['CourseName']
        title = request.form['Title']
        description = request.form['Description']
        due_date = request.form['DueDate']
        completed = 'Completed' in request.form

        # Insert assignment data into the database
        db = get_connection()
        cursor = db.cursor()
        cursor.execute("INSERT INTO Assignments (UserID, CourseName, Title, Description, DueDate, Completed) VALUES (%s, %s, %s, %s, %s, %s)", (session['UserID'], course_name, title, description, due_date, completed))
        db.commit()
        cursor.close()
        db.close()

        return redirect('/home')  # Redirect to the home page after adding
    return render_template('add_assignment.html')

if __name__ == '__main__':
    app.run(debug=True)
