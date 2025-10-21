from flask import Flask, render_template, request, redirect, url_for, flash, session
import random
import os

app = Flask(__name__)
app.secret_key = 'super_secret_key'

PREDEFINED_USERS = {
    "user": "user1",
    "admin": "admin1"
}

def load_users():
    users = {}
    if os.path.exists("users.txt"):
        with open("users.txt", "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(":")
                if len(parts) >= 2:
                    username, password = parts[0], parts[1]
                    history = parts[2].split(",") if len(parts) > 2 else []
                    users[username] = {"password": password, "history": history}
    return users


def save_users(users):
    with open("users.txt", "w", encoding="utf-8") as file:
        for username, data in users.items():
            line = f"{username}:{data['password']}"
            if data["history"]:
                line += ":" + ",".join(data["history"])
            file.write(line + "\n")


def save_user(username, password):
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
        return "Недопустимый уровень сложности."

    return ''.join(random.choices(chars, k=length))


@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user' not in session:
        flash("Пожалуйста, выполните вход.", "error")
        return redirect(url_for("login"))

    username = session['user']
    users = {**PREDEFINED_USERS, **load_users()}
    password = None
    error = None

    user_data = load_users().get(username, {"history": []})
    history = user_data.get("history", [])

    if request.method == 'POST':
        try:
            pwd_length = int(request.form['length'])
        except ValueError:
            error = "Длина должна быть числом."
            return render_template('index.html', error=error, password=None, history=history, username=username)

        if pwd_length < 8:
            error = "Пароль не должен быть меньше 8 символов."
            return render_template('index.html', error=error, password=None, history=history, username=username)

        complexity = request.form['complexity'].lower()
        password = generate_password(pwd_length, complexity)

        users_full = load_users()
        if username not in users_full:
            users_full[username] = {"password": PREDEFINED_USERS.get(username, ""), "history": []}
        users_full[username]["history"].append(password)
        save_users(users_full)
        history = users_full[username]["history"]

    return render_template('index.html', password=password, error=error, username=username, history=history)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        all_users = load_users()
        users_simple = {u: d["password"] for u, d in all_users.items()}
        users_combined = {**PREDEFINED_USERS, **users_simple}

        if username in users_combined and users_combined[username] == password:
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

        users = load_users()
        if username in users:
            flash("Такой пользователь уже существует.", "error")
            return redirect(url_for("login"))

        save_user(username, password)
        flash("Регистрация успешно завершена! Теперь войдите.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.pop('user', None)
    flash("Вы вышли из системы.", "success")
    return redirect(url_for("login"))


if __name__ == '__main__':
    if not os.path.exists("users.txt"):
        with open("users.txt", "w", encoding="utf-8") as f:
            f.write("user:user1\nadmin:admin1\n")
    app.run(debug=True)
    app.run(debug=True)
