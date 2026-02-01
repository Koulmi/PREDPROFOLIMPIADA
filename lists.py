import pandas as pd
import random
from collections import defaultdict

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
        consent = random.random() < 0.1
        maths = random.randint(40, 100)
        rus = random.randint(40, 100)
        phys_it = random.randint(41, 100)
        ind = random.randint(0, 10)
    elif day == '02.08':
        consent = random.random() < 0.4
        if 'ИБ' in priorities or 'ИТСС' in priorities:
            maths = random.randint(52, 100)
            rus = random.randint(52, 100)
            phys_it = random.randint(52, 100)
            ind = random.randint(5, 10)
        else:
            maths = random.randint(40, 85)
            rus = random.randint(40, 85)
            phys_it = random.randint(41, 85)
            ind = random.randint(0, 5)
    elif day == '03.08':
        consent = random.random() < 0.4
        if 'ИБ' in priorities or 'ИТСС' in priorities:
            maths = random.randint(40, 80)
            rus = random.randint(40, 80)
            phys_it = random.randint(41, 80)
            ind = random.randint(0, 5)
        else:
            maths = random.randint(55, 100)
            rus = random.randint(55, 100)
            phys_it = random.randint(55, 100)
            ind = random.randint(5, 10)
    else:
        if 'ПМ' in priorities and 'ИТСС' not in priorities:
            maths = random.randint(87, 100)
            rus = random.randint(87, 100)
            phys_it = random.randint(88, 100)
            ind = random.randint(7, 10)
        elif 'ИТСС' in priorities and 'ПМ' not in priorities:
            maths = random.randint(45, 60)
            rus = random.randint(45, 60)
            phys_it = random.randint(45, 60)
            ind = random.randint(0, 3)
        elif 'ИБ' in priorities and 'ПМ' in priorities and 'ИТСС' not in priorities:
            maths = random.randint(77, 85)
            rus = random.randint(77, 85)
            phys_it = random.randint(78, 85)
            ind = random.randint(6, 9)
        else:
            maths = random.randint(70, 82)
            rus = random.randint(70, 82)
            phys_it = random.randint(71, 82)
            ind = random.randint(4, 7)

        consent = random.random() < 0.6


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
            if random.random() < 0.4:
                prio = [s.get(f'Приоритет{k}') for k in range(1, 5) if s.get(f'Приоритет{k}')]
                maths, rus, phys_it, ind, _ = generate_student_details(day, prio)
                s.update({'Математика': maths, 'Русский': rus, 'Физика/Информатика': phys_it,
                          'Индивидуальные достижения': ind, 'Сумма': maths + rus + phys_it + ind})
                if random.random() < 0.1: s['Согласие'] = not s['Согласие']

        num_existing = len(current_students)
        num_new = int(max(num_existing * 0.15, 60))
        for _ in range(num_new):
            current_students.append({
                'id': next_id, 'Сумма': 0, 'Согласие': False,
                'Приоритет1': None, 'Приоритет2': None, 'Приоритет3': None, 'Приоритет4': None
            })
            next_id += 1

        exclusive_targets = get_exclusive_counts(day_configs[day])

        current_groups = defaultdict(list)
        pool_for_reassignment = []

        for s in current_students:
            if s['Сумма'] == 0:
                pool_for_reassignment.append(s)
            else:
                prio = tuple(sorted([s[f'Приоритет{k}'] for k in range(1, 5) if s[f'Приоритет{k}']]))
                if prio in [tuple(sorted(k)) for k in exclusive_targets.keys()]:
                    current_groups[prio].append(s)
                else:
                    pool_for_reassignment.append(s)

        final_roster = []

        for target_group_tuple, target_count in exclusive_targets.items():
            group_key = tuple(sorted(target_group_tuple))

            existing_candidates = current_groups.get(group_key, [])

            if len(existing_candidates) <= target_count:
                final_roster.extend(existing_candidates)
                needed = target_count - len(existing_candidates)
            else:
                keep = existing_candidates[:target_count]
                excess = existing_candidates[target_count:]
                final_roster.extend(keep)
                pool_for_reassignment.extend(excess)
                needed = 0

            for _ in range(needed):
                if not pool_for_reassignment:
                    s = {'id': next_id, 'Сумма': 0}
                    next_id += 1
                else:
                    s = pool_for_reassignment.pop()

                prio_list = list(target_group_tuple)
                random.shuffle(prio_list)
                prio_list += [None] * (4 - len(prio_list))

                for k in range(4):
                    s[f'Приоритет{k + 1}'] = prio_list[k]
                maths, rus, phys_it, ind, consent = generate_student_details(day, target_group_tuple)
                s.update({'Математика': maths, 'Русский': rus, 'Физика/Информатика': phys_it,
                          'Индивидуальные достижения': ind, 'Сумма': maths + rus + phys_it + ind, 'Согласие': consent})

                final_roster.append(s)

        current_students = final_roster
        df = pd.DataFrame(final_roster)
        df.fillna(value='', inplace=True)

        cols = ['id', 'Математика', 'Русский', 'Физика/Информатика', 'Индивидуальные достижения', 'Сумма', 'Согласие',
                'Приоритет1', 'Приоритет2', 'Приоритет3', 'Приоритет4']
        df = df[cols].sort_values('id')

        filename = f'{day}.xlsx'
        df.to_excel(filename, index=False)


if __name__ == "__main__":
    main()
