import pytest
import copy
from datetime import datetime, timedelta

from .services import AuthService, AuthenticationFailedError 
from .models import Authorisation, User
from .repositories import AuthorisationRepository, UserRepository
from datetime import datetime
import pytz


class InMemoryAuthorisationRepository(AuthorisationRepository):

    def __init__(self, auths):
        self.auths = auths
   
    def get_by_user_name(self, user_name):
        try:
            return next((u for u in self.auths if u.user_name == user_name ))
        except StopIteration:
            return None

    def get_by_user_id(self, user_id):
        try:
            return next((u for u in self.auths if u.user_id == user_id))
        except StopIteration:
            return None

    def add(self, auth):
        self.auths.append(auth)
        return auth.user_id

    def update(self, auth):
        _auth = self.get_by_user_name(auth.user_name)
        if not auth:
            raise Exception("Cannot update what is not found")
        _auth.user_name = auth.user_name
        _auth.password = auth.password
        _auth.roles = auth.roles


class InMemoryUserRepository(UserRepository):

    def __init__(self, users):
        self.users = users

    def generate_id(self):
        return (max(u.id for u in self.users) + 1) if self.users else 1

    def get_by_id(self, user_id):
        try:
            return next((u for u in self.users if u.id == user_id))
        except StopIteration:
            return None

    def update(self, user):
        _user = self.get_by_id(user.id)
        _user.name = user.name
        _user.email= user.email
        _user.phone = user.phone

    def add(self, user):
        self.users.append(user)


@pytest.fixture()
def auth_service():
    user_repository = InMemoryUserRepository(copy.copy(USERS))
    auth_repository =  InMemoryAuthorisationRepository(copy.copy(AUTHS))
    _auth_service = AuthService(user_repository, auth_repository)
    return _auth_service


def test_add_user(auth_service):
    user = auth_service.add('test name', 'test@email', '+testphone', 'username', 'password', ['what', 'ever'])
    assert user.name == 'test name'

def test_get_user(auth_service):
    user = auth_service.get(1)
    assert user.name == 'test user 1'

def test_authenticate(auth_service):
    user = auth_service.authenticate('test_user_name_1', 'test_password')
    assert user.id == 1
    try:
        user = auth_service.authenticate('test_user_name_2', 'test_password2')
        raise Exception("This should fail")
    except AuthenticationFailedError:
        pass

def test_change_password(auth_service):
    old_password = 'test_password'
    new_password = 'new_password'
    user_id = 1
    user = auth_service.change_password(user_id, old_password, new_password)
    assert user is not None
    try:
        user = auth_service.change_password(user_id, old_password, new_password)
        raise Exception("This should fail")
    except AuthenticationFailedError:
        pass

def test_add_role(auth_service):
    user_id = 2 
    user = auth_service.add_role(user_id, 'new role')
    assert user.roles is not None and 'new role' in user.roles

def test_remove_role(auth_service):
    user_id = 2
    user = auth_service.remove_role(user_id, 'role 1')
    assert user.roles is not None and 'role 1' not in user.roles


AUTHS = [
    Authorisation(1, 'test_user_name_1', 'test_password', ['role 1', 'role2']),
    Authorisation(2, 'test_user_name_2', 'test_password', ['role 1', 'role2']),
]

USERS = [
        User(1, 'test user 1', 'testemail1', 'testphone1'),
        User(2, 'test user 2', 'testemail2', 'testphone2'),
]


