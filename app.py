import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import date, datetime
from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# SQL Connectivity
db = SQL('sqlite:///library.db')


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    userinfo = db.execute('select * from users where id = ?', session['user_id'])
    username = userinfo[0]['username']
    issues = db.execute('select issues.bookid "bookid", books.bookname "bookname", issues.issuedate "issuedon", issues.issuetime "issuetime", issues.returndate "returndate", issues.fine "fines" from issues natural join books where userid = ? and issues.returndate is null', username)
    return render_template('index.html', username=username, issues=issues)
    # return apology("TODO")


@app.route("/log", methods=["GET", "POST"])
@login_required
def log():
    userinfo = db.execute('select * from users where id = ?', session['user_id'])
    username = userinfo[0]['username']
    issues = db.execute('select issues.bookid "bookid", issues.issuedate "issuedon", issues.issuetime "issuetime", issues.returndate "returndate", issues.fine "fines" from issues where issues.userid = ?', username)
    return render_template('log.html', username=username, issues=issues)



@app.route("/issue", methods=["GET", "POST"])
@login_required
def issue():
    userinfo = db.execute('select * from users where id = ?', session['user_id'])
    username = userinfo[0]['username']
    if request.method == 'GET':
        result = db.execute('select books.bookid "bookid", books.bookname "bookname", authors.authorname "authorname", books.status "status", books.userid "username" from books natural join authors')
        return render_template('issue.html', result=result)
    else:
        check = db.execute('select * from books where bookid like ?', request.form.get('bookid'))
        if not check:
            return apology('Book does not exist', 400)
        else:
            if check[0]['status'] == 'issued':
                flash('Sorry, that book has been issued already!')
                return redirect('/')
            else:
                db.execute('update books set status = "issued" where bookid = ?', request.form.get('bookid'))
                db.execute('update books set userid = ? where bookid = ?', username, request.form.get('bookid'))
                db.execute('insert into issues(userid, bookid) values (?, ?)', username, request.form.get('bookid'))
                flash('Issued!')
                return redirect('/')

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    return render_template('search.html')

@app.route("/searchbook", methods=["GET", "POST"])
@login_required
def searchbook():
    result = db.execute('select books.bookid "bookid", books.bookname "bookname", authors.authorname "authorname", books.status "status", books.userid "username" from books natural join authors where books.bookname like ?', '%' + request.form.get('name') + '%')
    if not result:
        return apology('book does not exist', 400)
    else:
        return render_template('searchbook-result.html', result=result)
    # return apology("TODO")

@app.route("/searchauthor", methods=["GET", "POST"])
@login_required
def searchauthor():
    result = db.execute('select authors.authorid "authorid", authors.authorname "author", count(books.bookid) "bookno" from books natural join authors group by authors.authorid having authors.authorname like ?', '%' + request.form.get('name') + '%')
    if not result:
        return apology('author does not exist', 400)
    else:
        return render_template('searchauthor-result.html', result=result)

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    existing = db.execute('select username from users;')
    if request.method == 'GET':
        return render_template('register.html')
    else:
        if not request.form.get("username"):
            return apology("must provide username", 400)

        elif not request.form.get("password"):
            return apology("must provide password", 400)

        elif request.form.get('password') != request.form.get('confirmation'):
            return apology('password and confirmation do not match', 400)

        else:
            existingusers = []
            for i in existing:
                existingusers.append(i['username'])
            if request.form.get('username') in existingusers:
                return apology('username already exists', 400)

        db.execute('insert into users(username, hash) values(?, ?);', request.form.get('username'), generate_password_hash(request.form.get('password')))
        flash('Registered!')
        return redirect('/login')


@app.route("/return", methods=["GET", "POST"])
@login_required
def returnbook():
    userinfo = db.execute('select * from users where id = ?', session['user_id'])
    username = userinfo[0]['username']
    issues = db.execute('select issues.bookid "bookid", books.bookname "bookname", issues.issuedate "issuedon", issues.issuetime "issuetime", issues.returndate "returndate", issues.fine "fines" from issues natural join books where userid = ? and returndate is null', username)
    if request.method == 'GET':
        return render_template('return.html', username=username, issues=issues)
    else:
        result = db.execute('select books.bookid "bookid", books.bookname "bookname", authors.authorname "authorname", books.status "status", books.userid "username" from books natural join authors where books.bookid like ?', request.form.get('bookid'))
        if not result:
            return apology('book does not exist', 400)
        issuedbooks = []
        for i in issues:
            issuedbooks.append(i['bookid'])
        if request.form.get('bookid') not in issuedbooks:
            return apology('You have not issued this book', 400)
        issue = db.execute('select issuedate from issues where bookid = ?', request.form.get('bookid'))
        issuedate = issue[0]['issuedate']
        rdate = datetime.today()
        days = rdate - datetime.strptime(issuedate, '%Y-%m-%d')
        if days.days > 14:
            fine = (days.days-14)*5
            db.execute('update issues set fine = ? where userid = ? and bookid = ? and returndate is null', fine, username, request.form.get('bookid'))
            flash('You have been fined $' + str(fine), 'for keeping the issued book for more than 2 weeks')
        else:
            flash('Thank you for returning the book on time!')
        db.execute('update issues set returndate = (current_date) where userid = ? and bookid = ?', username, request.form.get('bookid'))
        db.execute('update books set status = "not issued" where bookid = ?', request.form.get('bookid'))
        db.execute('update books set userid = null where bookid = ?', request.form.get('bookid'))
        return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
