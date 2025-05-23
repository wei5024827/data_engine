import pymysql

def get_db_connection(config):
    return pymysql.connect(
        host=config['db_host'],
        user=config['db_user'],
        password=config['db_password'],
        db=config['db_name'],
        port=config.get('db_port', 3306),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

def fetch_download_patterns(config):
    conn = get_db_connection(config)
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT File_name FROM t_download_config WHERE status = '1'")
            return [row['File_name'] for row in cursor.fetchall()]
    finally:
        conn.close()

def record_download_result(config, data_date, owner, table_name, status, finish_time):
    conn = get_db_connection(config)
    try:
        with conn.cursor() as cursor:
            sql = '''
                INSERT INTO t_ftp_download_result
                (Data, Owner, Table_name, status, finish_time)
                VALUES (%s, %s, %s, %s, %s)
            '''
            cursor.execute(sql, (data_date, owner, table_name, status, finish_time))
        conn.commit()
    finally:
        conn.close()
