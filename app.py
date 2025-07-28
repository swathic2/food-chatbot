from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import pandas as pd
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  

df = pd.read_csv("data/recipes.csv")

def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    with conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
    conn.close()

init_db()

@app.route("/")
def root():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password", "error")
    
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if not username or not password:
            flash("Username and password are required", "error")
            return render_template("signup.html")

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        try:
            conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashed_password)
            )
            conn.commit()
            flash("Signup successful! Please log in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Username already taken", "error")
            return render_template("signup.html")
        finally:
            conn.close()

    return render_template("signup.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("index.html", username=session.get("username"))

@app.route("/recommend", methods=["POST"])
def recommend():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_ingredients = request.form["ingredients"].lower()
    recommendations = []

    for idx, row in df.iterrows():
        if all(ingredient.strip() in row["Cleaned_Ingredients"].lower() for ingredient in user_ingredients.split(",")):
            image_filename = os.path.basename(row["Image_Name"])
            if not image_filename.endswith(".jpg"):
                image_filename += ".jpg"

            recommendations.append({
                "title": row["Title"],
                "ingredients": row["Cleaned_Ingredients"],
                "instructions": row["Instructions"],
                "image": image_filename
            })

        if len(recommendations) >= 5:
            break

    return jsonify(recommendations)

if __name__ == "__main__":
    app.run(debug=True)
