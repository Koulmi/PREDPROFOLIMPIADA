import pandas as pd
import random
import os

day_configs = {
    '01.08': {
        'total': {'ПМ': 60, 'ИВТ': 100, 'ИТСС': 50, 'ИБ': 70},
        'combos': {
            ('ПМ', 'ИВТ'): 22, ('ПМ', 'ИТСС'): 17, ('ПМ', 'ИБ'): 20,
            ('ИВТ', 'ИТСС'): 19, ('ИВТ', 'ИБ'): 22, ('ИТСС', 'ИБ'): 17,
            ('ПМ', 'ИВТ', 'ИТСС'): 5, ('ПМ', 'ИВТ', 'ИБ'): 5,
            ('ИВТ', 'ИТСС', 'ИБ'): 5, ('ПМ', 'ИТСС', 'ИБ'): 5,
            ('ПМ', 'ИВТ', 'ИТСС', 'ИБ'): 3
        }
    },
    '02.08': {
        'total': {'ПМ': 380, 'ИВТ': 370, 'ИТСС': 350, 'ИБ': 260},
        'combos': {
            ('ПМ', 'ИВТ'): 190, ('ПМ', 'ИТСС'): 190, ('ПМ', 'ИБ'): 150,
            ('ИВТ', 'ИТСС'): 190, ('ИВТ', 'ИБ'): 140, ('ИТСС', 'ИБ'): 120,
            ('ПМ', 'ИВТ', 'ИТСС'): 70, ('ПМ', 'ИВТ', 'ИБ'): 70,
            ('ИВТ', 'ИТСС', 'ИБ'): 70, ('ПМ', 'ИТСС', 'ИБ'): 70,
            ('ПМ', 'ИВТ', 'ИТСС', 'ИБ'): 50
        }
    },
    '03.08': {
        'total': {'ПМ': 1000, 'ИВТ': 1150, 'ИТСС': 1050, 'ИБ': 800},
        'combos': {
            ('ПМ', 'ИВТ'): 760, ('ПМ', 'ИТСС'): 600, ('ПМ', 'ИБ'): 410,
            ('ИВТ', 'ИТСС'): 750, ('ИВТ', 'ИБ'): 460, ('ИТСС', 'ИБ'): 500,
            ('ПМ', 'ИВТ', 'ИТСС'): 500, ('ПМ', 'ИВТ', 'ИБ'): 260,
            ('ИВТ', 'ИТСС', 'ИБ'): 300, ('ПМ', 'ИТСС', 'ИБ'): 250,
            ('ПМ', 'ИВТ', 'ИТСС', 'ИБ'): 200
        }
    },
    '04.08': {
        'total': {'ПМ': 1240, 'ИВТ': 1390, 'ИТСС': 1240, 'ИБ': 1190},
        'combos': {
            ('ПМ', 'ИВТ'): 1090, ('ПМ', 'ИТСС'): 1110, ('ПМ', 'ИБ'): 1070,
            ('ИВТ', 'ИТСС'): 1050, ('ИВТ', 'ИБ'): 1040, ('ИТСС', 'ИБ'): 1090,
            ('ПМ', 'ИВТ', 'ИТСС'): 1020, ('ПМ', 'ИВТ', 'ИБ'): 1020,
            ('ИВТ', 'ИТСС', 'ИБ'): 1000, ('ПМ', 'ИТСС', 'ИБ'): 1040,
            ('ПМ', 'ИВТ', 'ИТСС', 'ИБ'): 1000
        }
    }
}


def generate_student_details(day, priorities):
    if day == '01.08':
        consent = 0.1
        maths = random.randint(40, 100)
        rus = random.randint(40, 100)
        phys_it = random.randint(41, 100)
        ind = random.randint(0, 10)
    elif day == '02.08':
        consent = 0.4
        if 'ИБ' in priorities or 'ИТСС' in priorities:
            maths = random.randint(50, 100)
            rus = random.randint(50, 100)
            phys_it = random.randint(51, 100)
            ind = random.randint(5, 10)
        else:
            maths = random.randint(40, 90)
            rus = random.randint(40, 90)
            phys_it = random.randint(41, 90)
            ind = random.randint(0, 5)
    elif day == '03.08':
        consent = 0.4
        if 'ИБ' in priorities or 'ИТСС' in priorities:
            maths = random.randint(40, 90)
            rus = random.randint(40, 90)
            phys_it = random.randint(41, 90)
            ind = random.randint(0, 5)
        else:
            maths = random.randint(50, 100)
            rus = random.randint(50, 100)
            phys_it = random.randint(51, 100)
            ind = random.randint(5, 10)
    else:
        if 'ПМ' in priorities:
            maths  = random.randint(85, 100)
            rus = random.randint(85, 100)
            phys_it = random.randint(85, 100)
            ind = random.randint(7, 10)
        elif 'ИБ' in priorities:
            maths = random.randint(75, 95)
            rus = random.randint(75, 95)
            phys_it = random.randint(75, 95)
            ind = random.randint(6, 9)
        elif 'ИВТ' in priorities:
            maths = random.randint(65, 85)
            rus = random.randint(65, 85)
            phys_it = random.randint(65, 85)
            ind = random.randint(5, 8)
        else:
            maths = random.randint(60, 80)
            rus = random.randint(60, 80)
            phys_it = random.randint(60, 80)
            ind = random.randint(0, 6)
        consent = random.random() < 0.8


    return maths, rus, phys_it, ind, consent


def get_exclusive_counts(config):
    targets = config['combos'].copy()
    for prog, count in config['total'].items():
        targets[(prog,)] = count

    sorted_groups = sorted(targets.keys(), key=len, reverse=True)

    exclusive_counts = {}

    for group in sorted_groups:
        total_needed = targets[group]
        already_covered = 0
        for super_group, count in exclusive_counts.items():
            if set(group).issubset(set(super_group)):
                already_covered += count

        pure_needed = max(0, total_needed - already_covered)
        exclusive_counts[group] = pure_needed

    return exclusive_counts


def main():
    current_students = []
    next_id = 1

    for day in ['01.08', '02.08', '03.08', '04.08']:

        if current_students:
            drop_rate = random.uniform(0.05, 0.10)
            keep_count = int(len(current_students) * (1 - drop_rate))
            current_students = random.sample(current_students, keep_count)

        for s in current_students:
            if random.random() < 0.5:
                if random.random() < 0.2: s['Согласие'] = not s['Согласие']
                prio = [s.get(f'Приоритет{k}') for k in range(1, 5) if s.get(f'Приоритет{k}')]
                math, rus, phys_it, ind, consent = generate_student_details(day, prio)
                s.update({'Математика': math, 'Русский': rus, 'Физика/Информатика': phys_it,
                          'Индивидуальные достижения': ind, 'Сумма': math + rus + phys_it + ind})


        num_existing = len(current_students)
        num_new = int(max(num_existing * 0.15, 60))

        for _ in range(num_new):
            current_students.append({
                'id': next_id,
                'Приоритет1': None,
                'Приоритет2': None,
                'Приоритет3': None,
                'Приоритет4': None,
                'Математика': 0,
                'Русский': 0,
                'Физика/Информатика': 0,
                'Индивидуальные достижения': 0,
                'Сумма': 0,
                'Согласие': False
            })
            next_id += 1

        exclusive_targets = get_exclusive_counts(day_configs[day])

        student_idx = 0
        total_students_needed = sum(exclusive_targets.values())

        while len(current_students) < total_students_needed:
            current_students.append({
                'id': next_id,
                'Приоритет1': None,
                'Приоритет2': None,
                'Приоритет3': None,
                'Приоритет4': None,
                'Математика': 0,
                'Русский': 0,
                'Физика/Информатика': 0,
                'Индивидуальные достижения': 0,
                'Сумма': 0,
                'Согласие': False
            })
            next_id += 1

        random.shuffle(current_students)

        for group, count in exclusive_targets.items():
            for _ in range(count):
                if student_idx >= len(current_students):
                    break

                s = current_students[student_idx]
                prio_list = list(group)
                random.shuffle(prio_list)
                prio_list += [None] * (4 - len(prio_list))

                for k in range(4):
                    s[f'Приоритет{k + 1}'] = prio_list[k]

                if s['Сумма'] == 0:
                    math, rus, phys_it, ind, consent = generate_student_details(day, group)
                    s.update({'Математика': math, 'Русский': rus, 'Физика/Информатика': phys_it,
                              'Индивидуальные достижения': ind, 'Сумма': math + rus + phys_it + ind, 'Согласие': consent})
                else:
                    _, _, _, _, consent = generate_student_details(day, group)
                    s['Согласие'] = consent

                student_idx += 1

        current_students = current_students[:total_students_needed]
        df = pd.DataFrame(current_students)
        df.fillna(value='', inplace=True)

        cols = ['id', 'Математика', 'Русский', 'Физика/Информатика', 'Индивидуальные достижения', 'Сумма', 'Согласие',
                'Приоритет1', 'Приоритет2', 'Приоритет3', 'Приоритет4']
        df = df[cols].sort_values('id')

        filename = f'{day}.xlsx'
        df.to_excel(filename, index=False)


if __name__ == "__main__":
    main()

