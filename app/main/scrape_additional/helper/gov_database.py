import sqlite3
from datetime import datetime

def connect_db():
    conn = sqlite3.connect("government_profiles.db")  # Creates the database
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS people (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Salutation TEXT,
            FirstName TEXT,
            LastName TEXT,
            Name TEXT,
            Organisation TEXT,
            Department TEXT,
            Position TEXT,
            Gender TEXT,
            Phone TEXT,
            Email TEXT,
            City TEXT,
            State TEXT,
            Country TEXT,
            Source TEXT,
            UNIQUE(Name, Position)  -- <-- composite unique constraint
        );
    """) # The UNIQUE constraint prevents duplicate entries based on Name and Position

    # Create a table to store metadata (like last updated timestamp)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS metadata (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)

    conn.commit()
    return conn, cursor

def commit_batch(conn, cursor, batch):
    cursor.executemany("""
    INSERT INTO people (
        Salutation, FirstName, LastName, Name, Organisation, Department,
        Position, Gender, Phone, Email, City, State, Country, Source
    )
    VALUES (
        :Salutation, :FirstName, :LastName, :Name, :Organisation, :Department,
        :Position, :Gender, :Phone, :Email, :City, :State, :Country, 'https://www.directory.gov.au'
    )
    ON CONFLICT(Name, Position) DO UPDATE SET
        Salutation = excluded.Salutation,
        FirstName = excluded.FirstName,
        LastName = excluded.LastName,
        Organisation = excluded.Organisation,
        Department = excluded.Department,
        Gender = excluded.Gender,
        Phone = excluded.Phone,
        Email = excluded.Email,
        City = excluded.City,
        State = excluded.State,
        Country = excluded.Country,
        Source = excluded.Source
    """, batch)

    update_last_update(cursor)

    conn.commit()

def update_last_update(cursor):
    # Get current datetime and format its
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    cursor.execute("""
        INSERT INTO metadata (key, value) 
        VALUES ('last_update', ?)
        ON CONFLICT(key) DO UPDATE SET value=excluded.value
    """, (now,))

def get_last_update():
    conn, cursor = connect_db()
    cursor.execute("SELECT value FROM metadata WHERE key='last_update'")
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def search_database(fname, lname):
    conn, cursor = connect_db()

    cursor.execute("""
        SELECT * FROM people WHERE FirstName = ? AND LastName = ?
    """, (fname, lname))

    rows = cursor.fetchall()
    col_names = [description[0] for description in cursor.description]

    results = [dict(zip(col_names, row)) for row in rows]

    if results:
        print(f"Found {len(results)} record(s) for {fname} {lname}.")
    else:
        print(f"No records found for {fname} {lname}.")

    conn.close()
    return results