import io
import os
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt

from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as PlatypusImage, \
    PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
FONT_NAME = 'Arial'


def calculate_day_statistics(df, budget):
    df = df.copy()
    cols_to_numeric = ['Сумма', 'Математика', 'Русский', 'Физика/Информатика', 'Индивидуальные достижения']
    for col in cols_to_numeric:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    df.fillna('', inplace=True)

    if 'Согласие' in df.columns:
        df['is_consent'] = df['Согласие'].apply(lambda x: True if x == 'Есть' or x is True else False)
    else:
        df['is_consent'] = False

    stats = {prog: {
        'places': limit,
        'total_apps': 0,
        'prio_counts': {1: 0, 2: 0, 3: 0, 4: 0},
        'enrolled_prio_counts': {1: 0, 2: 0, 3: 0, 4: 0},
        'passing_score': "НЕДОБОР",
        'enrolled_list': []
    } for prog, limit in budget.items()}

    for _, row in df.iterrows():
        for i in range(1, 5):
            prog = row.get(f'Приоритет{i}')
            if prog in budget:
                stats[prog]['total_apps'] += 1
                stats[prog]['prio_counts'][i] += 1

    sort_cols = ['Сумма', 'Математика', 'Русский', 'Физика/Информатика', 'Индивидуальные достижения']
    existing_sort_cols = [c for c in sort_cols if c in df.columns]
    ascending_order = [False] * len(existing_sort_cols)

    candidates = df[df['is_consent'] == True].sort_values(by=existing_sort_cols, ascending=ascending_order)

    filled_counts = {prog: 0 for prog in budget}

    for _, row in candidates.iterrows():
        for i in range(1, 5):
            prog = row.get(f'Приоритет{i}')
            if prog in budget and filled_counts[prog] < budget[prog]:
                filled_counts[prog] += 1

                stats[prog]['enrolled_list'].append({
                    'id': row['id'],
                    'score': int(row['Сумма']),
                    'priority': i
                })
                stats[prog]['enrolled_prio_counts'][i] += 1
                break

    for prog in budget:
        enrolled = stats[prog]['enrolled_list']
        limit = budget[prog]

        if len(enrolled) == limit:
            min_score = min(s['score'] for s in enrolled)
            stats[prog]['passing_score'] = min_score
        else:
            stats[prog]['passing_score'] = "НЕДОБОР"

    return stats


def generate_pdf_report(upload_folder, budget, current_day='01.08'):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=30, bottomMargin=30)
    elements = []

    styles = getSampleStyleSheet()
    style_normal = ParagraphStyle('CyrillicNormal', parent=styles['Normal'], fontName=FONT_NAME, fontSize=10)
    style_heading = ParagraphStyle('CyrillicHeading', parent=styles['Heading1'], fontName=FONT_NAME,
                                   alignment=TA_CENTER, spaceAfter=15)
    style_subheading = ParagraphStyle('CyrillicSubHeading', parent=styles['Heading2'], fontName=FONT_NAME,
                                      spaceAfter=10)

    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    elements.append(Paragraph(f"Отчет сформирован: {now}", style_normal))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(f"Отчет приемной комиссии за {current_day}", style_heading))

    file_path = os.path.join(upload_folder, f'{current_day}.xlsx')

    if not os.path.exists(file_path):
        elements.append(Paragraph(f"Файл данных за {current_day} не найден", style_normal))
        doc.build(elements)
        buffer.seek(0)
        return buffer

    df = pd.read_excel(file_path)
    current_stats = calculate_day_statistics(df, budget)

    all_days = ['01.08', '02.08', '03.08', '04.08']
    history_scores = {prog: [] for prog in budget}

    for day in all_days:
        if day == current_day:
            for prog in budget:
                score = current_stats[prog]['passing_score']
                val = score if isinstance(score, (int, float)) else 0
                history_scores[prog].append(val)
            break
        else:
            hist_file_path = os.path.join(upload_folder, f'{day}.xlsx')
            if os.path.exists(hist_file_path):
                hist_df = pd.read_excel(hist_file_path)
                hist_stats = calculate_day_statistics(hist_df, budget)
                for prog in budget:
                    score = hist_stats[prog]['passing_score']
                    val = score if isinstance(score, (int, float)) else 0
                    history_scores[prog].append(val)
            else:
                for prog in budget:
                    history_scores[prog].append(0)

    if len(history_scores[list(budget.keys())[0]]) > 0:
        elements.append(Paragraph("c. Динамика проходного балла (с начала до текущего дня):", style_subheading))

        plt.figure(figsize=(8, 5))

        days_for_chart = []
        for day in all_days:
            days_for_chart.append(day)
            if day == current_day:
                break

        x = np.arange(len(days_for_chart))
        width = 0.2
        multiplier = 0

        for prog in budget:
            scores = history_scores[prog][:len(days_for_chart)]
            offset = width * multiplier
            rects = plt.bar(x + offset, scores, width, label=prog)
            multiplier += 1

        plt.title(f"Динамика проходных баллов (до {current_day})")
        plt.xlabel("Дата")
        plt.ylabel("Проходной балл")
        plt.xticks(x + width * 1.5, days_for_chart)
        plt.legend(loc='upper left', ncols=4)
        plt.grid(axis='y', linestyle='--', alpha=0.7)

        all_scores = []
        for prog in budget:
            all_scores.extend(history_scores[prog][:len(days_for_chart)])
        max_val = max(all_scores) if all_scores and max(all_scores) > 0 else 300
        plt.ylim(0, max_val + 10)

        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=100)
        img_buffer.seek(0)
        plt.close()

        im = PlatypusImage(img_buffer, width=480, height=300)
        elements.append(im)
        elements.append(Spacer(1, 15))

    elements.append(PageBreak())
    elements.append(Paragraph(f"d. Списки зачисленных абитуриентов на {current_day}:", style_subheading))

    for prog in budget:
        elements.append(Paragraph(f"<b>Направление: {prog}</b>", style_subheading))

        enrolled = current_stats[prog]['enrolled_list']

        if not enrolled:
            elements.append(Paragraph("Нет зачисленных", style_normal))
        else:
            enrolled_sorted = sorted(enrolled, key=lambda x: x['score'], reverse=True)
            table_data = [['ID', 'Балл', 'Приоритет']]
            for student in enrolled_sorted:
                table_data.append([
                    str(student['id']),
                    str(student['score']),
                    str(student['priority'])
                ])

            t = Table(table_data, colWidths=[100, 80, 80])
            t.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ]))
            t.hAlign = 'LEFT'
            elements.append(t)

        elements.append(Spacer(1, 15))

    elements.append(PageBreak())
    elements.append(Paragraph(f"e. Статистика по каждой ОП на {current_day}:", style_subheading))

    header = ['Показатель'] + list(budget.keys())
    row_total = ['Общее кол-во заявлений']
    row_places = ['Количество мест на ОП']

    rows_prio_apps = {i: [f'Заявлений {i}-го приоритета'] for i in range(1, 5)}
    rows_enrolled_prio = {i: [f'Зачислено {i}-го приоритета'] for i in range(1, 5)}

    for prog in budget:
        s = current_stats[prog]
        row_total.append(s['total_apps'])
        row_places.append(s['places'])
        for i in range(1, 5):
            rows_prio_apps[i].append(s['prio_counts'][i])
            rows_enrolled_prio[i].append(s['enrolled_prio_counts'][i])

    table_data = [header, row_total, row_places]
    for i in range(1, 5): table_data.append(rows_prio_apps[i])
    for i in range(1, 5): table_data.append(rows_enrolled_prio[i])

    t = Table(table_data, colWidths=[180, 50, 50, 50, 50])
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(t)

    doc.build(elements)
    buffer.seek(0)
    return buffer