import os
import logging
from db import get_db_connection

DELIMITER = '!|'

def parse_script(script_path):
    with open(script_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]

    if not lines or not lines[0].lower().startswith('insert into'):
        raise ValueError("Invalid script format")

    target_table = lines[0].split()[2]
    field_line_idx = 1
    while not lines[field_line_idx].lower().startswith('select'):
        field_line_idx += 1

    insert_fields = [field.strip(',') for field in lines[1:field_line_idx]]
    select_fields = [val.strip(',') for val in lines[field_line_idx+1:-1]]

    return target_table, insert_fields, select_fields

def load_data_file(data_file_path):
    with open(data_file_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]

    headers = lines[0].split(DELIMITER)
    data_rows = [line.split(DELIMITER) for line in lines[1:]]
    return headers, data_rows

def map_fields_to_values(headers, rows, select_fields):
    mapped_data = []
    for row in rows:
        val_map = {f"Val[{i+1}]": row[i] for i in range(len(headers))}
        try:
            mapped_row = [val_map[field] for field in select_fields]
        except KeyError as e:
            raise ValueError(f"Field {e} not found in row mapping")
        mapped_data.append(mapped_row)
    return mapped_data

def insert_data(config, table, fields, data):
    conn = get_db_connection(config)
    try:
        with conn.cursor() as cursor:
            placeholders = ', '.join(['%s'] * len(fields))
            sql = f"INSERT INTO {table} ({', '.join(fields)}) VALUES ({placeholders})"
            cursor.executemany(sql, data)
        conn.commit()
        logging.info(f"Inserted {len(data)} rows into {table}")
    except Exception as e:
        logging.error(f"Insert failed for table {table}: {e}")
        raise
    finally:
        conn.close()

def load_and_insert(config, script_path, data_dir):
    try:
        base_filename = os.path.splitext(os.path.basename(script_path))[0]
        data_file_path = os.path.join(data_dir, base_filename)

        table, insert_fields, select_fields = parse_script(script_path)
        headers, rows = load_data_file(data_file_path)
        data = map_fields_to_values(headers, rows, select_fields)
        insert_data(config, table, insert_fields, data)

    except Exception as e:
        logging.error(f"Failed to load {script_path}: {e}")
