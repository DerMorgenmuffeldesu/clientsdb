import psycopg2

with psycopg2.connect(database="clientsdb", user="postgres", password="") as conn:

    def create_db(conn):
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS Client (
                client_id SERIAL PRIMARY KEY,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                email VARCHAR(100) UNIQUE
                )
                """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS Phone (
                phone_id SERIAL PRIMARY KEY,
                client_id INT REFERENCES Client(client_id),
                phone_number VARCHAR(15) NOT NULL
                )
                """)
    conn.commit()

# Function to add a new client
def add_client(conn, first_name, last_name, email, phones=None):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO Client (first_name, last_name, email)
            VALUES (%s, %s, %s)
            RETURNING client_id
        """, (first_name, last_name, email))
        client_id = cur.fetchone()[0]
        if phones:
            for phone in phones:
                add_phone(conn, client_id, phone)

# Function to add a phone for an existing client
def add_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO Phone (client_id, phone_number)
            VALUES (%s, %s)
        """, (client_id, phone))

# Function to change client data
def change_client(conn, client_id, first_name=None, last_name=None, email=None, phones=None):
    with conn.cursor() as cur:
        if first_name:
            cur.execute("""
                UPDATE Client
                SET first_name = %s
                WHERE client_id = %s
            """, (first_name, client_id))
        if last_name:
            cur.execute("""
                UPDATE Client
                SET last_name = %s
                WHERE client_id = %s
            """, (last_name, client_id))
        if email:
                cur.execute("""
                UPDATE Client
                SET email = %s
                WHERE client_id = %s
            """, (email, client_id))
        if phones:
            cur.execute("""
                DELETE FROM Phone
                WHERE client_id = %s
            """, (client_id,))
            for phone in phones:
                add_phone(conn, client_id, phone)

# Function to delete a phone for an existing client
def delete_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute("""
            DELETE FROM Phone
            WHERE client_id = %s AND phone_number = %s
        """, (client_id, phone))

# Function to delete an existing client
def delete_client(conn, client_id):
    with conn.cursor() as cur:
        cur.execute("""
            DELETE FROM Client
            WHERE client_id = %s
        """, (client_id,))

# Function to find a client by their data
def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    with conn.cursor() as cur:
        if first_name:
            cur.execute("""
                SELECT * FROM Client
                WHERE first_name = %s
            """, (first_name,))
        elif last_name:
            cur.execute("""
                SELECT * FROM Client
                WHERE last_name = %s
            """, (last_name,))
        elif email:
            cur.execute("""
                SELECT * FROM Client
                WHERE email = %s
            """, (email,))
        elif phone:
            cur.execute("""
                SELECT * FROM Client
                WHERE client_id IN (
                    SELECT client_id FROM Phone
                    WHERE phone_number = %s
                )
            """, (phone,))
        else:
            return None
        return cur.fetchall()

# Connecting to the database and calling functions
with psycopg2.connect(database="clientsdb", user="postgres", password="") as conn:
    create_db(conn)

    # Adding a new client
    add_client(conn, "John", "Doe", "john.doe@example.com", ["123456789", "987654321"])

    # Changing client data
    change_client(conn, 1, first_name="", last_name="", email="", phones=["555555555", "999999999"])

    # Deleting a phone for a client
    delete_phone(conn, 1, "123456789")

    # Deleting a client
    delete_phone(conn, 1)
    delete_client(conn, 1)

    # Finding a client
    result = find_client(conn, first_name= "", last_name="", email="", phone="")
    print("Found client:", result)