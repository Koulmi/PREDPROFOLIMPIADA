import pandas as pd
import random
import os

day_configs = {
    '01.08': {
        'total_counts': {'ПМ': 60, 'ИВТ': 100, 'ИТСС': 50, 'ИБ': 70},
        'intersections': {
            ('ПМ', 'ИВТ'): 22, ('ПМ', 'ИТСС'): 17, ('ПМ', 'ИБ'): 20,
            ('ИВТ', 'ИТСС'): 19, ('ИВТ', 'ИБ'): 22, ('ИТСС', 'ИБ'): 17,
            ('ПМ', 'ИВТ', 'ИТСС'): 5, ('ПМ', 'ИВТ', 'ИБ'): 5,
            ('ИВТ', 'ИТСС', 'ИБ'): 5, ('ПМ', 'ИТСС', 'ИБ'): 5,
            ('ПМ', 'ИВТ', 'ИТСС', 'ИБ'): 3
        }
    },
    '02.08': {
        'total_counts': {'ПМ': 380, 'ИВТ': 370, 'ИТСС': 350, 'ИБ': 260},
        'intersections': {
            ('ПМ', 'ИВТ'): 190, ('ПМ', 'ИТСС'): 190, ('ПМ', 'ИБ'): 150,
            ('ИВТ', 'ИТСС'): 190, ('ИВТ', 'ИБ'): 140, ('ИТСС', 'ИБ'): 120,
            ('ПМ', 'ИВТ', 'ИТСС'): 70, ('ПМ', 'ИВТ', 'ИБ'): 70,
            ('ИВТ', 'ИТСС', 'ИБ'): 70, ('ПМ', 'ИТСС', 'ИБ'): 70,
            ('ПМ', 'ИВТ', 'ИТСС', 'ИБ'): 50
        }
    },
    '03.08': {
        'total_counts': {'ПМ': 1000, 'ИВТ': 1150, 'ИТСС': 1050, 'ИБ': 800},
        'intersections': {
            ('ПМ', 'ИВТ'): 760, ('ПМ', 'ИТСС'): 600, ('ПМ', 'ИБ'): 410,
            ('ИВТ', 'ИТСС'): 750, ('ИВТ', 'ИБ'): 460, ('ИТСС', 'ИБ'): 500,
            ('ПМ', 'ИВТ', 'ИТСС'): 500, ('ПМ', 'ИВТ', 'ИБ'): 260,
            ('ИВТ', 'ИТСС', 'ИБ'): 300, ('ПМ', 'ИТСС', 'ИБ'): 250,
            ('ПМ', 'ИВТ', 'ИТСС', 'ИБ'): 200
        }
    },
    '04.08': {
        'total_counts': {'ПМ': 1240, 'ИВТ': 1390, 'ИТСС': 1240, 'ИБ': 1190},
        'intersections': {
            ('ПМ', 'ИВТ'): 1090, ('ПМ', 'ИТСС'): 1110, ('ПМ', 'ИБ'): 1070,
            ('ИВТ', 'ИТСС'): 1050, ('ИВТ', 'ИБ'): 1040, ('ИТСС', 'ИБ'): 1090,
            ('ПМ', 'ИВТ', 'ИТСС'): 1020, ('ПМ', 'ИВТ', 'ИБ'): 1020,
            ('ИВТ', 'ИТСС', 'ИБ'): 1000, ('ПМ', 'ИТСС', 'ИБ'): 1040,
            ('ПМ', 'ИВТ', 'ИТСС', 'ИБ'): 1000
        }
    }
}


def create_student(student_id, programs, day):
    priorities = list(programs)
    random.shuffle(priorities)
    priorities += [''] * (4 - len(priorities))

    if day == '01.08':
        consent_prob = 0.1
        maths = random.randint(40, 100)
        rus = random.randint(40, 100)
        phys_it = random.randint(41, 100)
        ind = random.randint(0, 10)
    elif day == '02.08':
        consent_prob = 0.4
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
        consent_prob = 0.4
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
        consent_prob = 0.4
        maths = random.randint(40, 100)
        rus = random.randint(40, 100)
        phys_it = random.randint(41, 100)
        ind = random.randint(0, 10)

    return {
        'id': student_id,
        'Математика': maths,
        'Русский': rus,
        'Физика/Информатика': phys_it,
        'Индивидуальные достижения': ind,
        'Сумма': maths + rus + phys_it + ind,
        'Согласие': random.random() <= consent_prob,
        'Приоритет1': priorities[0],
        'Приоритет2': priorities[1],
        'Приоритет3': priorities[2],
        'Приоритет4': priorities[3]
    }


def generate_day_data(day, config):
    all_requirements = config['intersections'].copy()
    for prog, count in config['total_counts'].items():
        all_requirements[(prog,)] = count

    sorted_groups = sorted(all_requirements.keys(), key=len, reverse=True)

    pure_counts = {}

    for group in sorted_groups:
        total_needed = all_requirements[group]

        already_covered = 0
        for existing_group, count in pure_counts.items():
            if set(group).issubset(set(existing_group)):
                already_covered += count

        pure_count = max(0, total_needed - already_covered)
        pure_counts[group] = pure_count
    students = []
    student_id = 1

    for group, count in pure_counts.items():
        for _ in range(count):
            students.append(create_student(student_id, group, day))
            student_id += 1

    df = pd.DataFrame(students)
    filename = f'{day}.xlsx'
    df.to_excel(filename, index=False)


def main():
    for day in day_configs:
        generate_day_data(day, day_configs[day])


if __name__ == "__main__":
    main()
