"""DuckDB database module for managing services, events, and employees."""

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
    
    # Employees table - עובדים
    conn.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            first_name VARCHAR NOT NULL,
            last_name VARCHAR NOT NULL,
            email VARCHAR,
            phone VARCHAR,
            residence VARCHAR,
            role VARCHAR,
            work_location VARCHAR,
            registered_events VARCHAR
        )
    """)
    
    # Events table - אירועים
    conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY,
            name VARCHAR NOT NULL,
            date DATE
        )
    """)
    
    # Create sequences for auto-increment if not exists
    conn.execute("""
        CREATE SEQUENCE IF NOT EXISTS services_id_seq START 1
    """)
    
    conn.execute("""
        CREATE SEQUENCE IF NOT EXISTS employees_id_seq START 1
    """)
    
    conn.execute("""
        CREATE SEQUENCE IF NOT EXISTS events_id_seq START 1
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


def clear_services_table():
    """Clear all services from the table."""
    conn = get_connection()
    conn.execute("DELETE FROM services")
    conn.commit()
    conn.close()


# --- Employees CRUD operations ---

def get_all_employees() -> list[dict]:
    """Get all employees."""
    conn = get_connection()
    result = conn.execute("""
        SELECT id, first_name, last_name, email, phone, residence, role, work_location, registered_events 
        FROM employees ORDER BY last_name, first_name
    """).fetchall()
    conn.close()
    return [{"id": r[0], "first_name": r[1], "last_name": r[2], "email": r[3], 
             "phone": r[4], "residence": r[5], "role": r[6], "work_location": r[7],
             "registered_events": r[8]} for r in result]


def add_employee(first_name: str, last_name: str, email: str = None, phone: str = None,
                 residence: str = None, role: str = None, work_location: str = None,
                 registered_events: str = None) -> int:
    """Add a new employee. Returns the new employee's ID."""
    conn = get_connection()
    conn.execute("""
        INSERT INTO employees (id, first_name, last_name, email, phone, residence, role, work_location, registered_events)
        VALUES (nextval('employees_id_seq'), ?, ?, ?, ?, ?, ?, ?, ?)
    """, [first_name, last_name, email, phone, residence, role, work_location, registered_events])
    result = conn.execute("SELECT currval('employees_id_seq')").fetchone()[0]
    conn.commit()
    conn.close()
    return result


def add_employees_bulk(employees_data: list[dict], event_name: str = None) -> int:
    """Add multiple employees at once, or update existing ones with new events.
    
    Matches employees by first_name + last_name + email.
    If employee exists, appends event to their registered_events list.
    Returns count of processed employees (new or updated).
    """
    conn = get_connection()
    count = 0
    new_count = 0
    updated_count = 0
    
    for employee in employees_data:
        first_name = employee.get('first_name', '')
        last_name = employee.get('last_name', '')
        email = employee.get('email')
        
        # Check if employee already exists
        existing = conn.execute("""
            SELECT id, registered_events FROM employees 
            WHERE first_name = ? AND last_name = ? AND (email = ? OR (email IS NULL AND ? IS NULL))
        """, [first_name, last_name, email, email]).fetchone()
        
        if existing:
            # Employee exists - append event to their list
            emp_id, current_events = existing
            if current_events:
                # Parse existing events and add new one if not already present
                events_list = [e.strip() for e in current_events.split(',')]
                if event_name and event_name not in events_list:
                    events_list.append(event_name)
                    new_events = ', '.join(events_list)
                    conn.execute("""
                        UPDATE employees SET registered_events = ? WHERE id = ?
                    """, [new_events, emp_id])
                    updated_count += 1
            elif event_name:
                # No events yet, set the new one
                conn.execute("""
                    UPDATE employees SET registered_events = ? WHERE id = ?
                """, [event_name, emp_id])
                updated_count += 1
        else:
            # New employee - insert
            conn.execute("""
                INSERT INTO employees (id, first_name, last_name, email, phone, residence, role, work_location, registered_events)
                VALUES (nextval('employees_id_seq'), ?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                first_name,
                last_name,
                email,
                employee.get('phone'),
                employee.get('residence'),
                employee.get('role'),
                employee.get('work_location'),
                event_name
            ])
            new_count += 1
        count += 1
    
    conn.commit()
    conn.close()
    return count


def clear_employees_table():
    """Clear all employees from the table."""
    conn = get_connection()
    conn.execute("DELETE FROM employees")
    conn.commit()
    conn.close()


def get_employees_count() -> int:
    """Get the count of employees in the table."""
    conn = get_connection()
    result = conn.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
    conn.close()
    return result


# --- Events CRUD operations ---

def get_all_events() -> list[dict]:
    """Get all events."""
    conn = get_connection()
    result = conn.execute("""
        SELECT id, name, date FROM events ORDER BY date DESC, name
    """).fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1], "date": r[2]} for r in result]


def add_event(name: str, date=None) -> int:
    """Add a new event. Returns the new event's ID."""
    conn = get_connection()
    conn.execute("""
        INSERT INTO events (id, name, date)
        VALUES (nextval('events_id_seq'), ?, ?)
    """, [name, date])
    result = conn.execute("SELECT currval('events_id_seq')").fetchone()[0]
    conn.commit()
    conn.close()
    return result


def clear_events_table():
    """Clear all events from the table."""
    conn = get_connection()
    conn.execute("DELETE FROM events")
    conn.commit()
    conn.close()


def get_events_count() -> int:
    """Get the count of events in the table."""
    conn = get_connection()
    result = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    conn.close()
    return result


# Initialize DB on module import
init_db()
