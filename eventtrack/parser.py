import os
from .settings import MEDIA_ROOT
import pandas as pd

pd.set_option('display.max_columns', 10)


def get_workers_list(username):
    # load data
    user_media_dir = os.path.join(MEDIA_ROOT, username)

    evac_path = os.path.join(user_media_dir, 'evac.xlsx')
    breath_path = os.path.join(user_media_dir, 'breath.xlsx')

    df_evac = pd.read_excel(evac_path)
    df_breath = pd.read_excel(breath_path)

    df_breath['Name'] = df_breath['Staff Name'].apply(lambda x: x.replace(' ', ', ', 1) if isinstance(x, str) and x != 'Invalid Staff ID' else x)
    df_evac['EmployeeID'] = pd.to_numeric(df_evac['EmployeeID'], errors='coerce')
    df_breath['Staff ID'] = pd.to_numeric(df_breath['Staff ID'], errors='coerce')

    df_breath['Time'] = pd.to_datetime(df_breath['Time'], format='%H:%M:%S')
    max_times = df_breath.groupby(['Staff ID', 'Name'], as_index=False)['Time'].max()
    df_breath = pd.merge(df_breath, max_times, on=['Staff ID', 'Name', 'Time'], how='inner')

    df_breath = df_breath.rename(columns={'Staff ID': 'StaffID'})
    df_evac = df_evac.rename(columns={'Work Status': 'WorkStatus'})

    # mark 'Name' df_breath who not in evac list
    mask = ~df_breath['Name'].isin(df_evac['Name'])
    df_breath.loc[mask, 'Comment'] = 'ERROR'

    # check correlations with evac list
    for index, row in df_breath.iterrows():
        if row['Comment'] == 'ERROR':
            staff_id = row['StaffID']
            employee_id = df_evac[df_evac['EmployeeID'] == staff_id]['Name'].values
            if len(employee_id) > 0:
                df_breath.at[index, 'Name'] = employee_id[0]
                df_breath.at[index, 'Comment'] = 'OK'

    # Select rows where 'Staff Name' is 'Invalid Staff ID'
    error_rows = df_breath[df_breath['Staff Name'] == 'Invalid Staff ID']

    # Сравнение значений столбца 'id' с 'id' в df_evac
    for index, row in error_rows.iterrows():
        if row['StaffID'] in df_evac['EmployeeID'].values:
            df_breath.at[index, 'Name'] = df_evac[df_evac['EmployeeID'] == row['StaffID']]['Name'].iloc[0]

    # Объединение данных на основе столбца "Name"
    merged_df = pd.merge(df_evac[['Name', 'Organisation', 'Supervisor', 'Workgroup', 'WorkStatus', 'EmployeeID']],
                         df_breath[['Name', 'Result', 'Staff Name', 'StaffID', 'Date', 'Comment']],
                         how='outer',
                         on='Name')

    merged_df['EmployeeID'] = merged_df['EmployeeID'].fillna('').apply(lambda x: '{:.0f}'.format(x) if x != '' else '')
    merged_df['StaffID'] = merged_df['StaffID'].fillna('').apply(lambda x: '{:.0f}'.format(x) if x != '' else '')

    # Отбор строк, где EmployeeID не уникален и не является пустым значением
    duplicate_employee_ids = merged_df.duplicated(subset=['EmployeeID'], keep=False) & merged_df['EmployeeID'].notna()

    # Замена значений EmployeeID на StaffID, если StaffID не является пустым значением
    merged_df.loc[duplicate_employee_ids, 'EmployeeID'] = merged_df.loc[duplicate_employee_ids, 'StaffID']


    # add "Status" by default
    merged_df['Status'] = 'NOT SET'

    # check analyzer data: to text, then first 6 symbols, then to int
    merged_df['Result'] = merged_df['Result'].astype(str)
    merged_df['Result'] = merged_df['Result'].str[:6]
    merged_df['Result'] = pd.to_numeric(merged_df['Result'], errors='coerce')

    # set status code depends on "Result"
    merged_df.loc[merged_df['Result'] > 0, 'Status'] = 'DENIED'
    merged_df.loc[merged_df['Result'] == 0, 'Status'] = 'ALLOWED'
    merged_df.loc[merged_df['Staff Name'] == 'Invalid Staff ID', 'Status'] = 'NOT FOUND'
    merged_df.loc[merged_df['Comment'] == 'ERROR', 'Status'] = 'NOT FOUND'
    merged_df.loc[merged_df['Comment'] == 'OK', 'Status'] = 'ALLOWED'

    status_order = {'DENIED': 1, 'NOT FOUND': 2, 'ALLOWED': 3, 'NOT SET': 4}
    merged_df['Status'] = merged_df['Status'].map(status_order)
    merged_df = merged_df.sort_values(by=['Status', 'WorkStatus', 'Name'])
    merged_df['Status'] = merged_df['Status'].replace({v: k for k, v in status_order.items()})
    # merged_df = merged_df.sort_values(by=['Status'], key=lambda x: x.map(status_order))

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

    return count_dict, row_dict

