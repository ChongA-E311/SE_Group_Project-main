from UniqueCodedGenerator import db_check
import sqlite3
import Encryption
DB_NAME = "project_database.db"

def db_type(code):
    """
    Returns the type of the organisation based on the unique code.
    Takes in the unique code as a parameter.
    """
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT org_type FROM organisations WHERE org_id = ?", (code[:4],))
        return cursor.fetchone()[0]

def register(code, username, password):
    """
    Registers a new user in the database.
    Takes in the unique code, username, and password.
    Encrypts the password and stores it in the database along with other information.
    Deletes the unique code from the database.
    Returns a message indicating whether the registration statement.
    """
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT username FROM user_info WHERE username = ?", (username,))
        if cursor.fetchone():
            return "Username already exists"

        if db_check(code):
            encryptor = Encryption.HybridEncryptor()
            encrypted_password, encrypted_aes, rsa_key = encryptor.encrypt_aes(password)

            if len(code) == 10:
                class_id = code[4:8]
            else:
                class_id = None

            if code == "0000":
                user_type = "komodo_admin"
            else:
                user_type = "standard"

            cursor.execute(
                "INSERT INTO user_info (username, password, encrypted_aes, rsa_key, user_org, org_type, user_class, user_type) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (username, encrypted_password, encrypted_aes, rsa_key, code[:4], db_type(code), class_id, user_type))
            cursor.execute("DELETE FROM unique_code WHERE valid_unique_code = ?", (code,))
            conn.commit()
            return "Registration successful!"
        else:
            return "Invalid unique code"

# register("L3Zk6d", "Kale", "Test1234")
# register("L3ZkAC419M", "Tom", "Test1234")
# register("R9m2J4", "Scott", "Test1234")
# with sqlite3.connect(DB_NAME) as conn:
#    cursor = conn.cursor()
#    cursor.execute("SELECT * FROM user_info")
#    for row in cursor.fetchall():
#        for col in row:
#            print(col)

#to allow user to change password
def change_password(username, current_password, new_password):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT password, encrypted_aes, rsa_key FROM user_info WHERE username = ?", (username,))
        result = cursor.fetchone()

        if not result:
            return "User not found"

        encrypted_password, encrypted_aes, rsa_key = result

        encryptor = Encryption.HybridEncryptor()
        try:
            decrypted_password = encryptor.decrypt_aes(encrypted_password, encrypted_aes, rsa_key)
        except Exception:
            return "Error decrypting stored password"

        if current_password != decrypted_password:
            return "Current password is incorrect"

        new_encrypted_password, new_encrypted_aes, new_rsa_key = encryptor.encrypt_aes(new_password)

        cursor.execute(
            "UPDATE user_info SET password = ?, encrypted_aes = ?, rsa_key = ? WHERE username = ?",
            (new_encrypted_password, new_encrypted_aes, new_rsa_key, username)
        )
        conn.commit()
        return "Password changed successfully!"

