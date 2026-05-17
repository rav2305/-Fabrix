import time

from flask import current_app
from sqlalchemy.exc import IntegrityError, OperationalError

from ..extensions import db


RETRIABLE_DB_FRAGMENTS = (
    "deadlock found",
    "lock wait timeout exceeded",
    "server has gone away",
    "lost connection",
)


def _is_retriable_database_error(error) -> bool:
    message = str(getattr(error, "orig", error)).lower()
    return any(fragment in message for fragment in RETRIABLE_DB_FRAGMENTS)


def run_transaction(operation):
    retries = current_app.config.get("DB_TRANSACTION_RETRIES", 3)
    attempt = 0

    while True:
        try:
            with db.session.begin():
                result = operation(db.session)
            return result
        except OperationalError as exc:
            db.session.rollback()
            attempt += 1
            if attempt >= retries or not _is_retriable_database_error(exc):
                raise
            time.sleep(0.2 * attempt)
        except IntegrityError:
            db.session.rollback()
            raise
        except Exception:
            db.session.rollback()
            raise
