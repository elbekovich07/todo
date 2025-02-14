from service import (
    logout, login, register, todo_add, set_admin, create_todo, get_todos, update_todo, delete_todo
)
from utils import Response
from Session import Session


def login_page():
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    response = login(username, password)
    print(response.message)


def register_page():
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    response = register(username, password)
    print(response.message)


def logout_page():
    response = logout()
    print(response.message)


def create_todo():
    title = input("Enter your title: ")
    response = todo_add(title)
    print(response.message)

def set_admin_user():
    username = input("Enter your username: ")
    response = set_admin(username)
    print(response.message)


def create_todo_page():
    title = input("Enter task title: ")
    description = input("Enter description (optional): ")
    todo_type = input("Enter priority (low, medium, high): ")

    response = create_todo(title, description, todo_type)
    print(response.message)


def view_todos_page():
    response = get_todos()

    if response.status_code == 404:
        print("No todos found.")
        return

    for todo in response.data:
        print(f"[{todo[0]}] {todo[1]} - {todo[2]} ({todo[3]})")


def update_todo_page():
    todo_id = int(input("Enter task ID to update: "))
    title = input("Enter new title (leave empty to skip): ")
    description = input("Enter new description (leave empty to skip): ")
    todo_type = input("Enter new priority (low, medium, high, leave empty to skip): ")

    response = update_todo(todo_id, title if title else None, description if description else None, todo_type if todo_type else None)
    print(response.message)

def delete_todo_page():
    todo_id = int(input("Enter task ID to delete: "))
    response = delete_todo(todo_id)
    print(response.message)







def menu():
    print('Login       => 1')
    print('Register    => 2')
    print('Logout      => 3')
    print('Create Task => 4')
    print('View Tasks  => 5')
    print('Update Task => 6')
    print('Delete Task => 7')
    print('Set Admin   => 8')
    print('Exit        => q')
    return input('Enter your choice: ')



def run():
    while True:
        choice = menu()
        if choice == '1':
            login_page()
        elif choice == '2':
            register_page()
        elif choice == '3':
            logout_page()
        elif choice == '4':
            create_todo_page()
        elif choice == '5':
            view_todos_page()
        elif choice == '6':
            update_todo_page()
        elif choice == '7':
            delete_todo_page()
        elif choice == '8':
            set_admin_user()
        elif choice == 'q':
            return
        else:
            print("Invalid choice")


if __name__ == "__main__":
    run()