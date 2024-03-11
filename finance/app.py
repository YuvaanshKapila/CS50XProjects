import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__, template_folder="templates")
app.jinja_env.filters["usd"] = usd
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

db.execute(
    """
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        symbol TEXT NOT NULL,
        shares INTEGER NOT NULL,
        price REAL NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """
)


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    user_id = session["user_id"]

    user_cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]

    transactions = db.execute(
        "SELECT symbol, SUM(shares) as shares FROM transactions WHERE user_id = ? GROUP BY symbol HAVING SUM(shares) > 0",
        user_id,
    )

    stocks = []
    total_value = user_cash

    for transaction in transactions:
        quote_data = lookup(transaction["symbol"])
        shares = transaction["shares"]
        total_price = quote_data["price"] * shares
        total_value += total_price
        stocks.append(
            {
                "symbol": transaction["symbol"],
                "name": quote_data["name"],
                "shares": shares,
                "price": quote_data["price"],
                "total_price": total_price,
            }
        )

    return render_template(
        "index.html", stocks=stocks, cash=user_cash, total_value=total_value
    )


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = int(request.form.get("shares"))

        if not symbol:
            return apology("must provide symbol", 400)
        if not shares or shares <= 0:
            return apology("must provide valid number of shares", 400)

        quote_data = lookup(symbol)
        if quote_data is None:
            return apology("invalid symbol", 400)

        cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0][
            "cash"
        ]
        total_cost = quote_data["price"] * shares

        if total_cost > cash:
            return apology("not enough cash", 400)

        db.execute(
            "INSERT INTO transactions (user_id, symbol, shares, price, timestamp) VALUES (?, ?, ?, ?, datetime('now'))",
            session["user_id"],
            quote_data["symbol"],
            shares,
            quote_data["price"],
        )

        db.execute(
            "UPDATE users SET cash = cash - ? WHERE id = ?",
            total_cost,
            session["user_id"],
        )

        return redirect("/")

    return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    user_id = session["user_id"]
    transactions = db.execute(
        "SELECT symbol, shares, price, timestamp FROM transactions WHERE user_id = ? ORDER BY timestamp DESC",
        user_id,
    )
    return render_template("history.html", transactions=transactions)


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
    # Clear the user's session
    session.clear()

    # Redirect user to the login form
    return redirect("/login")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    if request.method == "POST":
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("must provide symbol", 400)

        quote_data = lookup(symbol)
        if quote_data is None:
            return apology("invalid symbol", 400)

        return render_template("quoted.html", quote_data=quote_data)

    return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    # Rest of the code for handling the registration form submission

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must confirm password", 400)

        # Ensure password and confirmation match
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match", 400)

        # Hash the password
        hashed_password = generate_password_hash(request.form.get("password"))

        # Insert the new user into the database
        result = db.execute(
            "INSERT INTO users (username, hash) VALUES (?, ?)",
            request.form.get("username"),
            hashed_password,
        )

        # Check if insertion was successful
        if not result:
            return apology("username already exists", 400)

        # Log in the newly registered user
        session["user_id"] = result

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        if not symbol:
            return apology("must select a symbol", 400)
        if not shares:
            return apology("must provide shares", 400)

        try:
            shares = int(shares)
        except ValueError:
            return apology("shares must be a positive integer", 400)

        if shares <= 0:
            return apology("shares must be a positive integer", 400)

        user_id = session["user_id"]
        user_shares = db.execute(
            "SELECT SUM(shares) AS total_shares FROM transactions WHERE user_id = ? AND symbol = ?",
            user_id,
            symbol,
        )[0]["total_shares"]

        if user_shares is None or user_shares < shares:
            return apology("insufficient shares to sell", 400)

        quote_data = lookup(symbol)
        if quote_data is None:
            return apology("invalid symbol", 400)

        total_gain = quote_data["price"] * shares
        db.execute(
            "INSERT INTO transactions (user_id, symbol, shares, price) VALUES (?, ?, ?, ?)",
            user_id,
            quote_data["symbol"],
            -shares,
            quote_data["price"],
        )
        db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", total_gain, user_id)

        return redirect("/")
    else:
        user_id = session["user_id"]
        symbols = db.execute(
            "SELECT DISTINCT symbol FROM transactions WHERE user_id = ?", user_id
        )
        return render_template("sell.html", symbols=symbols)


@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        # Retrieve current password from the form
        current_password = request.form.get("current_password")

        # Retrieve new password and confirmation from the form
        new_password = request.form.get("new_password")
        confirmation = request.form.get("confirmation")

        # Query the database for the current user's information
        user = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])[0]

        # Check if the current password is correct
        if not check_password_hash(user["hash"], current_password):
            return apology("Incorrect current password", 403)

        # Check if new password and confirmation match
        if new_password != confirmation:
            return apology("Passwords do not match", 403)

        # Update the user's password in the database
        db.execute(
            "UPDATE users SET hash = ? WHERE id = ?",
            generate_password_hash(new_password),
            session["user_id"],
        )

        # Redirect to the home page
        return redirect("/")

    return render_template("change_password.html")


if __name__ == "__main__":
    app.run()
