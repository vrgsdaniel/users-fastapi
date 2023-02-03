from datetime import datetime
from uuid import UUID

import pytest

from users_fastapi.db.db import DuplicateEntryException, Repo
from users_fastapi.model.users import User, UserForm, UserType

RANDOM_UUID = str(UUID(int=0x0, version=4))


def is_valid_uuid(uuid_to_test: str, version: int = 4):
    """
    Check if uuid_to_test is a valid UUID.
    """

    try:
        uuid_obj = UUID(uuid_to_test, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_to_test


@pytest.mark.usefixtures("repo")
class TestRepo:
    # TODO: creation of users could be factored out for some tests
    def test_get_and_create_user(self):
        repo: Repo = self.repo
        repo.truncate_table()
        # invalid field
        with pytest.raises(AssertionError):
            repo.get_user_by_field("invalid_field", "invalid_value")

        # valid field, empty db
        user = repo.get_user_by_field("id", RANDOM_UUID)
        assert user is None

        # create user
        email, passhash = "user@email.com", "hashedPassword"
        expected = User(email=email, user_type=UserType.customer)
        new_user = repo.create_user(UserForm(email=email, passhash=passhash))
        assert expected.email == new_user.email
        assert isinstance(new_user.created_at, datetime)
        assert is_valid_uuid(new_user.id)

        # retrieve user
        user_by_id = repo.get_user_by_field("id", new_user.id)
        assert new_user == user_by_id

        user_by_email = repo.get_user_by_field("email", new_user.email)
        assert new_user == user_by_email

        # retrieve non existing user
        user = repo.get_user_by_field("id", RANDOM_UUID)
        assert user is None

        # duplicated user
        with pytest.raises(DuplicateEntryException):
            repo.create_user(UserForm(email=email, passhash=passhash))

    def test_is_admin(self):
        repo: Repo = self.repo
        repo.truncate_table()
        # empty db
        expected, got = False, repo.is_admin(RANDOM_UUID)
        assert expected == got
        # customer
        email, passhash = "user@email.com", "hashedPassword"
        new_user = repo.create_user(UserForm(email=email, passhash=passhash))
        expected, got = False, repo.is_admin(new_user.id)
        assert expected == got
        # admin
        email, passhash = "admin@email.com", "hashedPassword"
        new_user = repo.create_user(UserForm(email=email, passhash=passhash, user_type=UserType.admin))
        expected, got = True, repo.is_admin(new_user.id)
        assert expected == got

    def test_get_user_for_auth(self):
        repo: Repo = self.repo
        repo.truncate_table()
        email, passhash = "user@email.com", "hashedPassword"
        # empty db
        user = repo.get_user_for_auth(email)
        assert user is None

        # create user and retrieve it
        new_user = repo.create_user(UserForm(email=email, passhash=passhash))
        user = repo.get_user_for_auth(email)
        assert new_user.id == user.id
        assert passhash == user.passhash

        # non-existing email
        user = repo.get_user_for_auth("fake@email.com")
        assert user is None

    def test_list_users(self):
        pass

    def test_update_user(self):
        repo: Repo = self.repo
        repo.truncate_table()
        # invalid field
        with pytest.raises(AssertionError):
            repo.update_user("id", "value", "invalid_field")

        # empty db
        user = repo.update_user(RANDOM_UUID, "new@email.com", "email")
        assert user is None

        # create and update user
        email, passhash = "user@email.com", "hashedPassword"
        new_user = repo.create_user(UserForm(email=email, passhash=passhash))
        updated_user = repo.update_user(new_user.id, "new@email.com", "email")
        assert new_user.id == updated_user.id
        assert new_user.created_at == updated_user.created_at
        assert "new@email.com" == updated_user.email

        # create new user update email to existing one
        new_user = repo.create_user(UserForm(email=email, passhash=passhash))
        with pytest.raises(DuplicateEntryException):
            repo.update_user(new_user.id, "new@email.com", "email")

    def test_delete_user(self):
        repo: Repo = self.repo
        repo.truncate_table()

        # empty db (no raised error)
        repo.delete_user(RANDOM_UUID)

        # create and delete user
        email, passhash = "user@email.com", "hashedPassword"
        new_user = repo.create_user(UserForm(email=email, passhash=passhash))
        repo.delete_user(new_user.id)
        deleted_user = repo.get_user_by_field("id", new_user.id)
        assert deleted_user is None
