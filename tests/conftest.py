import pytest

from users_fastapi.db.db import Repo


@pytest.fixture(scope="class", name="repo")
def repo(request):
    """Instantiates a database object"""
    db = Repo()
    try:
        request.cls.repo = db
        yield db
    finally:
        db.close()


@pytest.fixture(scope="class", name="clean_db")
def clean_db(request):
    """Instantiates a database object"""
    db = Repo()
    try:
        db.truncate_table()
        yield
    finally:
        db.truncate_table()
