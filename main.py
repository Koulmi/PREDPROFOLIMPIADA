from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import os
import pandas as pd
from data.db_session import global_init, db
from data.models import (User, pw_secure, List, Applications, Programs)

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


@app.route('/upload_first', methods=['POST'])
def upload_first():
    if 'file' not in request.files:
        flash("Файла нет в запросе")
    file = request.files['file']
    if file.filename == '':
        flash("Файл не выбран")

    if file:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.filename.endswith('.xlsx') or file.filename.endswith('.xls'):
            df = pd.read_excel(file)
        else:
            flash("Неподдерживаемый формат файла")

        for index, row in df.iterrows():
            new_item = List(id=row['id'],
                            maths=row['Математика'],
                            russian=row['Русский'],
                            physics_it=row['Физика/Информатика'],
                            achievements=row['Индивидуальные достижения'],
                            summ=row['Сумма'],
                            consent=row['Согласие'])
            db.session.merge(new_item)

            for i in range(1, 5):
                column_name = f'Приоритет{i}'
                prog_name = row[column_name]


                program = Programs(name=prog_name)
                db.session.add(program)
                db.session.flush()


                new_priority = Applications(
                    priority=i,
                    applicants_id=row['id'],
                    program_id=program.id
                )
                db.session.add(new_priority)
        db.session.commit()
        html_table = df.to_html(classes='table table-striped')
        return render_template('result.html', table=html_table)


@app.route('/result_pm')
def result_pm():
    applicants = db.session.query(List, Applications, Programs). \
        join(Applications, List.id == Applications.applicants_id). \
        join(Programs, Applications.program_id == Programs.id). \
        filter(Programs.name == 'ПМ').all()

    count = len(applicants)
    consent_count = 0
    priority_count = 0

    if not applicants:
        return render_template('result.html')

    data = []
    for item, applic, prog in applicants:
        if item.consent:
            if applic.priority == 1:
                priority_count += 1
            consent = 'Есть'
            consent_count += 1
        else:
            consent = 'Нет'
        data.append({
            'id': item.id,
            'Математика': item.maths,
            'Русский': item.russian,
            'Физика/Информатика': item.physics_it,
            'Индивидуальные достижения': item.achievements,
            'Сумма': item.summ,
            'Согласие': consent,
            'Приоритет': applic.priority
        })

    df = pd.DataFrame(data)

    if not df.empty:
        df = df.sort_values(by=['Согласие', 'Сумма'], ascending=[True, False])

    html_table = df.to_html(classes='table table-striped', index=False)
    return render_template('result_ib.html', table=html_table, count=count,
                           consent_count=consent_count, priority_count=priority_count)


@app.route('/result_ivt')
def result_ivt():
    applicants = db.session.query(List, Applications, Programs). \
        join(Applications, List.id == Applications.applicants_id). \
        join(Programs, Applications.program_id == Programs.id). \
        filter(Programs.name == 'ИВТ').all()

    count = len(applicants)
    consent_count = 0
    priority_count = 0

    if not applicants:
        return render_template('result.html')

    data = []
    for item, applic, prog in applicants:
        if item.consent:
            if applic.priority == 1:
                priority_count += 1
            consent = 'Есть'
            consent_count += 1
        else:
            consent = 'Нет'
        data.append({
            'id': item.id,
            'Математика': item.maths,
            'Русский': item.russian,
            'Физика/Информатика': item.physics_it,
            'Индивидуальные достижения': item.achievements,
            'Сумма': item.summ,
            'Согласие': consent,
            'Приоритет': applic.priority
        })

    df = pd.DataFrame(data)

    if not df.empty:
        df = df.sort_values(by=['Согласие', 'Сумма'], ascending=[True, False])

    html_table = df.to_html(classes='table table-striped', index=False)
    return render_template('result_ib.html', table=html_table, count=count,
                           consent_count=consent_count, priority_count=priority_count)


@app.route('/result_itss')
def result_itss():
    applicants = db.session.query(List, Applications, Programs). \
        join(Applications, List.id == Applications.applicants_id). \
        join(Programs, Applications.program_id == Programs.id). \
        filter(Programs.name == 'ИТСС').all()

    count = len(applicants)
    consent_count = 0
    priority_count = 0

    if not applicants:
        return render_template('result.html')

    data = []
    for item, applic, prog in applicants:
        if item.consent:
            if applic.priority == 1:
                priority_count += 1
            consent = 'Есть'
            consent_count += 1
        else:
            consent = 'Нет'
        data.append({
            'id': item.id,
            'Математика': item.maths,
            'Русский': item.russian,
            'Физика/Информатика': item.physics_it,
            'Индивидуальные достижения': item.achievements,
            'Сумма': item.summ,
            'Согласие': consent,
            'Приоритет': applic.priority
        })

    df = pd.DataFrame(data)

    if not df.empty:
        df = df.sort_values(by=['Согласие', 'Сумма'], ascending=[True, False])

    html_table = df.to_html(classes='table table-striped', index=False)
    return render_template('result_ib.html', table=html_table, count=count,
                           consent_count=consent_count, priority_count=priority_count)


@app.route('/result_ib')
def result_ib():
    applicants = db.session.query(List, Applications, Programs). \
        join(Applications, List.id == Applications.applicants_id). \
        join(Programs, Applications.program_id == Programs.id). \
        filter(Programs.name == 'ИБ').all()

    count = len(applicants)
    consent_count = 0
    priority_count = 0

    if not applicants:
        return render_template('result.html')

    data = []
    for item, applic, prog in applicants:
        if item.consent:
            if applic.priority == 1:
                priority_count += 1
            consent = 'Есть'
            consent_count += 1
        else:
            consent = 'Нет'
        data.append({
            'id': item.id,
            'Математика': item.maths,
            'Русский': item.russian,
            'Физика/Информатика': item.physics_it,
            'Индивидуальные достижения': item.achievements,
            'Сумма': item.summ,
            'Согласие': consent,
            'Приоритет': applic.priority
        })

    df = pd.DataFrame(data)

    if not df.empty:
        df = df.sort_values(by=['Согласие', 'Сумма'], ascending=[True, False])

    html_table = df.to_html(classes='table table-striped', index=False)
    return render_template('result_ib.html', table=html_table, count=count,
                           consent_count=consent_count, priority_count=priority_count)


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
