from flask import Flask, render_template, request, redirect, url_for, flash, session
import os

app = Flask(__name__)
app.secret_key = 'super_secret_key'

PREDEFINED_USERS = {"user": "user1", "admin": "admin1"}

def load_users():
    users = {}
    if os.path.exists("users.txt"):
        with open("users.txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if ":" in line:
                    name, pwd = line.split(":", 1)
                    users[name] = pwd
    return users

def save_user(username, password):
    with open("users.txt", "a", encoding="utf-8") as f:
        f.write(f"{username}:{password}\n")

@app.route("/")
def home():
    if "user" in session:
        return redirect(url_for("welcome"))
    return redirect(url_for("login"))

@app.route("/welcome")
def welcome():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("welcome.html", user=session["user"])

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        users = {**PREDEFINED_USERS, **load_users()}

        if username in users and users[username] == password:
            session["user"] = username
            flash(f"Привет, {username}!", "success")
            return redirect(url_for("welcome"))
        flash("Неверный логин или пароль. Зарегистрируйтесь.", "error")
        return redirect(url_for("register"))
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        confirm = request.form.get("password_confirm", "").strip()

        if not username or not password:
            flash("Поля не должны быть пустыми.", "error")
            return redirect(url_for("register"))
        if password != confirm:
            flash("Пароли не совпадают.", "error")
            return redirect(url_for("register"))

        users = {**PREDEFINED_USERS, **load_users()}
        if username in users:
            flash("Такой пользователь уже существует.", "error")
            return redirect(url_for("login"))

        save_user(username, password)
        flash("Регистрация успешна! Теперь войдите.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/logout")
def logout():
    user = session.pop("user", None)
    if user:
        flash(f"Пользователь {user} вышел из системы.", "success")
    return redirect(url_for("login"))

if __name__ == '__main__':
    if not os.path.exists("users.txt"):
        with open("users.txt", "w", encoding="utf-8") as f:
            f.write("user:user1\nadmin:admin1\n")
    app.run(debug=True)
