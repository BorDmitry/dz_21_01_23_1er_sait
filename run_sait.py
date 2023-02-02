import sqlite3
import os
from flask import Flask, render_template, url_for, request, flash, session, redirect, abort, g
from FDataBase import FDataBase

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


def get_db():                       # возвращает активное соединение с БД
    if not hasattr(g, 'link_db'):   # link_db - переменная из g,стандартная запись- проверка на наличие аттрибутов
        g.link_db = connect_db()
    return g.link_db


@app.route("/index")
@app.route("/")
def index():
    db = get_db()
    dbase = FDataBase(db)  # dbase - экзэмпляр класса FDataBase
    return render_template("/index.html", title="Продажа, покупка и сервис автомобилей", menu=dbase.get_menu(),
                           posts=dbase.get_posts_anonce())


@app.route("/add_post", methods=["POST", "GET"])
def add_post():
    db = get_db()
    dbase = FDataBase(db)

    if request.method == "POST":
        if len(request.form['name']) > 4 and len(request.form['post']) > 10:
            res = dbase.add_post(request.form['name'], request.form['post'], request.form['url'])
            if not res:
                flash("Ошибка добавления статьи", category="error")
            else:
                flash("Статья добавлена успешно", category="success")
        else:
            flash("Ошибка добавления статьи", category="error")

    return render_template("add_post.html", menu=dbase.get_menu(), title="Добавление статьи")


@app.route("/post/<alias>")
def show_post(alias):
    db = get_db()
    dbase = FDataBase(db)
    title, post = dbase.get_post(alias)
    if not title:
        abort(404)

    return render_template('post.html', menu=dbase.get_menu(), title=title, post=post)


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
    db = get_db()
    dbase = FDataBase(db)

    return render_template("page404.html", title="Страница не найдена", menu=dbase.get_menu())


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()


if __name__ == "__main__":
    app.run(debug=True)
