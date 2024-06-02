import psycopg2
import os
from dotenv import load_dotenv
import utils

load_dotenv()

conn = psycopg2.connect(database=os.getenv('database'),
                        user=os.getenv('user'),
                        password=os.getenv('password'),
                        host=os.getenv('host'),
                        port=os.getenv('port')
                        )

cur = conn.cursor()

create_users_table = """create table if not exists users(
    id serial primary key ,
    username varchar(100) not null unique ,
    password varchar(255) not null ,
    role varchar(20) not null ,
    status varchar(30) not null ,
    login_try_count int not null
);
"""

create_todos_table = """create table if not exists todos(
    id serial PRIMARY KEY,
    title varchar(100) not null ,
    todo_type varchar(15) not null,
    user_id int references users(id)
);
"""


def commit(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        conn.commit()
        return result

    return wrapper


def create_table():
    cur.execute(create_users_table)
    cur.execute(create_todos_table)
    conn.commit()


@commit
def migrate():
    insert_into_users = """
    insert into users (username, password, role, status,login_try_count)
    values (%s, %s, %s, %s, %s);

    """
    cur.execute(insert_into_users, ('admin', utils.hash_password('123'), 'SUPERADMIN', 'ACTIVE', 0))


def init():
    create_table()
    migrate()


if __name__ == '__main__':
    init()