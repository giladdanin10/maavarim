"""DuckDB database module for managing services, events, and people."""

import duckdb
from pathlib import Path

DB_PATH = Path(__file__).parent / "maavarim.duckdb"


def get_connection():
    """Get a connection to the DuckDB database."""
    return duckdb.connect(str(DB_PATH))


def init_db():
    """Initialize the database with required tables."""
    conn = get_connection()
    
    # Services table - שירותים
    conn.execute("""
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY,
            name VARCHAR NOT NULL UNIQUE,
            domain VARCHAR NOT NULL
        )
    """)
    
    # Create sequence for auto-increment if not exists
    conn.execute("""
        CREATE SEQUENCE IF NOT EXISTS services_id_seq START 1
    """)
    
    conn.close()


# --- Services CRUD operations ---

def get_all_services() -> list[dict]:
    """Get all services with their domains."""
    conn = get_connection()
    result = conn.execute("""
        SELECT id, name, domain FROM services ORDER BY domain, name
    """).fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1], "domain": r[2]} for r in result]


def get_domains() -> list[str]:
    """Get list of unique domains."""
    conn = get_connection()
    result = conn.execute("""
        SELECT DISTINCT domain FROM services ORDER BY domain
    """).fetchall()
    conn.close()
    return [r[0] for r in result]


def add_service(name: str, domain: str) -> bool:
    """Add a new service. Returns True if successful."""
    conn = get_connection()
    try:
        conn.execute("""
            INSERT INTO services (id, name, domain)
            VALUES (nextval('services_id_seq'), ?, ?)
        """, [name, domain])
        conn.commit()
        conn.close()
        return True
    except duckdb.ConstraintException:
        conn.close()
        return False


def update_service(service_id: int, name: str, domain: str) -> bool:
    """Update an existing service."""
    conn = get_connection()
    try:
        conn.execute("""
            UPDATE services SET name = ?, domain = ? WHERE id = ?
        """, [name, domain, int(service_id)])
        conn.commit()
        conn.close()
        return True
    except duckdb.ConstraintException:
        conn.close()
        return False


def delete_service(service_id: int):
    """Delete a service by ID."""
    conn = get_connection()
    conn.execute("DELETE FROM services WHERE id = ?", [int(service_id)])
    conn.commit()
    conn.close()


# Initialize DB on module import
init_db()
