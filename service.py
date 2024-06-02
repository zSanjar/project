import utils
from typing import Union
from dto import UserRegisterDTO
from db import cur, conn
from models import User, UserRole, UserStatus, TodoType
from sessions import Session

from validators import check_validators

session: Session = Session()


def get_data(parameter: str, input_atr: str | int) -> tuple:
    cur.execute(f"""SELECT * FROM users where {parameter} = %s """, (input_atr,))
    return cur.fetchone()


def login(username: str, password: str) -> Union[utils.BadRequest, utils.ResponseData]:
    user: User | None = session.check_session()
    if user:
        return utils.BadRequest('You already logged in', status_code=401)

    get_user_by_username = '''select * from users where username = %s;'''
    cur.execute(get_user_by_username, (username,))
    user_data = cur.fetchone()
    if not user_data:
        return utils.BadRequest('Bad credentials', status_code=401)
    user = User.from_tuple(user_data)
    if user.login_try_count >= 3:
        return utils.BadRequest('User is blocked')
    if not utils.check_password(password, user.password):
        update_count_query = """update users set login_try_count = login_try_count + 1 where username = %s;"""
        cur.execute(update_count_query, (user.username,))
        conn.commit()
        return utils.BadRequest('Bad credentials', status_code=401)

    session.add_session(user)
    return utils.ResponseData('User Successfully Logged in')


def register(dto: UserRegisterDTO):
    try:
        check_validators(dto)
        user_data = '''select * from users where username = %s;'''
        cur.execute(user_data, (dto.username,))
        user = cur.fetchone()
        if user:
            return utils.BadRequest('User already registered', status_code=401)

        insert_user_query = """
        insert into users(username,password,role,status,login_try_count)
        values (%s,%s,%s,%s,%s);
        """
        user_data = (dto.username, utils.hash_password(dto.password), UserRole.USER.value, UserStatus.ACTIVE.value, 0)
        cur.execute(insert_user_query, user_data)

        conn.commit()
        cur.execute("""Select id from users where username=%s""", (dto.username,))
        user_id = cur.fetchone()
        user = User(username=dto.username, password=utils.hash_password(dto.password), user_id=user_id[0],
                    role=UserRole.USER.value,
                    status=UserStatus.ACTIVE.value, login_try_count=0)
        session.add_session(user)
        return utils.ResponseData('User Successfully Registered👌')

    except AssertionError as e:
        return utils.BadRequest(e)


def logout():
    global session
    if session.check_session():
        session.session = None
        return utils.ResponseData('User Successfully Logged Out !!!')


@utils.login_required
def block_user(_id: str):
    global session
    cur.execute("""Update users set login_try_count=4 where id = %s""", (_id,))
    conn.commit()
    return utils.ResponseData('User Successfully Blocked')


def is_admin():
    global session
    if session.session.role == UserRole.SUPERADMIN.value:
        return True
    else:
        return False