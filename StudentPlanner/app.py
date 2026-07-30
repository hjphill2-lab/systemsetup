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

        cursor.execute(
            """
            SELECT UserID, username, password, email, Role, Active
            FROM Users
            WHERE username = %s
            """,
            (username,)
        )

        user = cursor.fetchone()

        cursor.close()
        db.close()

        if user is None:
            return "Invalid username or password."

        if user[2] != password:
            return "Invalid username or password."

        if not user[5]:
            return "This account has been deactivated."

        session['UserID'] = user[0]
        session['username'] = user[1]
        session['role'] = user[4]

        return redirect('/home')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        db = get_connection()
        cursor = db.cursor()

        cursor.execute(
            """
            INSERT INTO Users (username, password, email)
            VALUES (%s, %s, %s)
            """,
            (username, password, email)
        )

        db.commit()
        cursor.close()
        db.close()

        return redirect('/')

    return render_template('register.html')

@app.route('/home')
def home():
    if 'UserID' not in session:
        return redirect('/')

    db = get_connection()
    cursor = db.cursor()

    cursor.execute(
        """
        SELECT CourseName, Title, DueDate
        FROM Assignments
        WHERE UserID = %s
        AND Completed = 0
        AND DueDate BETWEEN CURDATE()
        AND DATE_ADD(CURDATE(), INTERVAL 7 DAY)
        ORDER BY DueDate
        """,
        (session['UserID'],)
    )

    reminders = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template("home.html", reminders=reminders)


@app.route('/add_assignment', methods=['GET', 'POST'])
def add_assignment():
    if 'UserID' not in session:
        return redirect('/')

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
    if 'UserID' not in session:
        return redirect('/')

    db = get_connection()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Assignments WHERE UserID = %s", (session['UserID'],))
    assignments = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('assignments.html', assignments=assignments)

@app.route('/complete_assignment/<int:assignment_id>')
def complete_assignment(assignment_id):
    if 'UserID' not in session:
        return redirect('/')

    db = get_connection()
    cursor = db.cursor()
    cursor.execute("UPDATE Assignments SET Completed = 1 WHERE AssignmentID = %s AND UserID = %s", (assignment_id, session['UserID']))
    db.commit()
    cursor.close()
    db.close()
    return redirect('/assignments')


@app.route("/edit_assignment/<int:assignment_id>", methods=["GET", "POST"])
def edit_assignment(assignment_id):
    if 'UserID' not in session:
        return redirect('/')

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    if request.method == "POST":
        course_name = request.form['CourseName']
        title = request.form['Title']
        description = request.form['Description']
        due_date = request.form['DueDate']
        completed = 1 if request.form.get("Completed") else 0

        cursor.execute(
            """
            UPDATE Assignments
            SET CourseName = %s,
                Title = %s,
                Description = %s,
                DueDate = %s,
                Completed = %s
            WHERE AssignmentID = %s
            AND UserID = %s
            """,
            (
                course_name,
                title,
                description,
                due_date,
                completed,
                assignment_id,
                session['UserID']
            )
        )

        db.commit()
        cursor.close()
        db.close()

        return redirect(url_for("home"))

    cursor.execute(
        """
        SELECT AssignmentID, CourseName, Title, Description, DueDate, Completed
        FROM Assignments
        WHERE AssignmentID = %s
        AND UserID = %s
        """,
        (assignment_id, session['UserID'])
    )

    assignment = cursor.fetchone()

    cursor.close()
    db.close()

    if assignment is None:
        return "Assignment not found.", 404

    return render_template(
        "edit_assignment.html",
        assignment=assignment
    )

@app.route('/manage_users')
def manage_users():
    if 'UserID' not in session:
        return redirect('/')

    if session.get('role') != 'admin':
        return redirect('/home')

    db = get_connection()
    cursor = db.cursor()

    cursor.execute(
        """
        SELECT UserID, username, email, Role, Active
        FROM Users
        ORDER BY username
        """
    )

    users = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('manage_users.html', users=users)

@app.route('/deactivate_user/<int:user_id>')
def deactivate_user(user_id):
    if 'UserID' not in session:
        return redirect('/')

    if session.get('role') != 'admin':
        return redirect('/home')

    if session['UserID'] == user_id:
        return "You cannot deactivate your own account."

    db = get_connection()
    cursor = db.cursor()

    cursor.execute(
        """
        UPDATE Users
        SET Active = FALSE
        WHERE UserID = %s
        """,
        (user_id,)
    )

    db.commit()
    cursor.close()
    db.close()

    return redirect('/manage_users')

@app.route('/activate_user/<int:user_id>')
def activate_user(user_id):
    if 'UserID' not in session:
        return redirect('/')

    if session.get('role') != 'admin':
        return redirect('/home')

    db = get_connection()
    cursor = db.cursor()

    cursor.execute(
        """
        UPDATE Users
        SET Active = TRUE
        WHERE UserID = %s
        """,
        (user_id,)
    )

    db.commit()
    cursor.close()
    db.close()

    return redirect('/manage_users')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)