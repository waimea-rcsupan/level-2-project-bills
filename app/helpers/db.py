
#============================================================================
# SQLite Database Setup and Logging
#============================================================================

from contextlib import contextmanager
from pathlib import Path
from dotenv import load_dotenv
from os import getenv, environ
from rich.table import Table, box
import sqlite3

from app.db.config import TABLES
from app.helpers.log import get_logger, get_console, log_prefix, truncate, wrap_lines, _announce

load_dotenv()
LOCAL_DB_PATH = getenv("LOCAL_DB_PATH", "app/db/data.sqlite")

DB_LOGGER = "DB"
PREVIEW_ROWS = 5

TYPE_COLOUR = {
    "INTEGER":   "cyan",
    "REAL":      "cyan",
    "NUMERIC":   "cyan",
    "TIMESTAMP": "blue",
    "DATETIME":  "blue",
    "TEXT":      "green",
    "BLOB":      "magenta",
}

console = get_console()


def _prefix(action="", colour="blue"):
    """Helper to create database log prefix"""
    return log_prefix(action, colour, DB_LOGGER)


@contextmanager
def connect_db():
    """Create a database connection with Rich logging"""
    connection = sqlite3.connect(LOCAL_DB_PATH)
    connection.row_factory = _dict_factory

    wrapped_connection = _LoggingConnection(connection)

    try:
        yield wrapped_connection
        wrapped_connection.commit()
    except Exception:
        wrapped_connection.rollback()
        raise
    finally:
        wrapped_connection.close()


def _dict_factory(cursor, row):
    """Convert database rows to dictionaries"""
    return dict(zip([col[0] for col in cursor.description], row))


class _LoggingCursor:
    """Cursor wrapper that logs query results"""

    def __init__(self, cursor, sql_type):
        self._cursor = cursor
        self._sql_type = sql_type
        self._logger = get_logger()

    def fetchall(self):
        rows = self._cursor.fetchall()
        if self._sql_type == 'SELECT':
            self._log_rows(rows)
        return rows

    def fetchone(self):
        row = self._cursor.fetchone()
        if self._sql_type == 'SELECT':
            self._log_single_row(row)
        return row

    def _log_rows(self, rows):
        """Log multiple rows with preview"""
        num_rows = len(rows)
        self._logger.debug(
            f"{_prefix('Resu')} {num_rows} {'row' if num_rows == 1 else 'rows'} returned"
        )

        if num_rows > 0:
            for row in rows[:PREVIEW_ROWS]:
                self._logger.debug(f"{_prefix()} {truncate(row)}")

            if num_rows > PREVIEW_ROWS:
                self._logger.debug(f"{_prefix()} ... and {num_rows - PREVIEW_ROWS} more")

    def _log_single_row(self, row):
        """Log a single row result"""
        row_text = "1 row" if row else "0 rows"
        self._logger.debug(f"{_prefix('Resu')} {row_text} returned")

        if row:
            self._logger.debug(f"{_prefix()} {truncate(row)}")

    def __getattr__(self, name):
        return getattr(self._cursor, name)


class _LoggingConnection:
    """Connection wrapper that logs all database operations"""

    def __init__(self, conn):
        self._conn = conn
        self._logger = get_logger()

    def execute(self, sql, params=(), logged=True):
        """Execute a single SQL statement with logging"""
        try:
            if logged:
                collapsed_sql = ' '.join(sql.split())
                self._log_query(collapsed_sql, params)

            cursor = self._conn.execute(sql, params)

            if logged:
                if self._is_select(sql):
                    return _LoggingCursor(cursor, 'SELECT')

                self._log_mutation_result(sql, cursor.rowcount, cursor.lastrowid)

            return cursor

        except sqlite3.Error as e:
            self._log_error(e, sql, params)
            raise

    def executemany(self, sql, params):
        """Execute SQL with multiple parameter sets"""
        try:
            collapsed_sql = ' '.join(sql.split())
            params_list = list(params)
            num_rows = len(params_list)

            self._log_query(collapsed_sql, f"{num_rows} row{'s' if num_rows != 1 else ''}")

            cursor = self._conn.executemany(sql, params_list)
            self._log_mutation_result(sql, cursor.rowcount, cursor.lastrowid)

            return cursor

        except sqlite3.Error as e:
            self._log_error(e, sql, f"{num_rows} rows")
            raise

    def _is_select(self, sql):
        """Check if SQL is a SELECT statement"""
        return sql.strip().upper().startswith('SELECT')

    def _log_query(self, sql, params):
        """Log the query being executed"""
        self._logger.debug(f"{_prefix('Qury')} {wrap_lines(sql)}")
        self._logger.debug(f"{_prefix('Para')} {wrap_lines(params)}")

    def _log_mutation_result(self, sql, rowcount, lastrowid):
        """Log the result of INSERT/UPDATE/DELETE"""
        sql_upper = sql.upper()
        row_text = f"{rowcount} row{'s' if rowcount != 1 else ''}"

        if sql_upper.startswith('INSERT'):
            self._logger.debug(f"{_prefix('Resu')} {row_text} inserted [dim](ID: {lastrowid})[/dim]")
        elif sql_upper.startswith('UPDATE'):
            self._logger.debug(f"{_prefix('Resu')} {row_text} updated")
        elif sql_upper.startswith('DELETE'):
            self._logger.debug(f"{_prefix('Resu')} {row_text} deleted")
        else:
            self._logger.debug(f"{_prefix('Resu')} {row_text} affected")

    def _log_error(self, error, sql=None, params=None):
        """Log database errors"""
        self._logger.error(f"{_prefix('Err', 'red bold')} {wrap_lines(error)}")
        if sql:
            self._logger.error(f"{_prefix('Qury', 'red')} {wrap_lines(sql)}")
        if params:
            self._logger.error(f"{_prefix('Para', 'red')} {wrap_lines(params)}")

    def commit(self):
        return self._conn.commit()

    def rollback(self):
        return self._conn.rollback()

    def close(self):
        return self._conn.close()

    def __getattr__(self, name):
        return getattr(self._conn, name)


def init_database():
    """Initialize database with all configured tables"""
    if environ.get('WERKZEUG_RUN_MAIN') != 'true':
        return

    _create_db_if_needed()

    for table in TABLES:
        _init_db_table(table.NAME, table.SCHEMA, table.SEED_DATA)


def _create_db_if_needed():
    """Initialize database - ensure directory exists"""
    db_path = Path(LOCAL_DB_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)


def _init_db_table(table_name, schema, seed_sql):
    """Initialize a database table and auto-patch fields safely if needed"""
    logger = get_logger()
    
    with connect_db() as db:
        if _table_exists(db, table_name):
            if table_name == 'bill':
                columns = db.execute("PRAGMA table_info(bill)", logged=False).fetchall()
                if not any(c.get('name') == 'due_date' for c in columns):
                    logger.info(f"{_prefix('Patc', 'yellow')} Patching 'bill' table to add 'due_date' column...")
                    try:
                        db.execute("ALTER TABLE bill ADD COLUMN due_date TEXT;")
                    except sqlite3.OperationalError:
                        pass
            return

        logger.info(f"{_prefix('Tabl', 'cyan')} creating '{table_name}'...")
        db.execute(schema)

        if seed_sql:
            _seed_table(db, logger, table_name, seed_sql)


def _table_exists(db, table_name):
    """Check if a table exists in the database"""
    result = db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,),
        logged=False
    ).fetchone()
    return result is not None


def _seed_table(db, logger, table_name, seed_sql):
    """Seed a table with initial data"""
    logger.info(f"{_prefix('Tabl', 'cyan')} seeding '{table_name}' with data")
    db.execute(seed_sql)
    logger.info(f"{_prefix('Tabl', 'cyan')} '{table_name}' seeded with data")


def db_show():
    """Placeholder to log structural schema info configurations"""
    pass

def db_reset():
    """Clears and reinits tables on command loop parameters"""
    _create_db_if_needed()
    for table in TABLES:
        with connect_db() as db:
            db.execute(f"DROP TABLE IF EXISTS {table.NAME}")
        _init_db_table(table.NAME, table.SCHEMA, table.SEED_DATA)

def db_clear():
    """Truncates tracking table targets"""
    for table in TABLES:
        with connect_db() as db:
            db.execute(f"DELETE FROM {table.NAME}")

def db_data():
    """Helper to return layout info mappings"""
    return []

def db_schema():
    """Helper to expose active structural table metrics"""
    return ""