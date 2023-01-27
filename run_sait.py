import sqlite3
import os
from flask import Flask, render_template, url_for, request, flash, session, redirect, abort


DATABASE = '/tmp/flsk.db'
DEBUG = True
SECRET_KEY = 'e7430694ceb7ad3af59ae16c4d4cabdf5d1709cc'

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flsk.db')))


def connect_db():
    con = sqlite3.connect(app.config['DATABASE'])
    con.row_factory = sqlite3.Row
    return con


def create_db():
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


menu = [
    {"name": "Продажа/ Покупка автомобилей", "url": "index"},
    {"name": "ПРОДАТЬ/ КУПИТЬ", "url": "sall"},
    {"name": "АВТОСАЛОНЫ", "url": "salons"},
    {"name": "АВТОСЕРВИСЫ", "url": "autoservis"},
    {"name": "Контакты", "url": "contact"},
]


@app.route("/index")
@app.route("/")
def index():
    print(url_for("index"))
    return render_template("/index.html", title="Продажа, покупка и сервис автомобилей", menu=menu)


@app.route("/sall")
def sall():
    print(url_for("sall"))
    return render_template("/sall.html", title="Продать/ Купить Автомобиль", menu=menu)


@app.route("/salons")
def salon():
    print(url_for("salon"))
    return render_template("/salons.html", title="Автосалоны", menu=menu)


@app.route("/autoservis")
def autoservis():
    print(url_for("autoservis"))
    return render_template("/autoservis.html", title="Автосервисы", menu=menu)


@app.route("/contact", methods=["POST", "GET"])
def contact():
    if request.method == "POST":
        if len(request.form['username']) > 2 and request.form['message']:
            flash('Сообщение отправлено успешно!', category="success")
        else:
            flash('Ошибка отправки', category="error")
    return render_template("/contact.html", title="Контакты", menu=menu)


@app.route("/profile/<username>")
def profile(username):
    if 'userLogged' not in session or session['userLogged'] != username:
        abort(401)
    return f"Пользователь: {username}"


@app.route("/login", methods=["POST", "GET"])
def login():
    if 'userlogged' in session:
        return redirect(url_for('profile', username=session['userLogged']))
    elif request.method == 'POST' and request.form['username'] == 'dmitry' and request.form['passw'] == '123456':
        session['userLogged'] = request.form['username']
        return redirect(url_for('profile', username=session['userLogged']))
    return render_template("login.html", title="Авторизация", menu=menu)


@app.errorhandler(404)
def page_not_found(error):
    return render_template("page404.html", title="Страница не найдена", menu=menu)


if __name__ == "__main__":
    app.run(debug=True)
