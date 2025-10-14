from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import random

app = Flask(__name__)
app.secret_key = 'super_secret_key'

PREDEFINED_USERS = {
    "user": "user1",
    "admin": "admin1"
}

def load_users():
    users = {}
    try:
        with open("users.txt", "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(":")
                if len(parts) >= 2:
                    username, password = parts[0], parts[1]
                    users[username] = password
    except FileNotFoundError:
        pass
    return users


def save_user(username, password):
    # добавляем \n чтобы каждый пользователь записывался с новой строки
    with open("users.txt", "a", encoding="utf-8") as file:
        file.write(f"{username}:{password}\n")


def generate_password(length, complexity):
    alfa = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    beta = "0123456789"
    zet = 'abcdefghijklmnopqrstuvwxyz'
    gamma = '!#$%&*+-=?@^_'

    chars = ''

    if complexity == "hard":
        chars = alfa + beta + zet + gamma
    elif complexity == "medium":
        chars = alfa + beta + zet
    elif complexity == "easy":
        chars = beta + zet
    else:
        return "Недопустимый уровень сложности. Выберите 'easy', 'medium' или 'hard'."

    password = ''.join(random.choices(chars, k=length))
    return password


@app.route('/', methods=['GET', 'POST'])
def index():
    # доступ только после входа
    user = session.get('user')
    if not user:
        flash("Пожалуйста, выполните вход.", "error")
        return redirect(url_for("login"))

    password = None
    error = None

    if request.method == 'POST':
        try:
            pwd_length = int(request.form['length'])
        except ValueError:
            error = "Длина должна быть числом."
            return render_template('index.html', error=error, password=None)

        if pwd_length < 8:
            error = "Пароль не должен быть меньше 8 символов."
            return render_template('index.html', error=error, password=None)

        pwd_auto = request.form['complexity'].lower()
        password = generate_password(pwd_length, pwd_auto)

        if not isinstance(password, str):
            error = password
            password = None

    return render_template('index.html', password=password, error=error, username=user)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        users = {**PREDEFINED_USERS, **load_users()}

        if username in users and users[username] == password:
            session['user'] = username
            flash(f"Добро пожаловать, {username}!", "success")
            return redirect(url_for("index"))
        else:
            flash("Неверные данные! Зарегистрируйтесь.", "error")
            return redirect(url_for("register"))
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        confirm = request.form.get("password_confirm", "").strip()

        if not username or not password:
            flash("Все поля обязательны.", "error")
            return redirect(url_for("register"))

        if password != confirm:
            flash("Пароли не совпадают.", "error")
            return redirect(url_for("register"))

        users = {**PREDEFINED_USERS, **load_users()}
        if username in users:
            flash("Такой пользователь уже существует.", "error")
            return redirect(url_for("login"))

        save_user(username, password)
        flash("Регистрация успешно завершена! Теперь войдите.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/logout")
def logout():
    user = session.pop('user', None)
    if user:
        flash(f"Пользователь {user} вышел из системы.", "success")
    return redirect(url_for("login"))


if __name__ == '__main__':
    if not os.path.exists("users.txt"):
        with open("users.txt", "w", encoding="utf-8") as f:
            f.write("user:user1\nadmin:admin1\n")
    app.run(debug=True)


