"""
Database wrapper for PostgreSQL compatibility with cs50.SQL-like interface
"""
import psycopg2
import psycopg2.extras
from psycopg2.extras import RealDictCursor
import os
from contextlib import contextmanager


class Database:
    def __init__(self, database_url=None):
        if database_url is None:
            database_url = os.environ.get('DATABASE_URL') or \
                f"postgresql://{os.environ.get('DB_USER', 'postgres')}:" \
                f"{os.environ.get('DB_PASSWORD', 'postgres')}@" \
                f"{os.environ.get('DB_HOST', 'localhost')}:" \
                f"{os.environ.get('DB_PORT', '5432')}/" \
                f"{os.environ.get('DB_NAME', 'unimak')}"
        
        self.database_url = database_url
        self._connection = None
    
    def _get_connection(self):
        if self._connection is None or self._connection.closed:
            self._connection = psycopg2.connect(
                self.database_url,
                cursor_factory=RealDictCursor
            )
        return self._connection
    
    def execute(self, query, *args):
        """
        Execute a query and return results as list of dicts.
        Compatible with cs50.SQL interface.
        """
        conn = self._get_connection()
        with conn.cursor() as cur:
            try:
                cur.execute(query, args)
                conn.commit()
                
                # For SELECT queries, return results
                if query.strip().upper().startswith('SELECT'):
                    return cur.fetchall()
                # For INSERT, return last inserted ID
                elif query.strip().upper().startswith('INSERT'):
                    cur.execute("SELECT lastval() AS id")
                    result = cur.fetchone()
                    return [{'id': result['id']}]
                # For other queries, return empty list
                else:
                    return []
            except Exception as e:
                conn.rollback()
                raise e
    
    def close(self):
        if self._connection and not self._connection.closed:
            self._connection.close()
            self._connection = None
    
    def __del__(self):
        self.close()

