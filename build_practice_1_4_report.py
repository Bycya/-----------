from pathlib import Path
import re

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor


ROOT = Path('/Users/lubovgoraeva/Downloads')
SOURCE_MAIN = Path('/Users/lubovgoraeva/.codex/attachments/217057b3-7fa2-44cb-a1ea-2fc4eee794d7/Pasted text.txt')
SOURCE_EXTRA = Path('/Users/lubovgoraeva/.codex/attachments/0c9f597e-8b3a-4d05-bdd4-754c12e33347/Pasted text.txt')
OUTPUT = ROOT / 'practice_1_4_isolation_triggers_fts_report.docx'


def between(text: str, start: str, end: str | None = None) -> str:
    begin = text.index(start)
    finish = text.index(end, begin) if end else len(text)
    return text[begin:finish].strip()


main_text = SOURCE_MAIN.read_text(encoding='utf-8')
extra_text = SOURCE_EXTRA.read_text(encoding='utf-8')

# Из первого материала берутся подготовка и триггеры. Старый сценарий
# потерянного изменения намеренно исключён: во втором материале он исправлен
# и использует требуемые условием инкременты.
preparation = between(main_text, '## 1. Подготовка тестовых данных', '# READ COMMITTED')
isolation = between(extra_text, '# 1. Сводная таблица уровней изоляции', '# 7. Оптимизация полнотекстового поиска')
triggers = between(main_text, '# Триггер №1: управление свободными местами')
fts = between(extra_text, '# 7. Оптимизация полнотекстового поиска', '# 8. Выводы по практической работе 1.4')
conclusions = between(extra_text, '# 8. Выводы по практической работе 1.4')

preparation = preparation.replace('## 1. Подготовка тестовых данных', '# 2. Подготовка тестовых данных', 1)
preparation = preparation.replace('## 2. Создание двух параллельных сеансов', '# 3. Организация двух параллельных сеансов', 1)

renumber = {
    '# 1. Сводная таблица уровней изоляции': '# 4. Сводная таблица уровней изоляции',
    '# 2. Потерянное изменение через инкременты': '# 5. Потерянное изменение через инкременты',
    '# 3. Грязное чтение': '# 6. Грязное чтение',
    '# 4. Неповторяющееся чтение': '# 7. Неповторяющееся чтение',
    '# 5. Фантомное чтение': '# 8. Фантомное чтение',
    '# 6. Аномалия сериализации': '# 9. Аномалия сериализации',
    '## 6.1. Последовательное выполнение на REPEATABLE READ': '## 9.1. Последовательное выполнение на REPEATABLE READ',
    '## 6.2. Параллельное выполнение на REPEATABLE READ': '## 9.2. Параллельное выполнение на REPEATABLE READ',
    '## 6.3. Параллельное выполнение на SERIALIZABLE': '## 9.3. Параллельное выполнение на SERIALIZABLE',
}
for old, new in renumber.items():
    isolation = isolation.replace(old, new, 1)

triggers = triggers.replace('# Триггер №1: управление свободными местами', '# 10. Триггеры обеспечения целостности\n\n## 10.1. Управление свободными местами', 1)
triggers = triggers.replace('# Триггер №2: запрет переплаты', '## 10.2. Запрет переплаты', 1)
fts = fts.replace('# 7. Оптимизация полнотекстового поиска', '# 11. Оптимизация полнотекстового поиска', 1)
conclusions = conclusions.replace('# 8. Выводы по практической работе 1.4', '# 12. Выводы по практической работе 1.4', 1)

intro = '''# 1. Цель и задачи работы

Цель работы — исследовать параллельное выполнение транзакций PostgreSQL на уровнях изоляции READ UNCOMMITTED, READ COMMITTED, REPEATABLE READ и SERIALIZABLE, проверить наличие транзакционных аномалий, создать триггеры для сохранения целостности данных и оценить эффективность полнотекстового GIN-индекса.

Эксперименты выполняются на базе данных туристической фирмы первого семестра. Для транзакционных сценариев используется таблица `tours`; триггеры работают с таблицами `tours`, `bookings` и `payments`; полнотекстовый поиск выполняется по таблице `destinations`.

В работе проверяются:

- потерянное изменение при двух инкрементах одного поля;
- грязное чтение;
- неповторяющееся чтение;
- фантомное чтение;
- аномалия сериализации при последовательном и параллельном выполнении;
- изменение данных триггером и откат транзакции при нарушении целостности;
- изменение плана и времени полнотекстового поиска после создания GIN-индекса.
'''

report_markdown = '\n\n'.join([intro, preparation, isolation, triggers, fts, conclusions])


def set_cell_shading(cell, fill: str):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn('w:shd'))
    if shd is None:
        shd = OxmlElement('w:shd')
        tc_pr.append(shd)
    shd.set(qn('w:fill'), fill)


def set_cell_margins(cell, top=80, start=90, bottom=80, end=90):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in('w:tcMar')
    if tc_mar is None:
        tc_mar = OxmlElement('w:tcMar')
        tc_pr.append(tc_mar)
    for margin, value in [('top', top), ('start', start), ('bottom', bottom), ('end', end)]:
        node = tc_mar.find(qn(f'w:{margin}'))
        if node is None:
            node = OxmlElement(f'w:{margin}')
            tc_mar.append(node)
        node.set(qn('w:w'), str(value))
        node.set(qn('w:type'), 'dxa')


def set_run_font(run, name='Times New Roman', size=14, bold=None, italic=None, color=None):
    run.font.name = name
    run._element.rPr.rFonts.set(qn('w:eastAsia'), name)
    run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic
    if color:
        run.font.color.rgb = RGBColor(*color)


def add_inline(paragraph, text: str, size=14):
    # Поддержка основных элементов Markdown: **жирный** и `моноширинный`.
    pattern = re.compile(r'(\*\*.+?\*\*|`[^`]+`)')
    position = 0
    for match in pattern.finditer(text):
        if match.start() > position:
            set_run_font(paragraph.add_run(text[position:match.start()]), size=size)
        token = match.group(0)
        if token.startswith('**'):
            set_run_font(paragraph.add_run(token[2:-2]), size=size, bold=True)
        else:
            set_run_font(paragraph.add_run(token[1:-1]), name='Consolas', size=max(size - 2, 8))
        position = match.end()
    if position < len(text):
        set_run_font(paragraph.add_run(text[position:]), size=size)


def clean_table_cell(value: str) -> str:
    value = value.strip()
    value = re.sub(r'^`(.*)`$', r'\1', value)
    value = value.replace('**', '')
    return value


def add_markdown_table(doc, rows):
    width = max(len(row) for row in rows)
    normalized = [row + [''] * (width - len(row)) for row in rows]
    table = doc.add_table(rows=len(normalized), cols=width)
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = True
    for r_index, row in enumerate(normalized):
        for c_index, value in enumerate(row):
            cell = table.cell(r_index, c_index)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            set_cell_margins(cell)
            if r_index == 0:
                set_cell_shading(cell, 'D9EAF7')
            paragraph = cell.paragraphs[0]
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER if r_index == 0 else WD_ALIGN_PARAGRAPH.LEFT
            paragraph.paragraph_format.space_after = Pt(0)
            paragraph.paragraph_format.line_spacing = 1.0
            run = paragraph.add_run(clean_table_cell(value))
            set_run_font(run, size=9.5, bold=(r_index == 0))
    # Заголовок таблицы повторяется на новых страницах.
    tr_pr = table.rows[0]._tr.get_or_add_trPr()
    tbl_header = OxmlElement('w:tblHeader')
    tbl_header.set(qn('w:val'), 'true')
    tr_pr.append(tbl_header)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)


def add_code_block(doc, lines, language=''):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = True
    cell = table.cell(0, 0)
    set_cell_shading(cell, 'F2F2F2')
    set_cell_margins(cell, top=100, start=120, bottom=100, end=120)
    paragraph = cell.paragraphs[0]
    paragraph.paragraph_format.space_after = Pt(0)
    paragraph.paragraph_format.line_spacing = 1.0
    text = '\n'.join(lines).rstrip()
    run = paragraph.add_run(text)
    set_run_font(run, name='Consolas', size=8.5)
    if language:
        paragraph.style = doc.styles['Code Block']
    doc.add_paragraph().paragraph_format.space_after = Pt(0)


def parse_table(lines, start):
    rows = []
    index = start
    while index < len(lines) and lines[index].strip().startswith('|'):
        cells = [cell.strip() for cell in lines[index].strip().strip('|').split('|')]
        rows.append(cells)
        index += 1
    if len(rows) >= 2 and all(re.fullmatch(r':?-{3,}:?', cell.replace(' ', '')) for cell in rows[1]):
        rows.pop(1)
    return rows, index


def render_markdown(doc, markdown):
    lines = markdown.splitlines()
    index = 0
    paragraph_buffer = []

    def flush_paragraph():
        nonlocal paragraph_buffer
        if not paragraph_buffer:
            return
        text = ' '.join(part.strip() for part in paragraph_buffer).strip()
        if text:
            paragraph = doc.add_paragraph()
            paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            paragraph.paragraph_format.first_line_indent = Cm(1.25)
            paragraph.paragraph_format.space_after = Pt(6)
            paragraph.paragraph_format.line_spacing = 1.5
            add_inline(paragraph, text)
        paragraph_buffer = []

    while index < len(lines):
        raw = lines[index]
        stripped = raw.strip()

        if stripped.startswith('```'):
            flush_paragraph()
            language = stripped[3:].strip()
            index += 1
            code = []
            while index < len(lines) and not lines[index].strip().startswith('```'):
                code.append(lines[index])
                index += 1
            add_code_block(doc, code, language)
            index += 1
            continue

        if stripped.startswith('|') and index + 1 < len(lines) and lines[index + 1].strip().startswith('|'):
            flush_paragraph()
            rows, index = parse_table(lines, index)
            add_markdown_table(doc, rows)
            continue

        heading = re.match(r'^(#{1,3})\s+(.+)$', stripped)
        if heading:
            flush_paragraph()
            level = len(heading.group(1))
            paragraph = doc.add_paragraph(style=f'Heading {level}')
            paragraph.paragraph_format.keep_with_next = True
            add_inline(paragraph, heading.group(2), size={1: 16, 2: 14, 3: 14}[level])
            index += 1
            continue

        if re.fullmatch(r'-{3,}', stripped):
            flush_paragraph()
            index += 1
            continue

        bullet = re.match(r'^[-*]\s+(.+)$', stripped)
        if bullet:
            flush_paragraph()
            paragraph = doc.add_paragraph(style='List Bullet')
            paragraph.paragraph_format.space_after = Pt(3)
            paragraph.paragraph_format.line_spacing = 1.15
            add_inline(paragraph, bullet.group(1))
            index += 1
            continue

        numbered = re.match(r'^(\d+)\.\s+(.+)$', stripped)
        if numbered:
            flush_paragraph()
            paragraph = doc.add_paragraph(style='List Number')
            paragraph.paragraph_format.space_after = Pt(3)
            paragraph.paragraph_format.line_spacing = 1.15
            add_inline(paragraph, numbered.group(2))
            index += 1
            continue

        if not stripped:
            flush_paragraph()
        else:
            paragraph_buffer.append(stripped)
        index += 1
    flush_paragraph()


def add_field(paragraph, instruction: str, placeholder=''):
    begin = OxmlElement('w:fldChar')
    begin.set(qn('w:fldCharType'), 'begin')
    instr = OxmlElement('w:instrText')
    instr.set(qn('xml:space'), 'preserve')
    instr.text = instruction
    separate = OxmlElement('w:fldChar')
    separate.set(qn('w:fldCharType'), 'separate')
    text = OxmlElement('w:t')
    text.text = placeholder
    end = OxmlElement('w:fldChar')
    end.set(qn('w:fldCharType'), 'end')
    run = paragraph.add_run()._r
    run.extend([begin, instr, separate, text, end])


doc = Document()
section = doc.sections[0]
section.page_width = Cm(21)
section.page_height = Cm(29.7)
section.top_margin = Cm(2)
section.bottom_margin = Cm(2)
section.left_margin = Cm(3)
section.right_margin = Cm(1.5)

styles = doc.styles
normal = styles['Normal']
normal.font.name = 'Times New Roman'
normal._element.rPr.rFonts.set(qn('w:eastAsia'), 'Times New Roman')
normal.font.size = Pt(14)
normal.paragraph_format.line_spacing = 1.5

for level, size in [(1, 16), (2, 14), (3, 14)]:
    style = styles[f'Heading {level}']
    style.font.name = 'Times New Roman'
    style._element.rPr.rFonts.set(qn('w:eastAsia'), 'Times New Roman')
    style.font.size = Pt(size)
    style.font.bold = True
    style.font.color.rgb = RGBColor(0, 0, 0)
    style.paragraph_format.space_before = Pt(12)
    style.paragraph_format.space_after = Pt(6)
    style.paragraph_format.keep_with_next = True

if 'Code Block' not in styles:
    code_style = styles.add_style('Code Block', WD_STYLE_TYPE.PARAGRAPH)
else:
    code_style = styles['Code Block']
code_style.font.name = 'Consolas'
code_style._element.rPr.rFonts.set(qn('w:eastAsia'), 'Consolas')
code_style.font.size = Pt(8.5)
code_style.paragraph_format.line_spacing = 1.0
code_style.paragraph_format.space_after = Pt(0)

# Титульный лист.
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_after = Pt(3)
set_run_font(p.add_run('ОБРАЗОВАТЕЛЬНАЯ ОРГАНИЗАЦИЯ'), size=12)
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
set_run_font(p.add_run('Кафедра ______________________________'), size=12)

for _ in range(5):
    doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
set_run_font(p.add_run('ОТЧЁТ'), size=18, bold=True)
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
set_run_font(p.add_run('по практической работе № 1.4'), size=16, bold=True)
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(10)
set_run_font(p.add_run('«Транзакции, триггеры и оптимизация полнотекстового поиска в PostgreSQL»'), size=14, bold=True)

for _ in range(5):
    doc.add_paragraph()

for label in ['Выполнил(а): студент(ка) группы __________', '________________________________________', 'Проверил(а): ___________________________']:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    set_run_font(p.add_run(label), size=12)

for _ in range(4):
    doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
set_run_font(p.add_run('Москва — 2026'), size=12)
doc.add_page_break()

# Автоматическое оглавление. В Word его можно обновить через контекстное меню.
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
set_run_font(p.add_run('СОДЕРЖАНИЕ'), size=16, bold=True)
toc = doc.add_paragraph()
add_field(toc, 'TOC \\o "1-3" \\h \\z \\u', 'Щёлкните правой кнопкой и выберите «Обновить поле»')
doc.add_page_break()

render_markdown(doc, report_markdown)

# Номера страниц в нижнем колонтитуле.
footer = section.footer
footer_p = footer.paragraphs[0]
footer_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
add_field(footer_p, 'PAGE', '1')

# Просим Word обновить вычисляемые поля при открытии.
settings = doc.settings._element
update_fields = settings.find(qn('w:updateFields'))
if update_fields is None:
    update_fields = OxmlElement('w:updateFields')
    settings.append(update_fields)
update_fields.set(qn('w:val'), 'true')

core = doc.core_properties
core.title = 'Практическая работа № 1.4: транзакции, триггеры и полнотекстовый поиск'
core.subject = 'PostgreSQL: уровни изоляции, аномалии транзакций, триггеры и GIN-индекс'
core.author = 'Любовь Гораева'
core.keywords = 'PostgreSQL, транзакции, уровни изоляции, триггеры, полнотекстовый поиск, GIN'

doc.save(OUTPUT)
print(OUTPUT)
