import mysql.connector

def get_connection():
    connection = mysql.connector.connect(
        host="107.180.1.16",
        port=3306,
        user="cis440sum26team9",
        password="cis440sum26team9",
        database="cis440sum26team9"
    )
    return connection

if __name__ == "__main__":
    db = get_connection()  
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Users")
    result = cursor.fetchall()
    for user in result:
        print(user)
    cursor.close()
    db.close()