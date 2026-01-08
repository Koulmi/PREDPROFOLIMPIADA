import pandas as pd
import random

num_rows = 70
directions = ['ПМ', 'ПМ', 'ИВТ', 'ИВТ', 'ИВТ', 'ИТСС', 'ИТСС', 'ИБ']
columns_order = ['id', 'Математика', 'Русский', 'Физика/Информатика',
                 'Индивидуальные достижения', 'Сумма', 'Согласие',
                 'Приоритет1', 'Приоритет2', 'Приоритет3', 'Приоритет4']
data = []

for i in range(num_rows):
    maths = random.randint(40, 100)
    rus = random.randint(40, 100)
    phys_it = random.randint(40, 100)
    ind = random.randint(0, 100)
    summ = maths + rus + phys_it + ind

    if random.random() >= 1 / 3:
        consent = True
    else:
        consent = False

    prio_dict = {d: '-' for d in directions}

    num_choices = random.randint(1, 4)
    random.shuffle(directions)
    new_directions = directions[:num_choices]


    row = {
        'id': i + 1,
        'Математика': maths,
        'Русский': rus,
        'Физика/Информатика': phys_it,
        'Индивидуальные достижения': ind,
        'Сумма': summ,
        'Согласие': consent,
        'Приоритет1': new_directions[0],
        'Приоритет2': new_directions[1] if len(new_directions) > 1 else 'False',
        'Приоритет3': new_directions[2] if len(new_directions) > 2 else 'False',
        'Приоритет4': new_directions[3] if len(new_directions) > 3 else 'False'
    }


    data.append(row)


df = pd.DataFrame(data, columns=columns_order)
df.to_excel('random_table.xlsx', index=False)