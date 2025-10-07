from flask import Flask, render_template, request
import random

app = Flask(__name__)


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
    password = None

    if request.method == 'POST':
        try:  # Обработка случаев, когда ввод не является числом
            pwd_length = int(request.form['length'])  # Берем данные из HTML формы
        except ValueError:
            return render_template('index.html', error="Длина должна быть числом.", password=password)

        if pwd_length < 8:
            return render_template('index.html',error="Пароль не должен быть меньше 8.", password=password)

        pwd_auto = request.form['complexity'].lower()
        password = generate_password(pwd_length, pwd_auto)

        if not isinstance(password, str):  # если вернулась ошибка
            return render_template('index.html', error=password, password=None)
        else:
            return render_template('index.html', password=password, error=None)

    return render_template('index.html', password=password, error=None)  # отображаем форму при первом заходе


if __name__ == '__main__':
    app.run(debug=True)
