from flask import Flask, render_template, request
import random

app = Flask(__name__)

def generate_password(length, complexity):
    alfa = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    beta = "0123456789"
    zet = 'abcdefghijklmnopqrstuvwxyz'
    gamma = '!#$%&*+-=?@^_'

    if complexity == "hard":
        chars = alfa + beta + zet + gamma
    elif complexity == "medium":
        chars = alfa + beta + zet
    elif complexity == "easy":
        chars = beta + zet
    else:
        return "Недопустимый уровень сложности. Выберите 'easy', 'medium' или 'hard'."

    return ''.join(random.choices(chars, k=length))


@app.route('/', methods=['GET', 'POST'])
def index():
    password = None
    error = None

    if request.method == 'POST':
        try:
            pwd_length = int(request.form['length'])
        except ValueError:
            error = "Длина должна быть числом."
            return render_template('index.html', error=error)

        if pwd_length < 8:
            error = "Пароль не должен быть меньше 8 символов."
            return render_template('index.html', error=error)

        pwd_auto = request.form['complexity'].lower()
        password = generate_password(pwd_length, pwd_auto)
        if not isinstance(password, str):
            error = password
            password = None

    return render_template('index.html', password=password, error=error)


if __name__ == '__main__':
    app.run(debug=True)
