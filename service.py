from Session import Session
from migration.db import cur, commit
from models import User, Todo
from utils import Response, match_password
from functools import wraps


Session = Session()


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user = Session.check_session()
        if not user:
            return Response(message="User not authenticated", status_code=401)
        return func(*args, **kwargs)
    return wrapper


@commit
def login(username: str, password: str) -> Response:
    user: User | None = Session.check_session()
    if user is not None:
        return Response(message='You already logged in', status_code=401)
    get_user_by_username_query = '''select * from users where username = %s;'''
    cur.execute(get_user_by_username_query, (username,))
    user_data = cur.fetchone()
    if user_data is None:
        return Response(message='Invalid username or password', status_code=401)
    user = User.from_tuple(user_data)
    if not match_password(password, user.password):
        update_user_query = '''update users set login_try_count = login_try_count + 1 where username = %s;'''
        cur.execute(update_user_query, (username,))
        return Response('Invalid username or password', status_code=401)
    Session.add_session(user)
    return Response('Login successful', status_code=200)


@commit
def register(username, password):
    get_user_by_username = '''select * from users where username = %s;'''
    cur.execute(get_user_by_username, (username,))
    user_data = cur.fetchone()
    if user_data is not None:
        return Response(message=f'This {username} already exists', status_code=400)

    user = User(username=username, password=password)
    user.save()
    return Response('User successfully created', status_code=201)

@commit
def logout():
    session = Session._instance if Session._instance else Session()
    if session.check_session():
        session.remove_session()
        return Response(message="Logged out successfully!", status_code=200)
    return Response(message="You must login first", status_code=401)


@commit
@login_required
def todo_add(title: str):
    user = Session._instance.check_session()

    if not user:
        return Response(message='User not authenticated', status_code=401)

    if user.role != 'admin':
        return Response(message='Adding todo must be an admin', status_code=403)

    todo = Todo(title=title, user_id=user.id)
    todo.save()
    return Response(message='Todo added', status_code=201)


@commit
@login_required
def set_admin(username: str):
    user: User = Session.check_session()
    if not user or user.role != 'admin':
        return Response(message='Only admins can assign admin roles', status_code=403)

    get_user_query = '''SELECT * FROM users WHERE username = %s;'''
    cur.execute(get_user_query, (username,))
    user_data = cur.fetchone()

    if user_data is None:
        return Response(message='User not found', status_code=404)

    update_role_query = '''UPDATE users SET role = 'admin' WHERE username = %s;'''
    cur.execute(update_role_query, (username,))

    return Response(message=f'{username} is now an admin', status_code=200)


@commit
@login_required
def create_todo(title: str, description: str = "", todo_type: str = "low"):
    user = Session.check_session()

    if not user:
        return Response(message="User not authenticated", status_code=401)

    insert_query = '''INSERT INTO todos (title, description, todo_type, user_id)
                      VALUES (%s, %s, %s, %s);'''
    cur.execute(insert_query, (title, description, todo_type, user.id))

    return Response(message="Todo successfully created", status_code=201)


@login_required
def get_todos():
    user = Session.check_session()

    if not user:
        return Response(message="User not authenticated", status_code=401)

    select_query = '''SELECT id, title, description, todo_type, created_at FROM todos WHERE user_id = %s;'''
    cur.execute(select_query, (user.id,))
    todos = cur.fetchall()

    if not todos:
        return Response(message="No todos found", status_code=404)

    return Response(message="Todos fetched successfully", status_code=200, data=todos)



@commit
@login_required
def update_todo(todo_id: int, title: str = None, description: str = None, todo_type: str = None):
    user = Session.check_session()

    if not user:
        return Response(message="User not authenticated", status_code=401)

    update_query = "UPDATE todos SET"
    update_fields = []
    values = []

    if title:
        update_fields.append(" title = %s")
        values.append(title)
    if description:
        update_fields.append(" description = %s")
        values.append(description)
    if todo_type:
        update_fields.append(" todo_type = %s")
        values.append(todo_type)

    if not update_fields:
        return Response(message="Nothing to update", status_code=400)

    update_query += ",".join(update_fields) + " WHERE id = %s AND user_id = %s;"
    values.append(todo_id)
    values.append(user.id)

    cur.execute(update_query, tuple(values))

    return Response(message="Todo successfully updated", status_code=200)



@commit
@login_required
def delete_todo(todo_id: int):
    user = Session.check_session()

    if not user:
        return Response(message="User not authenticated", status_code=401)

    delete_query = '''DELETE FROM todos WHERE id = %s AND user_id = %s;'''
    cur.execute(delete_query, (todo_id, user.id))

    return Response(message="Todo successfully deleted", status_code=200)