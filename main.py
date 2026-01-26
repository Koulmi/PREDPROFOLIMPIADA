from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import os
import pandas as pd
from data.db_session import global_init, db
from data.models import User, pw_secure, List, Applications, Programs
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
        return redirect(url_for('home'))

    if request.method == 'POST':
        login_input = request.form['login']
        password = request.form['password']
        user = db.session.query(User).filter_by(login=login_input).first()

        if user and pw_secure.verify_password(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Неверный логин или пароль', 'danger')

    return render_template('login.html')


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/upload_first', methods=['POST'])
def upload_first():
    if 'file' not in request.files:
        flash("Файла нет в запросе", 'danger')
        return redirect(url_for('home'))

    file = request.files['file']
    if file.filename == '':
        flash("Файл не выбран", 'danger')
        return redirect(url_for('home'))

    if file:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.filename.endswith('.xlsx') or file.filename.endswith('.xls'):
            df = pd.read_excel(file)
        else:
            flash("Неподдерживаемый формат файла")
            return redirect(url_for('home'))

        df = df.fillna('')

        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        ids_in_file = df['id'].tolist()

        all_apps = Applications.query.all()
        for applic in all_apps:
            if applic.applicants_id not in ids_in_file:
                db.session.delete(applic)

        all_items = List.query.all()
        for item in all_items:
            if item.id not in ids_in_file:
                db.session.delete(item)

        for index, row in df.iterrows():
            new_item = List(
                id=row['id'],
                maths=row['Математика'],
                russian=row['Русский'],
                physics_it=row['Физика/Информатика'],
                achievements=row['Индивидуальные достижения'],
                summ=row['Сумма'],
                consent=bool(row['Согласие']) if row['Согласие'] != '' else False
            )

            db.session.merge(new_item)

            for i in range(1, 5):
                column_name = f'Приоритет{i}'
                prog_name = str(row[column_name]).strip()

                if not prog_name or prog_name == '' or prog_name.lower() == 'nan':
                    continue

                program = Programs.query.filter_by(name=prog_name).first()
                if not program:
                    program = Programs(name=prog_name)
                    db.session.add(program)
                    db.session.flush()

                old_priority = Applications.query.filter_by(
                    applicants_id=row['id'],
                    priority=i
                ).first()

                if old_priority:
                    old_priority.program_id = program.id
                else:
                    new_priority = Applications(
                        priority=i,
                        applicants_id=row['id'],
                        program_id=program.id,
                        is_enrolled=False
                    )
                    db.session.add(new_priority)

        db.session.commit()
        flash("Данные успешно загружены!")
        return redirect(url_for('home'))


def run_distribution():

    db.session.query(Applications).update({Applications.is_enrolled: False})
    db.session.commit()

    all_programs = db.session.query(Programs).all()

    prog_limits = {}
    prog_filled = {}

    for prog in all_programs:
        limit = BUDGET.get(prog.name, 0)
        prog_limits[prog.id] = limit
        prog_filled[prog.id] = 0

    candidates = db.session.query(List).filter_by(consent=True).order_by(
        List.summ.desc(),
        List.maths.desc()
    ).all()

    for student in candidates:
        apps = sorted(student.applications, key=lambda x: x.priority)

        for applic in apps:
            prog_id = applic.program_id
            if prog_filled.get(prog_id, 0) < prog_limits.get(prog_id, 0):
                applic.is_enrolled = True
                prog_filled[prog_id] = prog_filled.get(prog_id, 0) + 1
                break

    db.session.commit()


@app.route('/result_pm')
def result_pm():
    run_distribution()
    applicants = db.session.query(List, Applications, Programs). \
        join(Applications, List.id == Applications.applicants_id). \
        join(Programs, Applications.program_id == Programs.id). \
        filter(Programs.name == 'ПМ'). \
        order_by(List.summ.desc()).all()

    count = len(applicants)
    consent_count = 0
    enrolled_count = 0

    if not applicants:
        return render_template('result.html')
    data = []
    for item, applic, prog in applicants:
        if item.consent:
            consent = 'Есть'
            consent_count += 1
            if applic.is_enrolled:
                enrolled_count += 1
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
    html_table = df.to_html(classes='table table-striped', index=False)

    return render_template('result_pm.html',
                           table=html_table,
                           count=count,
                           consent_count=consent_count,
                           enrolled_count=enrolled_count)


@app.route('/result_ivt')
def result_ivt():
    run_distribution()

    applicants = db.session.query(List, Applications, Programs). \
        join(Applications, List.id == Applications.applicants_id). \
        join(Programs, Applications.program_id == Programs.id). \
        filter(Programs.name == 'ИВТ'). \
        order_by(List.summ.desc()).all()

    count = len(applicants)
    consent_count = 0
    enrolled_count = 0

    if not applicants:
        return render_template('result.html')

    data = []
    for item, applic, prog in applicants:
        if item.consent:
            consent = 'Есть'
            consent_count += 1
            if applic.is_enrolled:
                enrolled_count += 1
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
            'Приоритет': applic.priority,
        })

    df = pd.DataFrame(data)
    html_table = df.to_html(classes='table table-striped', index=False)

    return render_template('result_ivt.html',
                           table=html_table,
                           count=count,
                           consent_count=consent_count,
                           enrolled_count=enrolled_count)


@app.route('/result_itss')
def result_itss():
    run_distribution()

    applicants = db.session.query(List, Applications, Programs). \
        join(Applications, List.id == Applications.applicants_id). \
        join(Programs, Applications.program_id == Programs.id). \
        filter(Programs.name == 'ИТСС'). \
        order_by(List.summ.desc()).all()

    count = len(applicants)
    consent_count = 0
    enrolled_count = 0

    if not applicants:
        return render_template('result.html')

    data = []
    for item, applic, prog in applicants:
        if item.consent:
            consent = 'Есть'
            consent_count += 1
            if applic.is_enrolled:
                enrolled_count += 1
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
    html_table = df.to_html(classes='table table-striped', index=False)

    return render_template('result_itss.html',
                           table=html_table,
                           count=count,
                           consent_count=consent_count,
                           enrolled_count=enrolled_count)


@app.route('/result_ib')
def result_ib():
    run_distribution()

    applicants = db.session.query(List, Applications, Programs). \
        join(Applications, List.id == Applications.applicants_id). \
        join(Programs, Applications.program_id == Programs.id). \
        filter(Programs.name == 'ИБ'). \
        order_by(List.summ.desc()).all()

    count = len(applicants)
    consent_count = 0
    enrolled_count = 0

    if not applicants:
        return render_template('result.html')

    data = []
    for item, applic, prog in applicants:
        if item.consent:
            consent = 'Есть'
            consent_count += 1
            if applic.is_enrolled:
                enrolled_count += 1
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
    html_table = df.to_html(classes='table table-striped', index=False)

    return render_template('result_ib.html',
                           table=html_table,
                           count=count,
                           consent_count=consent_count,
                           enrolled_count=enrolled_count)


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

        programs_to_create = ['ПМ', 'ИВТ', 'ИТСС', 'ИБ']
        for program_name in programs_to_create:
            if not db.session.query(Programs).filter_by(name=program_name).first():
                program = Programs(name=program_name)
                db.session.add(program)

        db.session.commit()

        app.run(host='127.0.0.1', port=5000, debug=True)
