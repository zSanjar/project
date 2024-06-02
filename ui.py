from service import session
from utils import ResponseData, BadRequest
import service
from typing import Union
import dao
from colorama import Fore
from models import UserRole
from dto import UserRegisterDTO


# Utility function to print response with color
def print_response(response: Union[ResponseData, BadRequest]):
    color = Fore.GREEN if response.status_code == 200 else Fore.RED
    print(color + response.data + Fore.RESET)


# Utility function to get user input with color
def get_input(prompt: str) -> str:
    return input(Fore.LIGHTCYAN_EX + prompt + Fore.RESET)


# Function to handle user login
def login():
    username = input('Enter your username: ')
    password = input('Enter your password: ')
    response = service.login(username, password)
    print_response(response)
    return response


# Function to handle user registration
def register():
    username = input('Enter your username: ')
    password = input('Enter your password: ')
    dto: UserRegisterDTO = UserRegisterDTO(username, password)
    response = service.register(dto)
    print_response(response)
    return response


# Function to handle user logout
def logout():
    print_response(service.logout())


# Function to add a todo item
def todo_add():
    title = input('Enter title : ')
    todo_type = dao.choose_todo_type()
    response = dao.todo_add(title, todo_type)
    print_response(response)


# Function to show todo items
def show_todos():
    dao.show_todos()


# Function to update a todo item
def update_todo():
    todo_id_to_update = input('Enter todo_id to update: ')
    title = input('Enter title : ')
    todo_type = dao.choose_todo_type()
    response = dao.update_todo(todo_id_to_update, title, todo_type)
    print_response(response)


# Function to delete a todo item
def delete_todo():
    todo_id_to_delete = input('Enter todo_id to delete: ')
    response = dao.delete_todo(todo_id_to_delete)
    print_response(response)


# Function to block a user (only for super admin)
def block_user():
    _id = input('Enter id to block: ')
    response = service.block_user(_id)
    print_response(response)


# Function to display the menu for regular users
def user_menu() -> str:
    return get_input(Fore.LIGHTWHITE_EX + """Please choose option which you want:
1. Create todo
2. Show todos
3. Update todo
4. Delete todo
0. LogOut\n ....""" + Fore.RESET)


# Function to display the menu for super admins
def super_admin_menu() -> str:
    return get_input(Fore.LIGHTWHITE_EX + """Please choose option which you want:
1. Create todo
2. Show todos
3. Update todo
4. Delete todo
5. Block user
0. LogOut\n....""" + Fore.RESET)


# Function to dispatch menu choices
def menu_dispatch(choice: str, is_superadmin: bool):
    options = {
        '1': todo_add,
        '2': show_todos,
        '3': update_todo,
        '4': delete_todo,
        '0': logout
    }

    if is_superadmin:
        options['5'] = block_user

    if choice in options:
        options[choice]()
    else:
        print_response(BadRequest('Invalid option'))


# Function to handle the menu based on user role
def run_choice(is_superadmin: bool):
    menu = super_admin_menu if is_superadmin else user_menu
    while True:
        choice = menu()
        if choice == '0':
            logout()
            break
        menu_dispatch(choice, is_superadmin)


# Main function to run the program
def run() -> None:
    while True:
        if not session.check_session():
            choice = input(Fore.LIGHTCYAN_EX + "Welcome to our website.\n1."
                                               " Register\n2. Login. \n0. Exit\n.... " + Fore.RESET)
            if choice == '1':
                register_result = register()
                if isinstance(register_result, BadRequest):
                    pass
                else:
                    run_choice(False)
            elif choice == '2':
                login_result = login()
                if isinstance(login_result, ResponseData):
                    run_choice(session.get_user_role() == UserRole.SUPERADMIN.value)
            elif choice == '0':
                print_response(ResponseData("Thank you for using"))
                break
            else:
                print_response(BadRequest('Invalid option'))


if __name__ == '__main__':
    run()