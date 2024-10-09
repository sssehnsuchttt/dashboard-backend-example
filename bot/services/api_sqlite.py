import sqlite3
from bot.data.config import PATH_DATABASE, admin_id, admin_language
from bot.utils.const_functions import get_date, do_round
from datetime import datetime
import json



def add_format(sql, parameters: dict):
    sql = f"{sql} ("
    sql += ", ".join(parameters) + ") VALUES("
    sql += ", ".join(["?" for item in parameters]) + ")"
    return sql, list(parameters.values())

tables = [
    ("items", [
        "itemid INTEGER PRIMARY KEY AUTOINCREMENT",
        "name TEXT",
        "description TEXT",
        "price INT",
        "data TEXT"
    ]),
    ("faq", [
        "description TEXT"
    ]),
    ("buyers", [
        "userid TEXT",
        "itemid TEXT",
        "comment TEXT",
        "amount TEXT",
        "data TEXT"
    ]),
    ("userlist", [
        "userid INTEGER",
        "referid INTEGER",
        "date TEXT",
        "lang TEXT",
        "lang_code TEXT"
    ]),
    ("stats", [
        "users INTEGER",
        "users_month INTEGER",
        "users_day INTEGER",
        "buyers INTEGER",
        "buyers_month INTEGER",
        "buyers_day INTEGER",
        "profit INTEGER",
        "profit_month INTEGER",
        "profit_day INTEGER",
        "startup_data TEXT",
        "last_update_data TEXT"
    ]),
    ("user_purchases", [
        "userid INTEGER",
        "itemid TEXT"
    ]),
    ("settings", [
        "is_working INT",
        "support TEXT",
        "website TEXT"
    ]),
    ("profit_month_stats", [
        "date TEXT",
        "amount INTEGER"
    ]),
    ("traffic_month_stats", [
        "date TEXT",
        "amount INTEGER"
    ]),
    ("bills", [
        "paymentid INTEGER",
        "userid INTEGER",
        "itemid INTEGER",
        "amount INTEGER",
        "currency TEXT",
        "props INTEGER",
        "lifespan TEXT",
        "msgid INTEGER",
        "link TEXT"
    ]),
    ("payouts_history", [
        "payoutid INTEGER",
        "amount TEXT",
        "amount_orig TEXT",
        "commission_type INTEGER",
        "props TEXT",
        "method TEXT",
        "method_str TEXT",
        "bank TEXT",
        "userid INTEGER",
        "status INTEGER",
        "status_str TEXT",
        "date TEXT"
    ])
]

def create_db():
    with sqlite3.connect(PATH_DATABASE, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES) as con:
        cur = con.cursor()
        for table_name, columns in tables:
            try:
                cur.execute(f"SELECT 1 FROM {table_name} LIMIT 1")
                print(f"DB {table_name} was found")
            except sqlite3.OperationalError:
                print(f"DB {table_name} was not found")
                cur.execute(f"CREATE TABLE {table_name}({', '.join(columns)})")
                print(f"DB {table_name} was created")
            
            cur.execute(f"PRAGMA table_info({table_name})")
            existing_columns = [column[1] for column in cur.fetchall()]
            
            for column in columns:
                column_name = column.split()[0]
                if column_name not in existing_columns:
                    print(f"Adding column {column_name} to table {table_name}")
                    cur.execute(f"ALTER TABLE {table_name} ADD COLUMN {column}")
            
            for existing_column in existing_columns:
                if existing_column not in [column.split()[0] for column in columns]:
                    print(f"Removing column {existing_column} from table {table_name}")
                    cur.execute(f"CREATE TABLE temp_{table_name} AS SELECT {', '.join([col for col in existing_columns if col != existing_column])} FROM {table_name}")
                    cur.execute(f"DROP TABLE {table_name}")
                    cur.execute(f"ALTER TABLE temp_{table_name} RENAME TO {table_name}")

def dict_factory(cursor, row):
    save_dict = {}

    for idx, col in enumerate(cursor.description):
        save_dict[col[0]] = row[idx]

    return save_dict

def update_format(sql, parameters: dict):
    if "XXX" not in sql: sql += " XXX "

    values = ", ".join([
        f"{item} = ?" for item in parameters
    ])
    sql = sql.replace("XXX", values)

    return sql, list(parameters.values())

def update_format_args(sql, parameters: dict):
    sql = f"{sql} WHERE "

    sql += " AND ".join([
        f"{item} = ?" for item in parameters
    ])

    return sql, list(parameters.values())

def get_all_tables(db_path=PATH_DATABASE):
    with sqlite3.connect(db_path) as con:
        cursor = con.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        return [table[0] for table in tables]

def get_table(table, db_path=PATH_DATABASE):
    with sqlite3.connect(db_path) as con:
        cursor = con.cursor()

        # Получение структуры таблицы
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        column_headers = []
        for column in columns:
            column_name = column[1]
            column_type = column[2]
            editable = True
            if column[5] == 1:
                editable = False
            column_headers.append({"column": column_name, "editable": editable})

        # Получение данных из таблицы
        cursor.execute(f"SELECT * FROM {table}")
        data = cursor.fetchall()

        # Формирование результата
        result = {"columns": column_headers, "data": data}
        return result
    
def add_new_row(table, db_path=PATH_DATABASE):
    with sqlite3.connect(db_path) as con:
        cursor = con.cursor()
        cursor.execute(f"INSERT INTO {table} DEFAULT VALUES")
        last_row_id = cursor.lastrowid
        cursor.execute(f"SELECT * FROM {table} WHERE rowid=?", (last_row_id,))
        row = cursor.fetchone()
        return row
    
def update_table(data, db_path=PATH_DATABASE):
    with sqlite3.connect(db_path) as con:
        cursor = con.cursor()
        
        # Очищаем таблицу перед перезаписью
        cursor.execute(f"DELETE FROM {data['table']}")
        
        # Вставляем новые данные в таблицу
        columns = data['data']['columns']
        column_names = [column['column'] for column in columns]
        placeholders = ','.join('?' for _ in column_names)
        query = f"INSERT INTO {data['table']} ({','.join(column_names)}) VALUES ({placeholders})"
        
        rows = data['data']['data']
        cursor.executemany(query, rows)
        
        con.commit()
        
def fetch_data(table: str, fetch: str = "fetchall", db_path=PATH_DATABASE, **kwargs):
    with sqlite3.connect(db_path) as con:
        con.row_factory = dict_factory
        sql = f"SELECT * FROM {table}"
        if kwargs:
            sql, parameters = update_format_args(sql, kwargs)
            if fetch == "fetchall":
                result = con.execute(sql, parameters).fetchall()
            else:
                result = con.execute(sql, parameters).fetchone()
        else:
            if fetch == "fetchall":
                result = con.execute(sql).fetchall()
            else:
                result = con.execute(sql).fetchone()
        return result


def add_data(table: str, db_path=PATH_DATABASE, **kwargs):
    with sqlite3.connect(db_path) as con:
        sql = f"INSERT INTO {table}"
        sql, parameters = add_format(sql, kwargs)
        con.execute(sql, parameters)
        con.commit()


def update_data(table: str, update: dict, search: dict = None, db_path=PATH_DATABASE):
    with sqlite3.connect(db_path) as con:
        sql = f"UPDATE {table} SET "
        if search:
            sql += ", ".join([f"{item} = ?" for item in update])
            sql, parameters = update_format_args(sql, search)
            parameters = list(update.values()) + parameters
    
            cursor = con.cursor()
            cursor.execute(sql, parameters)
            rows_affected = cursor.rowcount
            con.commit()
            return rows_affected
        else:
            if fetch_data(table, db_path=db_path) == []:
                sql = f"INSERT INTO {table}"
                sql, parameters = add_format(sql, update)
            else:
                sql, parameters = update_format(sql, update)
            con.execute(sql, parameters)
            con.commit()
            return 1


def delete_data(table: str, db_path=PATH_DATABASE, **kwargs):
    with sqlite3.connect(db_path) as con:
        sql = f"DELETE FROM {table}"
  
        if kwargs:
            sql, parameters = update_format_args(sql, kwargs)
        else:
            parameters = []
        
        cursor = con.cursor()
        cursor.execute(sql, parameters)
        rows_affected = cursor.rowcount
        con.commit()
        return rows_affected
