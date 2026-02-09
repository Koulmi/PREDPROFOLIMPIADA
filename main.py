from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import os
import pandas as pd
from data.db_session import global_init, db
from data.models import (User, pw_secure, List, Applications, Programs)
from werkzeug.utils import secure_filename
from flask import send_file
from datetime import datetime
from report import generate_pdf_report

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

        try:
            df = pd.read_excel(file_path)
            existing_programs = db.session.query(Programs).all()
            existing_names = [p.name for p in existing_programs]
            for name in BUDGET.keys():
                if name not in existing_names:
                    db.session.add(Programs(name=name))
            db.session.commit()

            all_programs_map = {p.name: p for p in db.session.query(Programs).all()}
            ids_in_file = df['id'].tolist()

            db.session.query(Applications).filter(Applications.applicants_id.notin_(ids_in_file)).delete()
            db.session.query(List).filter(List.id.notin_(ids_in_file)).delete()
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
                    col = f'Приоритет{i}'
                    if col in row and pd.notna(row[col]):
                        prog_name = row[col]
                        if prog_name in all_programs_map:
                            db.session.add(Applications(priority=i, applicants_id=row['id'],
                                                        program_id=all_programs_map[prog_name].id))
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash("Загрузите файл с расширением xlsx")
            return redirect(url_for('home'))
        html_table = df.to_html(classes='table table-striped')
        return render_template('result.html', table=html_table)

    return redirect(url_for('home'))


def run_distribution():
    current_day = session.get('current_day', '01.08')
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{current_day}.xlsx')

    if not os.path.exists(file_path):
        return None

    df = pd.read_excel(file_path)

    cols_to_numeric = ['Сумма', 'Математика', 'Русский', 'Физика/Информатика', 'Индивидуальные достижения']
    for col in cols_to_numeric:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    df.fillna('', inplace=True)

    if 'Согласие' in df.columns:
        df['is_consent'] = df['Согласие'].apply(lambda x: True if x == 'Есть' or x is True else False)
    else:
        df['is_consent'] = False

    sort_cols = ['Сумма', 'Математика', 'Русский', 'Физика/Информатика', 'Индивидуальные достижения']
    existing_sort = [c for c in sort_cols if c in df.columns]
    ascending = [False] * len(existing_sort)

    candidates = df[df['is_consent'] == True].sort_values(by=existing_sort, ascending=ascending)

    filled = {p: 0 for p in BUDGET}
    enrolled_map = {}

    for _, row in candidates.iterrows():
        for i in range(1, 5):
            prog = row.get(f'Приоритет{i}')
            if prog in BUDGET and filled[prog] < BUDGET[prog]:
                filled[prog] += 1
                enrolled_map[row['id']] = prog
                break

    df['Зачислен_на'] = df['id'].map(enrolled_map)
    df['Согласие'] = df['is_consent'].apply(lambda x: 'Есть' if x else 'Нет')
    return df


def render_program_page(prog_name, template):
    df = run_distribution()
    if df is None:
        return render_template(template)

    condition = (df['Приоритет1'] == prog_name) | \
                (df['Приоритет2'] == prog_name) | \
                (df['Приоритет3'] == prog_name) | \
                (df['Приоритет4'] == prog_name)

    df_prog = df[condition].copy()
    def get_number(row):
        for i in range(1, 5):
            if row[f'Приоритет{i}'] == prog_name:
                return i
        return '-'

    df_prog['Приоритет'] = df_prog.apply(get_number, axis=1)

    enrolled_df = df_prog[df_prog['Зачислен_на'] == prog_name]

    count = len(df_prog)
    consent_count = len(df_prog[df_prog['Согласие'] == 'Есть'])
    enrolled_count = len(enrolled_df)

    passing_score = 0
    if enrolled_count == BUDGET.get(prog_name, 0):
        passing_score = enrolled_df['Сумма'].min()

    cols = ['id', 'Математика', 'Русский', 'Физика/Информатика',
            'Индивидуальные достижения', 'Сумма', 'Согласие', 'Приоритет']
    final_cols = [c for c in cols if c in df_prog.columns]

    html = df_prog[final_cols].to_html(classes='table table-striped', index=False)

    return render_template(template,
                           table=html,
                           count=count,
                           consent_count=consent_count,
                           enrolled_count=enrolled_count,
                           passing_score=passing_score,
                           current_day=session.get('current_day', '01.08'))


@app.route('/result_pm')
def result_pm():
    return render_program_page('ПМ', 'result_pm.html')


@app.route('/result_ivt')
def result_ivt():
    return render_program_page('ИВТ', 'result_ivt.html')


@app.route('/result_itss')
def result_itss():
    return render_program_page('ИТСС', 'result_itss.html')


@app.route('/result_ib')
def result_ib():
    return render_program_page('ИБ', 'result_ib.html')


@app.route('/result')
def result():
    df = run_distribution()
    current_day = session.get('current_day', '01.08')

    if df is not None:
        count = len(df)
        consent_count = len(df[df['Согласие'] == 'Есть'])

        cols = ['id', 'Математика', 'Русский', 'Физика/Информатика',
                'Индивидуальные достижения', 'Сумма', 'Согласие',
                'Приоритет1', 'Приоритет2', 'Приоритет3', 'Приоритет4']
        final_cols = [c for c in cols if c in df.columns]

        html = df[final_cols].to_html(classes='table table-striped', index=False)
        return render_template('all.html', table=html, count=count,
                               consent_count=consent_count, enrolled_count=0,
                               passing_score=0, current_day=current_day)
    else:
        return render_template('all.html', table="", count=0, consent_count=0, enrolled_count=0, passing_score=0)


@app.route('/generate_report')
def generate_report():
    current_day = session.get('current_day', '01.08')
    pdf_buffer = generate_pdf_report(app.config['UPLOAD_FOLDER'], BUDGET, current_day)
    if pdf_buffer is None:
        flash("Нет данных для формирования отчета", "danger")
        return redirect(url_for('home'))

    now_str = datetime.now().strftime("%Y-%m-%d_%H-%M")
    return send_file(pdf_buffer, as_attachment=True,
                     download_name=f"report_{current_day}_{now_str}.pdf", mimetype='application/pdf')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not db.session.query(User).filter_by(login=ADMIN_LOGIN).first():
            admin = User(login=ADMIN_LOGIN,
                         password=pw_secure.encrypt_password('sHjkfd23jHFSas[32'))
            db.session.add(admin)
            db.session.commit()
        app.run(host='127.0.0.1', port=5000, debug=True)
