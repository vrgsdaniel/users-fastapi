import logging
import os
from typing import Any, List

import psycopg2

from users_fastapi.model.auth import UserAuth
from users_fastapi.model.users import User, UserForm, UserType

USERS_TABLE = "users.users"


class DuplicateEntryException(Exception):
    pass


class Repo:
    # psycopg2 wrapper
    def __init__(self) -> None:
        self.conn = None
        try:
            self.connect()
            logging.info("db: database ready")
        except Exception as err:
            logging.error("db: failed to connect to database: %s", str(err))
            self.close()
            raise err

    def connect(self):
        """Stores a connection object `conn` of a postgres database"""
        logging.info("db: connecting to database")
        conn_str = os.environ.get("DB_DSN")
        self.conn = psycopg2.connect(conn_str)
        self.conn.autocommit = True

    def close(self):
        """Closes the connection object `conn`"""
        if self.conn is not None:
            logging.info("db: closing database")
            self.conn.close()

    def execute_select_query(self, query: str, args: tuple = ()) -> List[tuple]:
        """Executes a read query and returns the result

        Args:
            query (str): the query to execute.
            args (tuple, optional): arguments to the select statement. Defaults to ().

        Returns:
            List[tuple]: result of the select statement. One element per record
        """
        with self.conn.cursor() as cur:
            cur.execute(query, args)
            return list(cur)

    def execute_upsert_return(self, query: str, values: tuple = ()) -> Any:
        with self.conn.cursor() as cur:
            cur.execute(query, values)
            row = cur.fetchone()
        return row

    def execute_statement(self, query: str, values: tuple = ()) -> None:
        with self.conn.cursor() as cur:
            cur.execute(query, values)

    def truncate_table(self) -> None:
        self.execute_statement(f"TRUNCATE TABLE {USERS_TABLE}")

    # repository functions
    def create_user(self, user: UserForm) -> User:
        query = f"""INSERT INTO {USERS_TABLE} (passhash, email, user_type) values (%s, %s, %s)
        RETURNING id, created_at, user_type"""
        params = (user.passhash, user.email, user.user_type)
        try:
            record = self.execute_upsert_return(query, params)
        except psycopg2.errors.UniqueViolation:
            raise DuplicateEntryException
        return User(id=record[0], created_at=record[1], user_type=record[2], email=user.email)

    def update_user(self, id: str, value: str, field: str) -> (User | None):
        assert field in ("email",)  # could be expanded to other fields
        query = f"""UPDATE {USERS_TABLE} SET {field} = %s , updated_at = now()
         WHERE id = %s RETURNING id, email, created_at, user_type"""
        params = (value, id)
        try:
            record = self.execute_upsert_return(query, params)
        except psycopg2.errors.UniqueViolation:
            raise DuplicateEntryException
        if record is None:
            return None
        return User(id=record[0], email=record[1], created_at=record[2], user_type=record[3])

    def delete_user(self, user_id: str) -> None:
        query = f"DELETE FROM {USERS_TABLE} WHERE id = %s"
        params = (user_id,)
        self.execute_statement(query, params)

    def get_user_by_field(self, field: str, value: str) -> (User | None):
        assert field in ("id", "email")
        query = f"SELECT id, email, created_at, user_type FROM {USERS_TABLE} WHERE {field} =%s"
        params = (value,)
        res = self.execute_select_query(query, params)
        if len(res) == 0:
            return None
        record = res[0]
        return User(id=record[0], email=record[1], created_at=record[2], user_type=record[3])

    def list_users(self, limit: int, offset: int) -> List[User]:
        query = f"SELECT id, email, created_at FROM {USERS_TABLE} LIMIT %s OFFSET %s"
        params = (limit, offset)
        records = self.execute_select_query(query, params)
        if len(records) == 0:
            return []
        return [User(id=r[0], email=r[2], created_at=r[3]) for r in records]

    def is_admin(self, id: str) -> bool:
        query = f"SELECT 1 FROM {USERS_TABLE} WHERE id = %s and user_type = %s"
        params = (id, UserType.admin)
        records = self.execute_select_query(query, params)
        return len(records) > 0

    def get_user_for_auth(self, email: str) -> UserAuth | None:
        query = f"SELECT id, passhash FROM {USERS_TABLE} WHERE email = %s"
        records = self.execute_select_query(query, (email,))
        if len(records) == 0:
            return None
        user_auth = records[0]
        return UserAuth(id=user_auth[0], passhash=user_auth[1])
