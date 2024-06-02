from enum import Enum
from typing import Optional
from collections import namedtuple


class UserRole(Enum):
    ADMIN = 'ADMIN'
    USER = 'USER'
    SUPERADMIN = 'SUPERADMIN'


class UserStatus(Enum):
    ACTIVE = 'ACTIVE'
    INACTIVE = 'INACTIVE'
    BLOCKED = 'BLOCKED'


class TodoType(Enum):
    Optional = 'optional'
    Personal = 'personal'
    Shopping = 'shopping'


class User:
    def __init__(self,
                 username: str,
                 password: str,
                 user_id: Optional[int] = None,
                 role: Optional[UserRole] = None,
                 status: Optional[UserStatus] = None,
                 login_try_count: Optional[int] = None
                 ):
        self.username = username
        self.password = password
        self.id = user_id
        self.role = role or UserRole.USER.value
        self.status = status or UserStatus.INACTIVE.value
        self.login_try_count = login_try_count or 0

    @staticmethod
    def from_tuple(args):
        return User(user_id=args[0],
                    username=args[1],
                    password=args[2],
                    role=args[3],
                    status=args[4],
                    login_try_count=args[5])



    def __str__(self):
        return f'{self.role} => {self.username}'


class Todo:
    def __init__(self,
                 title: str,
                 user_id: int,
                 todo_type: Optional[TodoType] = None,
                 ):
        self.title = title
        self.user_id = user_id
        self.todo_type = todo_type or TodoType.Optional.value

