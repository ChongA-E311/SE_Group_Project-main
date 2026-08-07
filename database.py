import sqlite3
from datetime import datetime


DB_NAME = "project_database.db"

def execute_query(query, params=(), fetch_one=False):
    """
    Executes a SQL query and returns the result.
    query - The SQL query to execute.
    params - Information to be passed to the query.
    fetch_one - If True, fetches one result
    """
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        if fetch_one:
            return cursor.fetchone()
        return cursor.fetchall()

def get_user_info(username):
    """
    Retrieves user information from the database.
    """
    query = "SELECT password, encrypted_aes, rsa_key, org_type, user_type, user_class, user_org FROM user_info WHERE username = ?"
    return execute_query(query, (username,), fetch_one=True)

def get_organisations():
    """
    Retrieves all organisations from the database.
    """
    query = "SELECT org_name FROM organisations"
    return execute_query(query)

def get_contacts(current_user):
    """
    Retrieves all contacts for the current user from the database.
    """
    query = ("SELECT DISTINCT CASE WHEN message_sender = ? THEN message_receiver WHEN message_receiver = ?"
             " THEN message_sender END FROM messages WHERE message_sender = ? OR message_receiver = ?")
    params = (current_user, current_user, current_user, current_user)
    return execute_query(query, params)

def get_messages(current_user, current_contact):
    """
    Retrieves all messages between the current user and the current contact from the database.
    Order the messages by the time they were sent.
    """
    query = ("SELECT message_sender, message_receiver, message_content, message_time, encrypted_aes "
             "FROM messages WHERE (message_sender = ? AND message_receiver = ?) OR "
             "(message_sender = ? AND message_receiver = ?) ORDER BY message_time ASC")
    params = (current_user, current_contact, current_contact, current_user)
    return execute_query(query, params)

def insert_message(sender, receiver, content, encrypted_aes):
    """
    Inserts a new message into the database. With the current date and time.
    """
    query = ("INSERT INTO messages (message_sender, message_receiver, message_content, message_time, "
             "encrypted_aes) VALUES (?, ?, ?, ?, ?)")
    params = (sender, receiver, content, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), encrypted_aes)
    execute_query(query, params)

def get_libraries():
    """
    Retrieves all libraries from the database and returns them as a distinct list
    """
    query = "SELECT org_name FROM organisations WHERE org_id IN (SELECT DISTINCT library_org FROM libraries)"
    return execute_query(query)


def get_library_posts(library_name):
    """
    Retrieves all posts from a specific library from the database and returns them as a distinct list
    """
    query = "SELECT post_title, post_content, post_image FROM libraries WHERE library_org = ?"
    return execute_query(query, (library_name))

def get_org_id(org_name):
    query = "SELECT org_id FROM organisations WHERE org_name = ?"
    return execute_query(query, (org_name,), fetch_one=True)

def get_assignment_id(assignment_id):
    query = "SELECT assignment_id FROM schl_assignments WHERE assignment_id = ?"
    return execute_query(query, (assignment_id,), fetch_one=True)

def insert_assignments(content, deadline, title, time, current_user, class_id):
    """
    Insert assignment information into the database
    """
    query = ("INSERT INTO schl_assignments (assignment_content, "
             "assignment_deadline, assignment_title, assignment_creator, assignment_class) VALUES (?, ?, ?, ?, ?)")
    params = (content, (deadline + " " + time), title, current_user, class_id)
    execute_query(query, params)

def get_user_org(username):
    """
    Retrieves user organization from the database.
    """
    query = "SELECT user_org FROM user_info WHERE username = ?"
    return execute_query(query, (username,), fetch_one=True)[0]

def get_community_posts(org_id):
    """
    retrieves all posts from a given community/school
    """
    query = "SELECT post_creator, post_content, post_date FROM comm_posts WHERE comm_id = ?"
    return execute_query(query, (org_id,))

def insert_community_post(organisation, content, sender):
    """
    Inserts a community post into the database. With the current date and time.
    """
    query = ("INSERT INTO comm_posts (comm_id, post_content, post_creator, post_date) VALUES (?, ?, ?, ?)")
    params = (organisation, content, sender, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    execute_query(query, params)



def get_class_assignments(class_id):
    """
    Retrieve assignment from database for specific class
    """
    query = "SELECT * FROM schl_assignments WHERE assignment_class = ? ORDER BY assignment_deadline ASC"
    return execute_query(query, (class_id,))

def delete_assignment(assignment_id):
    """
    Delete a specific assignment from the database
    """
    if isinstance(assignment_id, tuple):
        assignment_id = assignment_id[0]
    query = "DELETE FROM schl_assignments WHERE assignment_id = ?"
    execute_query(query, (assignment_id,))

def insert_submission(assignment_id, submission_creator, submission_content):
    """
    Insert submission information into the database
    """
    query = ("INSERT INTO schl_submissions (submission_assi, submission_contents, submission_creator, "
             "submission_time) VALUES (?, ?, ?, ?)")
    params = (assignment_id, submission_content, submission_creator, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    execute_query(query, params)

def insert_feedback(grade, feedback):
    """
    Insert feedback information into the database
    """
    query = ("INSERT INTO schl_feedback (feedback_submission, feedback_content, feedback_time) VALUES (?, ?, ?)")
    params = (grade, feedback, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    execute_query(query, params)

def get_teacher(current_user):
    """
    Retrieves the teacher of a student from the database
    """
    query = "SELECT u2.username FROM user_info u1 JOIN user_info u2 ON u1.user_class = u2.user_class WHERE u1.username = ? AND u2.user_type = 'teacher'"
    params = (current_user,)
    return execute_query(query, params)

def get_students(current_user):
    """
    Retrieves the students of a teacher from the database
    """
    query = "SELECT u2.username FROM user_info u1 JOIN user_info u2 ON u1.user_class = u2.user_class WHERE u1.username = ? AND u2.user_type = 'student'"
    params = (current_user,)
    return execute_query(query, params)

def get_org_admins(current_user):
    """
    Retrieves the admins of the current users org from the database
    """
    query = "SELECT username, user_type FROM user_info WHERE user_type IN ('org_admin', 'org_leader') AND org_name = (SELECT org_name FROM user_info WHERE username = ?)"
    params = (current_user,)
    return execute_query(query, params)

def create_organisation(org_name, address):
    """
    Creates a new organisation in the database.
    """
    query = ("INSERT INTO Organisations (name, address, created_at) "
             "VALUES (?, ?, ?)")
    params = (org_name, address, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    execute_query(query, params)

def delete_organisation(org_id):
    """
    Deletes an organisation from the database.
    """
    query = "DELETE FROM Organisations WHERE organisation_id = ?"
    execute_query(query, (org_id,))

def delete_user(user_id):
    """
    Deletes a user from the database.
    """
    query = "DELETE FROM user_info WHERE user_id = ?"
    execute_query(query, (user_id,))

def promote_user(user_id, role):
    """
    Promotes a user to a specified role.
    """
    query = "UPDATE user_info SET role = ? WHERE user_id = ?"
    execute_query(query, (role, user_id))

def reset_password(username, new_password):
    """
    Resets a user's password in the database.
    """
    query = "UPDATE user_info SET password = ? WHERE username = ?"
    execute_query(query, (new_password, username))

def move_student_class(student_id, new_class_id):
    """
    Moves a student to a different class.
    """
    query = "UPDATE Enrollments SET class_id = ? WHERE user_id = ?"
    execute_query(query, (new_class_id, student_id))

def get_org_type(org_name):
    query = "SELECT org_type FROM organisations WHERE org_name = ?"
    return execute_query(query, (org_name,), fetch_one=True)

def get_org_users(org_id):
    query = "SELECT user_id, username, user_type, user_org, user_class FROM user_info WHERE user_org = ?"
    return execute_query(query, (org_id,))

def update_user_type(user_id, new_type):
    query = "UPDATE user_info SET user_type = ? WHERE user_id = ?"
    execute_query(query, (new_type, user_id))

def get_all_users():
    query = "SELECT user_id, username, user_type, user_org, user_class FROM user_info"
    return execute_query(query)

def get_encryption_keys(username):
    query = "SELECT encrypted_aes, rsa_key FROM user_info WHERE username = ?"
    params = (username,)
    return execute_query(query, params, fetch_one=True)

def get_org_rows():
    query = "SELECT * FROM Organisations"
    return execute_query(query)