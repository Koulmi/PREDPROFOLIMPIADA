from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import os
import pandas as pd
from data.db_session import global_init, db
from data.models import (User, pw_secure, List, Applications, Programs)
from werkzeug.utils import secure_filename

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

BUDGET = {
    'ПМ': 40,
    'ИВТ': 50,
    'ИТСС': 30,
    'ИБ': 20
}


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
    current_day = session.get('current_day', '01.08')
    return render_template('home.html', current_day=current_day)


@app.route('/set_day')
def set_day():
    day = request.args.get('day')
    redirect_to = request.args.get('redirect', url_for('home'))

    valid_days = ['01.08', '02.08', '03.08', '04.08']
    if day in valid_days:
        session['current_day'] = day

    return redirect(redirect_to)


@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        flash("Файла нет в запросе")
        return redirect(url_for('home'))

    file = request.files['file']
    if file.filename == '':
        flash("Файл не выбран")
        return redirect(url_for('home'))

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        if filename.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        else:
            flash("Неподдерживаемый формат файла")
            return redirect(url_for('home'))

        existing_programs = db.session.query(Programs).all()
        existing_names = [p.name for p in existing_programs]

        for name in BUDGET.keys():
            if name not in existing_names:
                new_prog = Programs(name=name)
                db.session.add(new_prog)
        db.session.commit()

        all_programs_map = {p.name: p for p in db.session.query(Programs).all()}

        ids_in_file = df['id'].tolist()

        all_apps = db.session.query(Applications).all()
        for applic in all_apps:
            if applic.applicants_id not in ids_in_file:
                db.session.delete(applic)

        all_items = db.session.query(List).all()
        for item in all_items:
            if item.id not in ids_in_file:
                db.session.delete(item)

        db.session.commit()

        for index, row in df.iterrows():
            new_item = List(id=row['id'],
                            maths=row['Математика'],
                            russian=row['Русский'],
                            physics_it=row['Физика/Информатика'],
                            achievements=row['Индивидуальные достижения'],
                            summ=row['Сумма'],
                            consent=row['Согласие'])
            db.session.merge(new_item)

            db.session.query(Applications).filter_by(applicants_id=row['id']).delete()

            for i in range(1, 5):
                column_name = f'Приоритет{i}'

                if column_name in row and pd.notna(row[column_name]):
                    prog_name = row[column_name]
                    if prog_name in all_programs_map:
                        target_prog = all_programs_map[prog_name]
                        new_priority = Applications(
                            priority=i,
                            applicants_id=row['id'],
                            program_id=target_prog.id
                        )
                        db.session.add(new_priority)

        db.session.commit()
        run_distribution()

        html_table = df.to_html(classes='table table-striped')
        return render_template('result.html', table=html_table)


def run_distribution():
    db.session.query(Applications).update({Applications.is_enrolled: False})
    db.session.commit()

    all_programs = db.session.query(Programs).all()

    prog_limits = {}
    prog_filled = {}

    for prog in all_programs:
        limit = BUDGET.get(prog.name)
        prog_limits[prog.id] = limit
        prog_filled[prog.id] = 0

    candidates = db.session.query(List).filter_by(consent=True).order_by(List.summ.desc(), List.maths.desc()).all()

    for student in candidates:
        apps = sorted(student.applications, key=lambda x: x.priority)

        for applic in apps:
            prog_id = applic.program_id
            if prog_filled[prog_id] < prog_limits[prog_id]:
                applic.is_enrolled = True
                prog_filled[prog_id] += 1
                break

    db.session.commit()


def load_data_from_file(program_name):
    current_day = session.get('current_day', '01.08')
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{current_day}.xlsx')

    if not os.path.exists(file_path):
        return None

    df = pd.read_excel(file_path)
    df.fillna('', inplace=True)

    program_df = df[df.apply(lambda row:
                             program_name in [row[f'Приоритет{i}'] for i in range(1, 5)], axis=1)].copy()

    def get_priority_number(row):
        for i in range(1, 5):
            if row[f'Приоритет{i}'] == program_name:
                return i
        return '-'

    program_df['Приоритет'] = program_df.apply(get_priority_number, axis=1)
    program_df['Согласие'] = program_df['Согласие'].apply(lambda x: 'Есть' if x else 'Нет')
    target_columns = ['id', 'Математика', 'Русский', 'Физика/Информатика',
                      'Индивидуальные достижения', 'Сумма', 'Согласие', 'Приоритет']

    return program_df[target_columns]


@app.route('/result')
def result():
    current_day = session.get('current_day', '01.08')
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{current_day}.xlsx')

    if os.path.exists(file_path):
        df = pd.read_excel(file_path)
        df.fillna('', inplace=True)
        if 'Согласие' in df.columns:
            df['Согласие'] = df['Согласие'].apply(lambda x: 'Есть' if x else 'Нет')

        count = len(df)
        consent_count = len(df[df['Согласие'] == 'Есть']) if 'Согласие' in df.columns else 0
        enrolled_count = 0
        passing_score = 0
        cols = ['id', 'Математика', 'Русский', 'Физика/Информатика',
                'Индивидуальные достижения', 'Сумма', 'Согласие',
                'Приоритет1', 'Приоритет2', 'Приоритет3', 'Приоритет4']

        cols = [c for c in cols if c in df.columns]
        df = df[cols]

        html_table = df.to_html(classes='table table-striped', index=False)

        return render_template('all.html',
                               table=html_table,
                               count=count,
                               consent_count=consent_count,
                               enrolled_count=enrolled_count,
                               passing_score=passing_score,
                               current_day=current_day)

    else:
        return render_template('all.html', table="", count=0,
                               consent_count=0, enrolled_count=0,
                               passing_score=0, current_day=current_day)


@app.route('/result_pm')
def result_pm():
    run_distribution()

    current_day = session.get('current_day', '01.08')
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{current_day}.xlsx')

    if os.path.exists(file_path):
        df = load_data_from_file('ПМ')
        if df is not None:
            count = len(df)
            consent_count = len(df[df['Согласие'] == 'Есть'])
            enrolled_count = min(consent_count, BUDGET['ПМ'])

            passing_score = 0
            if enrolled_count == BUDGET['ПМ'] and consent_count >= BUDGET['ПМ']:
                consent_sorted = df[df['Согласие'] == 'Есть'].sort_values('Сумма', ascending=False)
                passing_score = consent_sorted.iloc[BUDGET['ПМ'] - 1]['Сумма']

            html_table = df.to_html(classes='table table-striped', index=False)
            return render_template('result_pm.html', table=html_table, count=count,
                                   consent_count=consent_count, enrolled_count=enrolled_count,
                                   passing_score=passing_score, current_day=current_day)

    applicants = db.session.query(List, Applications, Programs). \
        join(Applications, List.id == Applications.applicants_id). \
        join(Programs, Applications.program_id == Programs.id). \
        filter(Programs.name == 'ПМ').group_by(List.id).all()

    count = len(applicants)
    consent_count = 0
    enrolled_count = 0
    enrolled_scores = []
    passing_score = 0

    if not applicants:
        return render_template('result_pm.html', table='', count=0,
                               consent_count=0, enrolled_count=0, passing_score=0,
                               current_day=current_day)

    data = []
    for item, applic, prog in applicants:
        if item.consent:
            consent = 'Есть'
            consent_count += 1
            if applic.is_enrolled:
                enrolled_count += 1
                enrolled_scores.append(item.summ)
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

    if enrolled_count == BUDGET['ПМ']:
        passing_score = min(enrolled_scores[:BUDGET['ПМ']])

    df = pd.DataFrame(data)

    html_table = df.to_html(classes='table table-striped', index=False)
    return render_template('result_pm.html', table=html_table, count=count,
                           consent_count=consent_count, enrolled_count=enrolled_count,
                           passing_score=passing_score, current_day=current_day)


@app.route('/result_ivt')
def result_ivt():
    run_distribution()

    current_day = session.get('current_day', '01.08')
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{current_day}.xlsx')

    if os.path.exists(file_path):
        df = load_data_from_file('ИВТ')
        if df is not None:
            count = len(df)
            consent_count = len(df[df['Согласие'] == 'Есть'])
            enrolled_count = min(consent_count, BUDGET['ИВТ'])

            passing_score = 0
            if enrolled_count == BUDGET['ИВТ'] and consent_count >= BUDGET['ИВТ']:
                consent_sorted = df[df['Согласие'] == 'Есть'].sort_values('Сумма', ascending=False)
                passing_score = consent_sorted.iloc[BUDGET['ИВТ'] - 1]['Сумма']

            html_table = df.to_html(classes='table table-striped', index=False)
            return render_template('result_ivt.html', table=html_table, count=count,
                                   consent_count=consent_count, enrolled_count=enrolled_count,
                                   passing_score=passing_score, current_day=current_day)

    applicants = db.session.query(List, Applications, Programs). \
        join(Applications, List.id == Applications.applicants_id). \
        join(Programs, Applications.program_id == Programs.id). \
        filter(Programs.name == 'ИВТ').group_by(List.id).all()

    count = len(applicants)
    consent_count = 0
    enrolled_count = 0
    enrolled_scores = []
    passing_score = 0

    if not applicants:
        return render_template('result_ivt.html', table='', count=0,
                               consent_count=0, enrolled_count=0, passing_score=0,
                               current_day=current_day)

    data = []
    for item, applic, prog in applicants:
        if item.consent:
            consent = 'Есть'
            consent_count += 1
            if applic.is_enrolled:
                enrolled_count += 1
                enrolled_scores.append(item.summ)
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

    if enrolled_count >= BUDGET['ИВТ']:
        passing_score = min(enrolled_scores[:BUDGET['ИВТ']])

    df = pd.DataFrame(data)

    html_table = df.to_html(classes='table table-striped', index=False)
    return render_template('result_ivt.html', table=html_table, count=count,
                           consent_count=consent_count, enrolled_count=enrolled_count,
                           passing_score=passing_score, current_day=current_day)


@app.route('/result_itss')
def result_itss():
    run_distribution()

    current_day = session.get('current_day', '01.08')
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{current_day}.xlsx')

    if os.path.exists(file_path):
        df = load_data_from_file('ИТСС')
        if df is not None:
            count = len(df)
            consent_count = len(df[df['Согласие'] == 'Есть'])
            enrolled_count = min(consent_count, BUDGET['ИТСС'])

            passing_score = 0
            if enrolled_count == BUDGET['ИТСС'] and consent_count >= BUDGET['ИТСС']:
                consent_sorted = df[df['Согласие'] == 'Есть'].sort_values('Сумма', ascending=False)
                passing_score = consent_sorted.iloc[BUDGET['ИТСС'] - 1]['Сумма']

            html_table = df.to_html(classes='table table-striped', index=False)
            return render_template('result_itss.html', table=html_table, count=count,
                                   consent_count=consent_count, enrolled_count=enrolled_count,
                                   passing_score=passing_score, current_day=current_day)

    applicants = db.session.query(List, Applications, Programs). \
        join(Applications, List.id == Applications.applicants_id). \
        join(Programs, Applications.program_id == Programs.id). \
        filter(Programs.name == 'ИТСС').group_by(List.id).all()

    count = len(applicants)
    consent_count = 0
    enrolled_count = 0
    enrolled_scores = []
    passing_score = 0

    if not applicants:
        return render_template('result_itss.html', table='', count=0,
                               consent_count=0, enrolled_count=0, passing_score=0,
                               current_day=current_day)

    data = []
    for item, applic, prog in applicants:
        if item.consent:
            consent = 'Есть'
            consent_count += 1
            if applic.is_enrolled:
                enrolled_count += 1
                enrolled_scores.append(item.summ)
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

    if enrolled_count == BUDGET['ИТСС']:
        passing_score = min(enrolled_scores[:BUDGET['ИТСС']])

    df = pd.DataFrame(data)

    html_table = df.to_html(classes='table table-striped', index=False)
    return render_template('result_itss.html', table=html_table, count=count,
                           consent_count=consent_count, enrolled_count=enrolled_count,
                           passing_score=passing_score, current_day=current_day)


@app.route('/result_ib')
def result_ib():
    run_distribution()

    current_day = session.get('current_day', '01.08')
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{current_day}.xlsx')

    if os.path.exists(file_path):
        df = load_data_from_file('ИБ')
        if df is not None:
            count = len(df)
            consent_count = len(df[df['Согласие'] == 'Есть'])
            enrolled_count = min(consent_count, BUDGET['ИБ'])

            passing_score = 0
            if enrolled_count == BUDGET['ИБ'] and consent_count >= BUDGET['ИБ']:
                consent_sorted = df[df['Согласие'] == 'Есть'].sort_values('Сумма', ascending=False)
                passing_score = consent_sorted.iloc[BUDGET['ИБ'] - 1]['Сумма']

            html_table = df.to_html(classes='table table-striped', index=False)
            return render_template('result_ib.html', table=html_table, count=count,
                                   consent_count=consent_count, enrolled_count=enrolled_count,
                                   passing_score=passing_score, current_day=current_day)

    applicants = db.session.query(List, Applications, Programs). \
        join(Applications, List.id == Applications.applicants_id). \
        join(Programs, Applications.program_id == Programs.id). \
        filter(Programs.name == 'ИБ').group_by(List.id).all()

    count = len(applicants)
    consent_count = 0
    enrolled_count = 0
    enrolled_scores = []
    passing_score = 0

    if not applicants:
        return render_template('result_ib.html', table='', count=0,
                               consent_count=0, enrolled_count=0, passing_score=0,
                               current_day=current_day)

    data = []
    for item, applic, prog in applicants:
        if item.consent:
            consent = 'Есть'
            consent_count += 1
            if applic.is_enrolled:
                enrolled_count += 1
                enrolled_scores.append(item.summ)
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

    if enrolled_count == BUDGET['ИБ']:
        passing_score = min(enrolled_scores[:BUDGET['ИБ']])

    df = pd.DataFrame(data)

    html_table = df.to_html(classes='table table-striped', index=False)
    return render_template('result_ib.html', table=html_table, count=count,
                           consent_count=consent_count, enrolled_count=enrolled_count,
                           passing_score=passing_score, current_day=current_day)


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