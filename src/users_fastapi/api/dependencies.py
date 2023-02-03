from users_fastapi.db.db import Repo


def get_db_connection():
    repo = Repo()
    yield repo
    repo.close()
