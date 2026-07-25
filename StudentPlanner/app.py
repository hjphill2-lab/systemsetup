from flask import Flask, render_template, request, session, redirect, url_for
from database import get_connection
app = Flask(__name__)
app.secret_key = 'studentplanner-secret-key'

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_connection()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM Users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        db.close()
        if user:
            session['UserID'] = user[0]
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
        db = get_connection()
        cursor = db.cursor()
        cursor.execute("INSERT INTO Assignments (UserID, CourseName, Title, Description, DueDate, Completed) VALUES (%s, %s, %s, %s, %s, %s)", (session['UserID'], course_name, title, description, due_date, completed))
        db.commit()
        cursor.close()
        db.close()
        return redirect('/home')
    return render_template('add_assignment.html')

@app.route('/assignments')
def view_assignments():
    db = get_connection()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Assignments WHERE UserID = %s", (session['UserID'],))
    assignments = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('assignments.html', assignments=assignments)

@app.route("/edit_assigment/<int:assignment_id>", methods=["GET", "POST"])
def edit_assigment(assignment_id):
    db = get_connection()
    cursor = db.cursor(dictionary=True)
    if request.method == "POST":
        course_name = request.form['CourseName']
        title = request.form['Title']
        description = request.form['Description']
        due_date = request.form['DueDate']
        completed = 1 if request.form.get("Completed") else 0
        cursor.execute("""UPDATE Assignments SET CourseName = %s, Title = %s, Description = %s, DueDate = %s, Completed = %s 
        WHERE AssignmentID = %s""", (course_name, title, description, due_date, completed, assignment_id))
        db.commit()
        cursor.close()
        db.close()
        return redirect(url_for("home"))

    cursor.execute("""SELECT AssignmentID, CourseName, Title, Description, DueDate, Completed 
    FROM Assignments WHERE AssignmentID = %s""", (assignment_id,))
    assignment = cursor.fetchone()
    cursor.close()
    db.close()
    if assignment is None:
        return "Assignment not found.", 404
    return render_template("edit_assignment.html", assignment=assignment)

if __name__ == '__main__':
    app.run(debug=True)