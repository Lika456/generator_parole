from flask import Flask, render_template, request, redirect, url_for, flash, session
import random
import os

app = Flask(__name__)
app.secret_key = "secretkey"

PREDEFINED_USERS = {
    "user": "user1",
    "admin": "admin1"
}

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        users = PREDEFINED_USERS.copy()

        if os.path.exists("users.txt"):
            with open("users.txt", "r", encoding="utf-8") as f:
                for line in f:
                    if ":" in line:
                        u, p = line.strip().split(":", 1)
                        users[u] = p

        if username in users and users[username] == password:
            session["user"] = username
            flash(f"Добро пожаловать, {username}!", "success")
            return redirect(url_for("index"))
        else:
            flash("Неверный логин или пароль! Попробуйте зарегистрироваться.", "danger")
            return redirect(url_for("register"))

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        confirm = request.form.get("password_confirm", "").strip()

        if not username or not password:
            flash("Поля не должны быть пустыми!", "danger")
            return redirect(url_for("register"))

        if password != confirm:
            flash("Пароли не совпадают.", "danger")
            return redirect(url_for("register"))

        existing_users = PREDEFINED_USERS.copy()
        if os.path.exists("users.txt"):
            with open("users.txt", "r", encoding="utf-8") as f:
                for line in f:
                    if ":" in line:
                        u, p = line.strip().split(":", 1)
                        existing_users[u] = p

        if username in existing_users:
            flash("Такой пользователь уже существует.", "danger")
            return redirect(url_for("login"))

        with open("users.txt", "a", encoding="utf-8") as f:
            f.write(f"{username}:{password}\n")

        flash("Регистрация успешна! Теперь войдите.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Вы вышли из системы.", "success")
    return redirect(url_for("login"))

def generate_password(length, complexity):
    upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    digits = "0123456789"
    lower = "abcdefghijklmnopqrstuvwxyz"
    symbols = "!#$%&*+-=?@^_"

    chars = ""
    if complexity == "hard":
        chars = upper + lower + digits + symbols
    elif complexity == "medium":
        chars = upper + lower + digits
    elif complexity == "easy":
        chars = lower + digits
    else:
        return "Ошибка: неверный уровень сложности"

    return "".join(random.choice(chars) for _ in range(length))


@app.route("/", methods=["GET", "POST"])
def index():
    if "user" not in session:
        return redirect(url_for("login"))

    password = ""
    error = ""

    if request.method == "POST":
        try:
            length = int(request.form.get("length", 0))
            level = request.form.get("complexity", "easy").lower()

            if length < 8:
                error = "Пароль должен быть не короче 8 символов."
            else:
                password = generate_password(length, level)

        except ValueError:
            error = "Введите число для длины пароля."

    return render_template("index.html", password=password, error=error, username=session.get("user"))

if __name__ == "__main__":
    if not os.path.exists("users.txt"):
        with open("users.txt", "w", encoding="utf-8") as f:
            f.write("user:user1\nadmin:admin1\n")

    app.run(debug=True)
