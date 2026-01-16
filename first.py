import pandas as pd
import random


dirs = ['ПМ', 'ИВТ', 'ИТСС', 'ИБ']
directions = {
    ('ПМ', 'ИВТ', 'ИТСС', 'ИБ'): 3,

    ('ПМ', 'ИВТ', 'ИТСС'): 5,
    ('ПМ', 'ИВТ', 'ИБ'): 5,
    ('ПМ', 'ИТСС', 'ИБ'): 5,
    ('ИВТ', 'ИТСС', 'ИБ'): 5,

    ('ПМ', 'ИВТ'): 22,
    ('ПМ', 'ИТСС'): 17,
    ('ПМ', 'ИБ'): 20,
    ('ИВТ', 'ИТСС'): 19,
    ('ИВТ', 'ИБ'): 22,
    ('ИТСС', 'ИБ'): 17,

    ('ПМ',): 60,
    ('ИВТ',): 100,
    ('ИТСС',): 50,
    ('ИБ',): 70
}

final_counts = {}
group_4 = ('ПМ', 'ИВТ', 'ИТСС', 'ИБ')
final_counts[group_4] = directions[group_4]

for group in directions:
    if len(group) == 3:
        count = directions[group]
        count = count - final_counts[group_4]
        final_counts[group] = count

for group in directions:
    if len(group) == 2:
        count = directions[group]
        for big_group in final_counts:
            first_subject = group[0]
            second_subject = group[1]

            if first_subject in big_group and second_subject in big_group:
                count = count - final_counts[big_group]

        final_counts[group] = count

for group in directions:
    if len(group) == 1:
        count = directions[group]
        subject = group[0]
        for big_group in final_counts:
            if subject in big_group:
                count = count - final_counts[big_group]

        final_counts[group] = count

data = []
current_id = 1

for combo, count in final_counts.items():
    for _ in range(count):
        new_directions = list(combo)
        random.shuffle(new_directions)
        new_directions += [False] * (4 - len(new_directions))

        maths = random.randint(40, 100)
        rus = random.randint(40, 100)
        phys_it = random.randint(41, 100)
        ind = random.randint(0, 10)
        summ = maths + rus + phys_it + ind

        data.append({
            'id': current_id,
            'Математика': maths,
            'Русский': rus,
            'Физика/Информатика': phys_it,
            'Индивидуальные достижения': ind,
            'Сумма': summ,
            'Согласие': random.random() >= 1 / 3,
            'Приоритет1': new_directions[0],
            'Приоритет2': new_directions[1],
            'Приоритет3': new_directions[2],
            'Приоритет4': new_directions[3]
        })
        current_id += 1

df = pd.DataFrame(data)
df.to_excel('01.08.xlsx', index=False)
