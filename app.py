import os
from mssql_python import connect
from flask import Flask, render_template, request, redirect, url_for, session
import secrets


def get_db_connection():
    connection = connect(
        "Server=localhost\\MSSQLSERVER01;"
        "Database=Tehilim Together;"
        "Trusted_Connection=yes;"
    )

    return connection


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config if it exists
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)


    @app.route('/home.html')
    def hello():
        return render_template("home.html")

    @app.route('/create_group.html', methods=['GET', 'POST'])
    def create_group():

        if request.method == 'POST':
            name = request.form.get('custom_name')
            group_category = request.form.get('group_name')

            book_code = secrets.token_urlsafe(8)

            connection = get_db_connection()
            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO dbo.BOOK
                    (BOOK_DATE_CREATED, BOOK_NAME, USER_ID, GROUP_CATEGORY, BOOK_CODE)
                    OUTPUT INSERTED.BOOK_ID
                VALUES (GETDATE(), ?, ?, ?, ?)
                """,
                (
                    name,
                    session['user_id'],
                    group_category,
                    book_code
                )
            )

            book_id = cursor.fetchone()[0]

            connection.commit()
            connection.close()

            return redirect(
                url_for('group', book_id=book_id)
            )

        return render_template("create_group.html")

    @app.route('/join/<book_code>', methods=['GET', 'POST'])
    def join_book(book_code):

        if 'user_id' not in session:
            return redirect(url_for('login'))

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT BOOK_ID, BOOK_NAME
            FROM dbo.BOOK
            WHERE BOOK_CODE = ?
            """,
            (book_code,)
        )

        book = cursor.fetchone()

        if not book:
            connection.close()
            return "Book not found."

        book_id = book[0]
        book_name = book[1]

        if request.method == 'POST':
            cursor.execute(
                """
                IF NOT EXISTS (
                    SELECT 1
                    FROM BOOK_USER
                    WHERE BOOK_ID = ? AND USER_ID = ?
                )
                INSERT INTO BOOK_USER (BOOK_ID, USER_ID)
                VALUES (?, ?)
                """,
                (
                    book_id,
                    session['user_id'],
                    book_id,
                    session['user_id']
                )
            )

            connection.commit()
            connection.close()

            return redirect(
                url_for('group', book_id=book_id)
            )

        connection.close()

        return render_template(
            "join_book.html",
            book_name=book_name,
            book_code=book_code
        )

    @app.route("/group_info.html")
    def group():

        hebrew_numbers = [
            "א׳", "ב׳", "ג׳", "ד׳", "ה׳", "ו׳", "ז׳", "ח׳", "ט׳", "י׳",
            "י״א", "י״ב", "י״ג", "י״ד", "ט״ו", "ט״ז", "י״ז", "י״ח", "י״ט", "כ׳",
            "כ״א", "כ״ב", "כ״ג", "כ״ד", "כ״ה", "כ״ו", "כ״ז", "כ״ח", "כ״ט", "ל׳",
            "ל״א", "ל״ב", "ל״ג", "ל״ד", "ל״ה", "ל״ו", "ל״ז", "ל״ח", "ל״ט", "מ׳",
            "מ״א", "מ״ב", "מ״ג", "מ״ד", "מ״ה", "מ״ו", "מ״ז", "מ״ח", "מ״ט", "נ׳",
            "נ״א", "נ״ב", "נ״ג", "נ״ד", "נ״ה", "נ״ו", "נ״ז", "נ״ח", "נ״ט", "ס׳",
            "ס״א", "ס״ב", "ס״ג", "ס״ד", "ס״ה", "ס״ו", "ס״ז", "ס״ח", "ס״ט", "ע׳",
            "ע״א", "ע״ב", "ע״ג", "ע״ד", "ע״ה", "ע״ו", "ע״ז", "ע״ח", "ע״ט", "פ׳",
            "פ״א", "פ״ב", "פ״ג", "פ״ד", "פ״ה", "פ״ו", "פ״ז", "פ״ח", "פ״ט", "צ׳",
            "צ״א", "צ״ב", "צ״ג", "צ״ד", "צ״ה", "צ״ו", "צ״ז", "צ״ח", "צ״ט", "ק׳",
            "ק״א", "ק״ב", "ק״ג", "ק״ד", "ק״ה", "ק״ו", "ק״ז", "ק״ח", "ק״ט", "קי׳",
            "קי״א", "קי״ב", "קי״ג", "קי״ד", "קט״ו", "קט״ז", "קי״ז", "קי״ח", "קי״ט", "ק״כ",
            "קכ״א", "קכ״ב", "קכ״ג", "קכ״ד", "קכ״ה", "קכ״ו", "קכ״ז", "קכ״ח", "קכ״ט", "ק״ל",
            "קל״א", "קל״ב", "קל״ג", "קל״ד", "קל״ה", "קל״ו", "קל״ז", "קל״ח", "קל״ט", "ק״מ",
            "קמ״א", "קמ״ב", "קמ״ג", "קמ״ד", "קמ״ה", "קמ״ו", "קמ״ז", "קמ״ח", "קמ״ט", "ק״נ"
        ]

        perakim = []

        for number in range(1, 151):
            perakim.append({
                "number": number,
                "hebrew": hebrew_numbers[number - 1]
            })

        book_id = request.args.get('book_id')

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT BOOK_NAME, GROUP_CATEGORY, BOOK_CODE
            FROM dbo.BOOK
            WHERE BOOK_ID = ?
            """,
            (book_id,)
        )

        book = cursor.fetchone()

        name = book[0] if book else None
        group_category = book[1] if book else None
        book_code = book[2] if book else None

        cursor.execute(
            """
            SELECT PERAK_ID
            FROM BOOK_PERAK
            WHERE BOOK_ID = ?
            """,
            (book_id,)
        )

        completed_perakim = [row[0] for row in cursor.fetchall()]

        connection.close()

        return render_template(
            "group_info.html",
            perakim=perakim,
            name=name,
            group_category=group_category,
            book_id=book_id,
            completed_perakim=completed_perakim,
            book_code=book_code
        )

    @app.route('/submit-progress', methods=['POST'])
    def submit_progress():

        book_id = request.form.get('book_id')
        perakim = request.form.getlist('perakim')

        connection = get_db_connection()
        cursor = connection.cursor()

        for perek in perakim:
            cursor.execute(
                """
                IF NOT EXISTS (
                    SELECT 1
                    FROM BOOK_PERAK
                    WHERE BOOK_ID = ? AND PERAK_ID = ?
                )
                INSERT INTO BOOK_PERAK (BOOK_ID, PERAK_ID)
                VALUES (?, ?)
                """,
                (book_id, perek, book_id, perek)
            )

        connection.commit()
        connection.close()

        return redirect(
            url_for('group', book_id=book_id)
        )

    @app.route('/', methods=['GET', 'POST'])
    def login():

        if 'user_id' in session:
            return redirect(url_for('hello'))

        if request.method == 'POST':
            phone = request.form.get('phone')
            password = request.form.get('password')

            connection = get_db_connection()
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT USER_ID
                FROM dbo.[USER]
                WHERE USER_PHONE = ? AND USER_PASS = ?
                """,
                (phone, password)
            )

            user = cursor.fetchone()

            connection.close()

            if user:
                session['user_id'] = user[0]
                return redirect(url_for('hello'))

            return "Incorrect phone number or password."

        return render_template("login.html")

    @app.route('/create_account.html', methods=['GET', 'POST'])
    def register():

        if request.method == 'POST':
            print("FORM DATA:", request.form)

            name = request.form.get('name')
            phone = request.form.get('phone')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')

            print("PASSWORD:", password)
            print("CONFIRM PASSWORD:", confirm_password)

            if password != confirm_password:
                return "Passwords do not match."

            connection = get_db_connection()
            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO dbo.[USER] (USER_NAME, USER_PHONE, USER_PASS)
                VALUES (?, ?, ?)
                """,
                (name, phone, password)
            )

            connection.commit()
            connection.close()

            return redirect(url_for('login'))

        return render_template("create_account.html")

    @app.route('/past_books.html', methods=['GET'])
    def books():

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT BOOK_ID, BOOK_NAME, BOOK_DATE_CREATED, BOOK_DATE_COMPLETED
            FROM dbo.BOOK
            WHERE USER_ID = ?
            """,
            (session['user_id'],)
        )

        books = cursor.fetchall()

        connection.close()

        return render_template("past_books.html", books=books)

    @app.route('/delete_book', methods=['POST'])
    def delete_book():

        book_id = request.form.get('book_id')

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE
            FROM BOOK_PERAK
            WHERE BOOK_ID = ?
            """,
            (book_id,)
        )

        cursor.execute(
            """
            DELETE
            FROM BOOK_USER
            WHERE BOOK_ID = ?
            """,
            (book_id,)
        )

        cursor.execute(
            """
            DELETE
            FROM BOOK
            WHERE BOOK_ID = ?
              AND USER_ID = ?
            """,
            (book_id, session['user_id'])
        )

        connection.commit()
        connection.close()

        return redirect(url_for('books'))

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)