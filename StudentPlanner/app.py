from flask import Flask, render_template, request
from database import get_connection

app = Flask(__name__)

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
            return "Login successful!"
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

if __name__ == '__main__':
    app.run(debug=True)

