import psycopg2
import sys
import utils
from service import session
from db import cur, conn, commit
from models import Todo, TodoType
from service import login
from colorama import Fore
from typing import Dict


def choose_todo_type() -> TodoType:
    todo_type_dict: Dict[str, TodoType] = {'3': TodoType.Optional.value, '1': TodoType.Personal.value,
                                           '2': TodoType.Shopping.value, }  # dict of todo types
    choice_todo_type: str = input(Fore.LIGHTWHITE_EX + "Enter your todo type:"
                                                       "\n1 - Personal\n2 - Shopping\n"
                                                       "3 - Optional\n...."
                                  + Fore.RESET)
    todo_type: TodoType = todo_type_dict.get(choice_todo_type)
    return todo_type


@utils.login_required
@commit
def todo_add(title: str, todo_type: TodoType):
    try:
        insert_query = """insert into todos(title,todo_type,user_id)
            values (%s,%s,%s);
            """
        data = (title, todo_type, session.session.id)

        cur.execute(insert_query, data)
        return utils.ResponseData('INSERTED TODO')
    except psycopg2.Error as e:
        conn.rollback()
        return utils.BadRequest('Error', str(e))


@utils.login_required
@commit
def delete_todo(todo_id_to_delete: str) -> utils:
    # todo_id_to_delete: str = input(Fore.LIGHTWHITE_EX + "Please enter todo id to delete: " + Fore.RESET)
    if todo_id_to_delete:
        try:
            cur.execute("""DELETE FROM todos WHERE id=%s""", (todo_id_to_delete,))
            return utils.ResponseData('Todo Deleted')
        except psycopg2.Error as e:
            conn.rollback()
            return utils.BadRequest('Error', str(e))


@utils.login_required
@commit
def update_todo(todo_id_to_update, title, todo_type: TodoType) -> utils:
    # todo_id_to_update: str = input(Fore.LIGHTWHITE_EX + "Please enter todo id to update: " + Fore.RESET)
    if todo_id_to_update:
        try:
            cur.execute("""SELECT * FROM todos where id = %s""", (todo_id_to_update,))
            todo_data: tuple = cur.fetchone()
            if not todo_data:
                return utils.BadRequest('Todo Not Found')
            else:
                # title: str = input(Fore.LIGHTWHITE_EX + "Enter your todo title: " + Fore.RESET)
                # todo_type: TodoType = choose_todo_type()
                todo: Todo = Todo(title, session.session.id, todo_type)
                cur.execute("UPDATE todos SET title = %s, todo_type = %s, user_id = %s WHERE id = %s",
                            (todo.title, todo.todo_type, todo.user_id, todo_id_to_update))
                return utils.ResponseData('Todo Updated')
        except psycopg2.Error as e:
            conn.rollback()
            return utils.BadRequest('Error', str(e))
    else:
        return utils.BadRequest('Todo Not Found')


@utils.login_required
def show_todos() -> utils:
    try:
        cur.execute("""SELECT * FROM todos where user_id = %s""", (session.session.id,))
        user_todo_data: tuple = cur.fetchall()
        if not user_todo_data:
            print("You don't have any todo yet😒")
        else:
            list(map(print, user_todo_data))
    except psycopg2.Error as e:
        conn.rollback()
        return utils.BadRequest('Error', str(e))