import os
import re
from .settings import MEDIA_ROOT
import pandas as pd

pd.set_option('display.max_columns', 10)


def normalize_name(full_name: str) -> str:
    """
    Преобразует строку имени в формат "Фамилия, Имя Отчество" (одна запятая).
    Если в имени несколько частей, последняя считается фамилией.
    """
    if not isinstance(full_name, str) or full_name.strip() == '' or full_name == 'Invalid Staff ID':
        return full_name
    parts = full_name.strip().split(", ")
    if len(parts) == 1:
        return parts[0]
    surname = parts[0]
    given = ' '.join(parts[1:])
    return f"{surname}, {given}"


def clean_id(x) -> str:
    """
    Очищает значение ID: убирает пробелы, лишний ".0" у числовых значений,
    остаются только буквы и цифры.
    """
    s = str(x).strip()
    # если это числовое представление с .0 — убираем дробную часть
    if re.fullmatch(r'\d+\.0+', s):
        s = s.split('.', 1)[0]
    # удаляем всё, кроме букв и цифр
    return re.sub(r'[^A-Za-z0-9]', '', s).lower()


def get_workers_list(username):
    """
    Загружает и обрабатывает списки эвакуации (evac.xlsx) и дыхания (breath.xlsx)
    для указанного пользователя, возвращает объединенный DataFrame со статусами сотрудников.
    """
    # Пути к файлам
    user_media_dir = os.path.join(MEDIA_ROOT, username)
    evac_path = os.path.join(user_media_dir, 'evac.xlsx')
    breath_path = os.path.join(user_media_dir, 'breath.xlsx')

    # Чтение данных
    df_evac = pd.read_excel(evac_path)
    df_breath = pd.read_excel(breath_path)
    if df_breath.empty:
        return pd.DataFrame()

    # Инициализация
    df_breath['Comment'] = ''

    # Очистка ID
    df_evac['EmployeeID'] = df_evac['EmployeeID'].apply(clean_id)
    df_breath['Staff ID'] = df_breath['Staff ID'].apply(clean_id)

    # Нормализация имён
    df_evac['Name'] = df_evac['Name'].apply(normalize_name)
    df_breath['Name'] = df_breath['Staff Name'].apply(normalize_name)
    df_breath['OriginalName'] = df_breath['Staff Name']

    # Последние замеры дыхания внутри файла
    df_breath['Time'] = pd.to_datetime(df_breath['Time'], format='%H:%M:%S', errors='coerce')
    max_times = df_breath.groupby(['Staff ID', 'Name'], as_index=False)['Time'].max()
    df_breath = df_breath.merge(max_times, on=['Staff ID', 'Name', 'Time'], how='inner')
    df_breath = df_breath.rename(columns={'Staff ID': 'StaffID'})

    # Переименование поля статуса работы
    df_evac = df_evac.rename(columns={'Work Status': 'WorkStatus'})

    # Пометка отсутствующих и корректировка имён по ID
    missing_mask = ~df_breath['Name'].isin(df_evac['Name'])
    df_breath.loc[missing_mask, 'Comment'] = 'ERROR'
    for idx, row in df_breath[df_breath['Comment'] == 'ERROR'].iterrows():
        sid = row['StaffID']
        match = df_evac.loc[df_evac['EmployeeID'] == sid, 'Name']
        if not match.empty:
            df_breath.at[idx, 'Name'] = match.iloc[0]
            df_breath.at[idx, 'Comment'] = 'OK'
    invalid_mask = df_breath['OriginalName'] == 'Invalid Staff ID'
    for idx in df_breath[invalid_mask].index:
        sid = df_breath.at[idx, 'StaffID']
        match = df_evac.loc[df_evac['EmployeeID'] == sid, 'Name']
        if not match.empty:
            df_breath.at[idx, 'Name'] = match.iloc[0]

    # Объединение таблиц
    merged_df = pd.merge(
        df_evac[['Name', 'Organisation', 'Supervisor', 'Workgroup', 'WorkStatus', 'EmployeeID']],
        df_breath[['Name', 'Result', 'OriginalName', 'StaffID', 'Date', 'Time', 'Comment']],
        how='outer', on='Name'
    )

    # Приведение ID к строкам для первоначальной фазы
    for col in ['EmployeeID', 'StaffID']:
        merged_df[col] = merged_df[col].fillna('').astype(str)

    # Преобразование времени
    merged_df['Time'] = pd.to_datetime(merged_df['Time'], format='%H:%M:%S', errors='coerce')
    # Преобразование в строку времени
    merged_df['Time'] = merged_df['Time'].dt.strftime('%H:%M:%S').fillna('')

    # Разбор и форматирование даты: оставить только день-месяц-год
    merged_df['Date'] = pd.to_datetime(merged_df['Date'], dayfirst=True, errors='coerce')
    merged_df['Date'] = merged_df['Date'].dt.strftime('%d-%m-%Y').fillna('')

    # Объединение в текстовый столбец
    merged_df['DateTime'] = merged_df['Date'] + ' ' + merged_df['Time']
    # Замена случаев, где дата или время пустые
    merged_df['DateTime'] = merged_df['DateTime'].replace('  ', '').replace('', '')

    # Отбор последних записей: отдельно для непустых StaffID, оставляем все пустые
    nonempty = merged_df[merged_df['StaffID'] != '']
    empty = merged_df[merged_df['StaffID'] == '']
    nonempty = nonempty.sort_values(['StaffID', 'Date']).drop_duplicates(subset=['StaffID'], keep='last')
    merged_df = pd.concat([nonempty, empty], ignore_index=True)

    # Снова очищаем ID, чтобы избежать literal 'nan'
    for col in ['EmployeeID', 'StaffID']:
        merged_df[col] = merged_df[col].fillna('').astype(str).replace('nan', '')

    # Вычисление статуса: сначала по Result, потом по ошибкам ID
    merged_df['Status'] = 'NOT SET'
    merged_df['Result'] = pd.to_numeric(merged_df['Result'].astype(str).str[:6], errors='coerce')
    merged_df.loc[merged_df['Result'] > 0, 'Status'] = 'DENIED'
    merged_df.loc[merged_df['Result'] == 0, 'Status'] = 'ALLOWED'
    merged_df.loc[merged_df['OriginalName'] == 'Invalid Staff ID', 'Status'] = 'NOT FOUND'
    merged_df.loc[merged_df['Comment'] == 'ERROR', 'Status'] = 'NOT FOUND'

    # Окончательная сортировка для отображения
    order = {'DENIED': 1, 'NOT FOUND': 2, 'ALLOWED': 3, 'NOT SET': 4}
    merged_df['StatusOrder'] = merged_df['Status'].map(order)
    merged_df = merged_df.sort_values(['StatusOrder', 'WorkStatus', 'Name'])
    merged_df = merged_df.drop(columns=['StatusOrder'])

    return merged_df


def validate_xls(username):
    user_media_dir = os.path.join(MEDIA_ROOT, username)
    evac_path = os.path.join(user_media_dir, 'evac.xlsx')
    breath_path = os.path.join(user_media_dir, 'breath.xlsx')

    if not os.path.exists(evac_path) or not os.path.exists(breath_path):
        return False

    df_evac = pd.read_excel(evac_path)
    required_columns = {'Name', 'EmployeeID', 'Work Status'}

    if not required_columns.issubset(df_evac.columns):
        return False

    df_breath = pd.read_excel(breath_path)
    required_columns = {'Staff Name', 'Staff ID', 'Result'}

    if not required_columns.issubset(df_breath.columns):
        return False

    return True


def check_data_for_errors(df):
    errors_list = []
    filtered1_df = df[df['EmployeeID'] != '']
    filtered2_df = df[df['Name'] != '']

    # Найти дубликаты EmployeeID
    duplicates = filtered1_df[filtered1_df.duplicated(subset=['EmployeeID'], keep=False)]

    # Сгруппировать дублирующиеся значения EmployeeID и собрать их в список
    duplicates_list = duplicates.groupby('EmployeeID')['EmployeeID'].apply(list).tolist()
    if duplicates_list:
        errors_list.append(f"Duplicated IDs in evacuate.xlsx ({', '.join(map(str, duplicates_list))})")

    # Проверить, есть ли дубликаты в столбце 'Name', игнорируя пустые строки
    if filtered2_df.duplicated(subset=['Name']).any():
        errors_list.append('Duplicated Names in merged table')

    return errors_list


def counters(df):
    total_rows = len(df.index)
    status_denied = len(df[df['Status'] == 'DENIED'])
    status_allowed = len(df[df['Status'] == 'ALLOWED'])
    status_not_found = len(df[df['Status'] == 'NOT FOUND'])
    status_not_set = len(df[df['Status'] == 'NOT SET'])
    empty_id = (df['EmployeeID'] == '').sum()

    count_dict = {
        "Staff with <span style='color: green;'>ALLOWED</span> status": status_allowed,
        "Staff with <span style='color: red;'>DENIED</span> status": status_denied,
        "Staff who were <span style='color: orange;'>NOT FOUND</span> on the Evacuation list": status_not_found,
        "Staff in Evacuation list but not in Breath analyzer report": status_not_set,
        "Rows with empty Employee ID": empty_id,
        "<span style='font-weight: bold;'>Total rows:</span>": f"<span style='font-weight: bold;'>{total_rows}</span>",
    }

    row_dict = {
        "ALLOWED": status_allowed,
        "DENIED": status_denied,
        "NOT FOUND": status_not_found,
        "NOT SET": status_not_set,
        "EMPTY ID": empty_id,
    }

    for key, value in row_dict.items():
        row_dict[key] = int(value)

    # --- НОВАЯ ЧАСТЬ: считаем уникальные значения WorkStatus ---
    # Убедимся, что колонка существует; если нет — вернём пустой словарь
    work_status_dict = {}

    if 'WorkStatus' in df.columns:
        # Заменяем NaN на пустую строку и приводим к str, затем считаем
        work_status_series = df['WorkStatus'].fillna('').astype(str)
        # Если хотите считать пустые как отдельную категорию, раскомментируйте следующую строку:
        # work_status_series = work_status_series.replace('', 'UNKNOWN')
        counts = work_status_series.value_counts(dropna=False).to_dict()
        # Приведём все подсчёты к int и уберём ключ '' если не нужен
        work_status_dict = {str(k): int(v) for k, v in counts.items()}
        # Опционально: переименовать пустую строку в более читаемый label
        if '' in work_status_dict:
            work_status_dict['(empty)'] = work_status_dict.pop('')

    return count_dict, row_dict, work_status_dict

