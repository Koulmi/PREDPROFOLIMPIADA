from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import os
import pandas as pd
from data.db_session import global_init, db
from data.models import (User, pw_secure, List)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

global_init(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
ADMIN_LOGIN = 'admin'

app.config['UPLOAD_FOLDER'] = 'static/uploads'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

print(pd.__version__)

def main():
    app.run()


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return render_template('home.html')

    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        user = db.session.query(User).filter_by(login=login).first()

        if user and pw_secure.verify_password(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Неверный email или пароль', 'danger')

    return render_template('login.html')


@app.route('/')
def home():
    return render_template('home.html')


'''@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('Файла нет в запросе')

    file = request.files['file']

    if file.filename == '':
        flash('Файл не выбран')

    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        if file.filename.endswith('.csv'):
            df = pd.read_csv(filepath)
        elif file.filename.endswith('.xlsx'):
            df = pd.read_excel(filepath)
        else:
            flash('Неподдерживаемый формат файла')

        html_table = df.to_html(classes='table table-striped')
        return render_template('result.html', table=html_table)'''


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not db.session.query(User).filter_by(login=ADMIN_LOGIN).first():
            admin = User(
                login=ADMIN_LOGIN,
                password=pw_secure.encrypt_password('sHjkfd23jHFSas[32')
            )
            db.session.add(admin)
            db.session.commit()
        app.run(host='127.0.0.1', port=5000, debug=True)
