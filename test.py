import pandas as pd
import random
import openpyxl

num_rows = 70
directions = ['ПМ', 'ИВТ', 'ИТСС', 'ИБ']
columns_order = ['id', 'Математика', 'Русский', 'Физика/Информатика',
                 'Индивидуальные достижения', 'Сумма', 'Согласие',
                 'Приоритет1', 'Приоритет2', 'Приоритет3', 'Приоритет4']
data = []
idd = 0
pm = 0
itss = 0
ib = 0
ivt = 0
pm_ivt = 0
pm_itss = 0
pm_ib = 0
ivt_itss = 0
ivt_ib = 0
itss_ib = 0
pm_ivt_itss = 0
pm_ivt_ib = 0
ivt_itss_ib = 0
pm_itss_ib = 0
pm_ivt_itss_ib = 0

while pm <= 60 and itss <= 50 and ib <= 70 and ivt <= 100:
    maths = random.randint(40, 100)
    rus = random.randint(40, 100)
    phys_it = random.randint(41, 100)
    ind = random.randint(0, 10)
    summ = maths + rus + phys_it + ind

    if random.random() >= 1 / 3:
        consent = True
    else:
        consent = False

    prio_dict = {d: '-' for d in directions}

    if pm == 60:
        directions.remove('ПМ')
        num_choices = random.randint(1, len(directions))
        random.shuffle(directions)
        new_directions = directions[:num_choices]
        if 'ИВТ' in new_directions:
            ivt += 1
        if 'ИТСС' in new_directions:
            itss += 1
        if 'ИБ' in new_directions:
            ib += 1
        if 'ИВТ' in new_directions and 'ИТСС' in new_directions:
            ivt += 1
            itss += 1
            ivt_itss += 1
        if 'ИВТ' in new_directions and 'ИБ' in new_directions:
            ivt += 1
            ib += 1
            ivt_ib += 1
        if 'ИТСС' in new_directions and 'ИБ' in new_directions:
            itss += 1
            ib += 1
            itss_ib += 1
        if 'ИВТ' in new_directions and 'ИТСС' in new_directions and 'ИБ' in new_directions:
            ivt += 1
            itss += 1
            ib += 1
            ivt_itss_ib += 11
    else:
        num_choices = random.randint(1, len(directions))
        random.shuffle(directions)
        new_directions = directions[:num_choices]

        if 'ПМ' in new_directions:
            pm += 1
        if 'ИВТ' in new_directions:
            ivt += 1
        if 'ИТСС' in new_directions:
            itss += 1
        if 'ИБ' in new_directions:
            ib += 1
        if 'ПМ' in new_directions and 'ИВТ' in new_directions:
            pm += 1
            ivt += 1
            pm_ivt += 1
        if 'ПМ' in new_directions and 'ИТСС' in new_directions:
            pm += 1
            itss += 1
            pm_itss += 1
        if 'ПМ' in new_directions and 'ИБ' in new_directions:
            pm += 1
            ib += 1
            pm_ib += 1
        if 'ИВТ' in new_directions and 'ИТСС' in new_directions:
            ivt += 1
            itss += 1
            ivt_itss += 1
        if 'ИВТ' in new_directions and 'ИБ' in new_directions:
            ivt += 1
            ib += 1
            ivt_ib += 1
        if 'ИТСС' in new_directions and 'ИБ' in new_directions:
            itss += 1
            ib += 1
            itss_ib += 1
        if 'ПМ' in new_directions and 'ИВТ' in new_directions and 'ИТСС' in new_directions:
            pm += 1
            ivt += 1
            itss += 1
            pm_ivt_itss += 1
        if 'ПМ' in new_directions and 'ИВТ' in new_directions and 'ИБ' in new_directions:
            pm += 1
            ivt += 1
            ib += 1
            pm_ivt_ib += 1
        if 'ИВТ' in new_directions and 'ИТСС' in new_directions and 'ИБ' in new_directions:
            ivt += 1
            itss += 1
            ib += 1
            ivt_itss_ib += 1
        if 'ПМ' in new_directions and 'ИТСС' in new_directions and 'ИБ' in new_directions:
            pm += 1
            itss += 1
            ib += 1
            pm_itss_ib += 1
        if 'ПМ' in new_directions and 'ИВТ' in new_directions and 'ИТСС' in new_directions and 'ИБ' in new_directions:
            pm += 1
            itss += 1
            ivt += 1
            ib += 1
            pm_ivt_itss_ib += 1
    if itss == 50:
        directions.remove('ИТСС')
        num_choices = random.randint(1, len(directions))
        random.shuffle(directions)
        new_directions = directions[:num_choices]
        if 'ПМ' in new_directions:
            pm += 1
        if 'ИВТ' in new_directions:
            ivt += 1
        if 'ИБ' in new_directions:
            ib += 1
        if 'ПМ' in new_directions and 'ИВТ' in new_directions:
            pm += 1
            ivt += 1
            pm_ivt += 1
        if 'ПМ' in new_directions and 'ИБ' in new_directions:
            pm += 1
            ib += 1
            pm_ib += 1
        if 'ИВТ' in new_directions and 'ИБ' in new_directions:
            ivt += 1
            ib += 1
            ivt_ib += 1
        if 'ПМ' in new_directions and 'ИВТ' in new_directions and 'ИБ' in new_directions:
            pm += 1
            ivt += 1
            ib += 1
            pm_ivt_ib += 1
    else:
        num_choices = random.randint(1, len(directions))
        random.shuffle(directions)
        new_directions = directions[:num_choices]

        if 'ПМ' in new_directions:
            pm += 1
        if 'ИВТ' in new_directions:
            ivt += 1
        if 'ИТСС' in new_directions:
            itss += 1
        if 'ИБ' in new_directions:
            ib += 1
        if 'ПМ' in new_directions and 'ИВТ' in new_directions:
            pm += 1
            ivt += 1
            pm_ivt += 1
        if 'ПМ' in new_directions and 'ИТСС' in new_directions:
            pm += 1
            itss += 1
            pm_itss += 1
        if 'ПМ' in new_directions and 'ИБ' in new_directions:
            pm += 1
            ib += 1
            pm_ib += 1
        if 'ИВТ' in new_directions and 'ИТСС' in new_directions:
            ivt += 1
            itss += 1
            ivt_itss += 1
        if 'ИВТ' in new_directions and 'ИБ' in new_directions:
            ivt += 1
            ib += 1
            ivt_ib += 1
        if 'ИТСС' in new_directions and 'ИБ' in new_directions:
            itss += 1
            ib += 1
            itss_ib += 1
        if 'ПМ' in new_directions and 'ИВТ' in new_directions and 'ИТСС' in new_directions:
            pm += 1
            ivt += 1
            itss += 1
            pm_ivt_itss += 1
        if 'ПМ' in new_directions and 'ИВТ' in new_directions and 'ИБ' in new_directions:
            pm += 1
            ivt += 1
            ib += 1
            pm_ivt_ib += 1
        if 'ИВТ' in new_directions and 'ИТСС' in new_directions and 'ИБ' in new_directions:
            ivt += 1
            itss += 1
            ib += 1
            ivt_itss_ib += 1
        if 'ПМ' in new_directions and 'ИТСС' in new_directions and 'ИБ' in new_directions:
            pm += 1
            itss += 1
            ib += 1
            pm_itss_ib += 1
        if 'ПМ' in new_directions and 'ИВТ' in new_directions and 'ИТСС' in new_directions and 'ИБ' in new_directions:
            pm += 1
            itss += 1
            ivt += 1
            ib += 1
            pm_ivt_itss_ib += 1
    if ib == 70:
        directions.remove('ИБ')
        num_choices = random.randint(1, len(directions))
        random.shuffle(directions)
        new_directions = directions[:num_choices]
        if 'ПМ' in new_directions:
            pm += 1
        if 'ИВТ' in new_directions:
            ivt += 1
        if 'ИТСС' in new_directions:
            itss += 1
        if 'ПМ' in new_directions and 'ИВТ' in new_directions:
            pm += 1
            ivt += 1
            pm_ivt += 1
        if 'ПМ' in new_directions and 'ИТСС' in new_directions:
            pm += 1
            itss += 1
            pm_itss += 1
        if 'ИВТ' in new_directions and 'ИТСС' in new_directions:
            ivt += 1
            itss += 1
            ivt_itss += 1
        if 'ПМ' in new_directions and 'ИВТ' in new_directions and 'ИТСС' in new_directions:
            pm += 1
            ivt += 1
            itss += 1
            pm_ivt_itss += 1
    else:
        num_choices = random.randint(1, len(directions))
        random.shuffle(directions)
        new_directions = directions[:num_choices]

        if 'ПМ' in new_directions:
            pm += 1
        if 'ИВТ' in new_directions:
            ivt += 1
        if 'ИТСС' in new_directions:
            itss += 1
        if 'ИБ' in new_directions:
            ib += 1
        if 'ПМ' in new_directions and 'ИВТ' in new_directions:
            pm += 1
            ivt += 1
            pm_ivt += 1
        if 'ПМ' in new_directions and 'ИТСС' in new_directions:
            pm += 1
            itss += 1
            pm_itss += 1
        if 'ПМ' in new_directions and 'ИБ' in new_directions:
            pm += 1
            ib += 1
            pm_ib += 1
        if 'ИВТ' in new_directions and 'ИТСС' in new_directions:
            ivt += 1
            itss += 1
            ivt_itss += 1
        if 'ИВТ' in new_directions and 'ИБ' in new_directions:
            ivt += 1
            ib += 1
            ivt_ib += 1
        if 'ИТСС' in new_directions and 'ИБ' in new_directions:
            itss += 1
            ib += 1
            itss_ib += 1
        if 'ПМ' in new_directions and 'ИВТ' in new_directions and 'ИТСС' in new_directions:
            pm += 1
            ivt += 1
            itss += 1
            pm_ivt_itss += 1
        if 'ПМ' in new_directions and 'ИВТ' in new_directions and 'ИБ' in new_directions:
            pm += 1
            ivt += 1
            ib += 1
            pm_ivt_ib += 1
        if 'ИВТ' in new_directions and 'ИТСС' in new_directions and 'ИБ' in new_directions:
            ivt += 1
            itss += 1
            ib += 1
            ivt_itss_ib += 1
        if 'ПМ' in new_directions and 'ИТСС' in new_directions and 'ИБ' in new_directions:
            pm += 1
            itss += 1
            ib += 1
            pm_itss_ib += 1
        if 'ПМ' in new_directions and 'ИВТ' in new_directions and 'ИТСС' in new_directions and 'ИБ' in new_directions:
            pm += 1
            itss += 1
            ivt += 1
            ib += 1
            pm_ivt_itss_ib += 1
    if ivt == 100:
        directions.remove('ИВТ')
        num_choices = random.randint(1, len(directions))
        random.shuffle(directions)
        new_directions = directions[:num_choices]
        if 'ПМ' in new_directions:
            pm += 1
        if 'ИТСС' in new_directions:
            itss += 1
        if 'ИБ' in new_directions:
            ib += 1
        if 'ПМ' in new_directions and 'ИТСС' in new_directions:
            pm += 1
            itss += 1
            pm_itss += 1
        if 'ПМ' in new_directions and 'ИБ' in new_directions:
            pm += 1
            ib += 1
            pm_ib += 1
        if 'ИТСС' in new_directions and 'ИБ' in new_directions:
            itss += 1
            ib += 1
            itss_ib += 1
        if 'ПМ' in new_directions and 'ИТСС' in new_directions and 'ИБ' in new_directions:
            pm += 1
            itss += 1
            ib += 1
            pm_itss_ib += 1
    else:
        num_choices = random.randint(1, len(directions))
        random.shuffle(directions)
        new_directions = directions[:num_choices]

        if 'ПМ' in new_directions:
            pm += 1
        if 'ИВТ' in new_directions:
            ivt += 1
        if 'ИТСС' in new_directions:
            itss += 1
        if 'ИБ' in new_directions:
            ib += 1
        if 'ПМ' in new_directions and 'ИВТ' in new_directions:
            pm += 1
            ivt += 1
            pm_ivt += 1
        if 'ПМ' in new_directions and 'ИТСС' in new_directions:
            pm += 1
            itss += 1
            pm_itss += 1
        if 'ПМ' in new_directions and 'ИБ' in new_directions:
            pm += 1
            ib += 1
            pm_ib += 1
        if 'ИВТ' in new_directions and 'ИТСС' in new_directions:
            ivt += 1
            itss += 1
            ivt_itss += 1
        if 'ИВТ' in new_directions and 'ИБ' in new_directions:
            ivt += 1
            ib += 1
            ivt_ib += 1
        if 'ИТСС' in new_directions and 'ИБ' in new_directions:
            itss += 1
            ib += 1
            itss_ib += 1
        if 'ПМ' in new_directions and 'ИВТ' in new_directions and 'ИТСС' in new_directions:
            pm += 1
            ivt += 1
            itss += 1
            pm_ivt_itss += 1
        if 'ПМ' in new_directions and 'ИВТ' in new_directions and 'ИБ' in new_directions:
            pm += 1
            ivt += 1
            ib += 1
            pm_ivt_ib += 1
        if 'ИВТ' in new_directions and 'ИТСС' in new_directions and 'ИБ' in new_directions:
            ivt += 1
            itss += 1
            ib += 1
            ivt_itss_ib += 1
        if 'ПМ' in new_directions and 'ИТСС' in new_directions and 'ИБ' in new_directions:
            pm += 1
            itss += 1
            ib += 1
            pm_itss_ib += 1
        if 'ПМ' in new_directions and 'ИВТ' in new_directions and 'ИТСС' in new_directions and 'ИБ' in new_directions:
            pm += 1
            itss += 1
            ivt += 1
            ib += 1
            pm_ivt_itss_ib += 1

    row = {
        'id': idd + 1,
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
    idd += 1

df = pd.DataFrame(data, columns=columns_order)
df.to_excel('01.08.xlsx', index=False)
