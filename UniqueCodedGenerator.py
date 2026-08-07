import random
import string
import sqlite3
import os

DB_NAME = "project_database.db"

def db_check(code):
    """Checks if the unique code exists in the database."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM unique_code WHERE valid_unique_code = ?", (code,))
        return cursor.fetchone()[0] > 0  # Returns True if code exists

def db_insert(code):
    """Inserts a new unique code into the database."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO unique_code (valid_unique_code) VALUES (?)", (code,))
        conn.commit()  # Save changes

# Generates a list of unique codes and stores them in the database with their respective organisation
def generate_code(amount, organisation, class_id=None):
    """
    Generates a list of unique codes and stores them in the database.
    First 4 characters of the code is the organisation ID.
    Next 4 characters of the code is the class if a school
    Last 2 characters of the code is a random string to make the code unique
    """
    if class_id is None:
        class_id = ""

    code_list = []
    while len(code_list) < amount:
        random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=2))
        code = organisation + class_id + random_string
        if not db_check(code):
            db_insert(code)  # Store in database
            code_list.append(code)
    return code_list

#print(generate_code(1, "L3Zk"))
#print(generate_code(1, "L3Zk", "AC41"))
#print(generate_code(2, "R9m2"))
#print(generate_code(1, "0000"))