import logging
import os
from time import sleep, time

import psycopg2

check_timeout = os.getenv("POSTGRES_CHECK_TIMEOUT", 30)
check_interval = os.getenv("POSTGRES_CHECK_INTERVAL", 1)
interval_unit = "second" if check_interval == 1 else "seconds"
config = {
    "dbname": os.getenv("POSTGRES_DB", "postgres"),
    "user": os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD", "postgres"),
    "host": os.getenv("DATABASE_URL", "postgres")
}

start_time = time()
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


def pg_isready(host: str, user: str, password: str, dbname: str) -> bool:
    """ Checks and returns the status of database for connection.

    Args:
        host: The host of the database.
        user: The user of the database.
        password: The database password.
        dbname: The name of the database.

    Returns:
        bool: The readiness of the database.
    """
    while time() - start_time < check_timeout:
        try:
            conn = psycopg2.connect(**vars())
            logger.info("Postgres is ready! ✨ 💅")
            conn.close()
            return True
        except psycopg2.OperationalError as e:
            print(e)
            logger.info(
                f"Postgres isn't ready. Waiting for {check_interval} {interval_unit}..."
            )
            sleep(check_interval)

    logger.error(
        f"We could not connect to Postgres within {check_timeout} seconds.")
    return False


pg_isready(**config)
