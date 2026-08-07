import random
from keyboard import on_release
from kivy.app import App
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.recycleview import RecycleView
from kivy.properties import StringProperty
from kivy.lang import Builder
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Color, RoundedRectangle
from kivy.properties import StringProperty, ListProperty
from kivy.metrics import dp
from kivy.clock import Clock
from datetime import datetime
import os
import sqlite3
import Encryption
import Account_Register
import database

# Load all .kv files from the UI_Menus directory
for file in os.listdir("UI_Menus"):
    if file.endswith(".kv"):
        with open(os.path.join("UI_Menus", file), encoding="utf-8") as f:
            Builder.load_string(f.read())


class BaseScreen(Screen):

    # Button Classes to make sure the buttons work correctly if the user is logged in or not
    class HomeButton(Button):
        def on_release(self):
            app = App.get_running_app()
            if app.current_org_type:
                if app.current_org_type == 'school':
                    komodoHubApp.sm.current = 'school'
                else:
                    komodoHubApp.sm.current = 'home'
            else:
                komodoHubApp.sm.current = 'login'

    class MessageButton(Button):
        def on_release(self):
            app = App.get_running_app()
            if app.current_org_type:
                komodoHubApp.sm.current = 'contacts'
            else:
                komodoHubApp.sm.current = 'login'



            # change the theme either light mode or dark mode

    class ThemeButton(Button):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.theme = 'light'  # this sets the default theme to light

            # layout and button
            self.layout = BoxLayout(orientation='vertical')
            self.toggle_button = Button(
                text='Switch to Dark Mode',
                size_hint=(1, 0.1),
                background_color=[0.9, 0.9, 0.9, 1],
                color=(0, 0, 0, 1)
            )
            self.toggle_button.bind(on_press=self.change_theme)

            self.layout.add_widget(self.toggle_button)
            self.add_widget(self.layout)

            with self.canvas.before:
                self.bg_color = Color(1, 1, 1, 1)
                self.bg_rect = RoundedRectangle(pos=self.pos, seze=self.size)

            self.bind(pos=self.update_rect, size=self.update_rect)

        def change_theme(self, instance):
            if self.theme == 'light':
                self.theme == 'dark'
                self.bg_color.rgba = (0.1, 0.1, 0.1, 1)
                self.toggle_button.background_color = (0.2, 0.2, 0.2, 1)
                self.toggle_button.color = (1, 1, 1, 1)
                self.toggle_button.text = 'Switch to Light Mode'
            else:
                self.theme = 'light'
                self.bg_color.rgba(1, 1, 1, 1)
                self.toggle_button.background_color = (0.9, 0.9, 0.9, 1)
                self.toggle_button.color = (0, 0, 0, 1)
                self.toggle_button.text = 'Switch to Dark Mode'

        def update_rect(self, *args):
            self.bg_rect.pos = self.pos
            self.bg_rect.size = self.size


class ProfilePicButton(ButtonBehavior, Image):
    def _init_(self, **kwargs):
        super()._init_(**kwargs)
        self.source = "Assets/ProfilePictures/Placeholder.png"

    def on_release(self):
        app = App.get_running_app()
        if app.current_org_type:
            komodoHubApp.sm.current = 'account_page'
        else:
            komodoHubApp.sm.current = 'login'

    def update_profilePic(self):
        self.source = "Assets/ProfilePictures/Profile1.jpg"
        self.reload()
    # self.image = Image(size_hint=(None, None), width=400, height=400)
    #  self.layout.add_widget(self.image)


class LoginScreen(BaseScreen):
    def validate_login(self):
        """
        Validate the user's login credentials.
        Takes in the username and password entered by the user.
        Checks if the username and password match a record in the database.
        If a match is found, the user is redirected to the appropriate screen based on their account type.
        """
        username = self.ids.username.text
        password = self.ids.password.text

        #updating profile pic upon login
        app = App.get_running_app()
        app.root.current = 'account_page'  #switcch screen

        #access the ProfilePicButton and update the image
        account_screen = app.root.get_screen('account_page')
        profile_pic = account_screen.ids.profile_pic
        profile_pic.update_profilePic()


        #PROFILE_PIC_PATH = "Assets/ProfilePictures/Profile1.png"
        # to be added to the login screen
      # self.profile_image = Image(size_hint=(None, None), width=400, height=400)
     #self.layout.add_widget(self.profile_image)

        # Check if the username and password match a record in the database
        result = database.get_user_info(username)
        # If a match for the username is found, check if the password is correct
        if result:
            stored_password, encrypted_aes, rsa_key, org_type, user_type, user_class, user_org = result
            encryptor = Encryption.HybridEncryptor(encrypted_aes, rsa_key)
            decrypted_password = encryptor.decrypt_aes(stored_password)

            if decrypted_password == password:
                app = App.get_running_app()
                app.current_org_type = org_type
                app.current_user = username
                app.current_user_type = user_type
                app.current_class = user_class
                if org_type == 'school':
                    komodoHubApp.sm.current = 'school'
                else:
                    komodoHubApp.sm.current = 'home'
            else:
                self.ids.login_message.text = "Incorrect password!"
        else:
            self.ids.login_message.text = "User not found!"

#if username exists, change the profile picture
            if result:
                if os.path.exists(PROFILE_PIC_PATH):
                    self.profile_image.source = PROFILE_PIC_PATH

class RegisterScreen(BaseScreen):
    def validate_register(self):
        """
        Validate the user's registration credentials.
        Takes in the unique code, username, password, and confirm password entered by the user.
        Checks if the unique code, username, and password match a record in the database.
        If a match is found, the user is redirected to the login screen.
        If the passwords do not match, or the password is less than 8 characters long, an error message is displayed.
        If the registration is successful, the user is redirected to the login screen.
        """
        unique_code = self.ids.unique_code.text
        username = self.ids.username.text
        password = self.ids.password.text
        confirm_password = self.ids.confirm_password.text

        # Check if the user has filled in all the required fields
        if not unique_code or not username or not password or not confirm_password:
            self.ids.register_message.text = "Please fill in all fields."
            return

        # Check if the password and confirm password match
        if password != confirm_password:
            self.ids.register_message.text = "Passwords do not match."
            return

        # Check if the password is at least 8 characters long
        if len(password) < 8:
            self.ids.register_message.text = "Password must be at least 8 characters long."
            return

        # Register the user in the database and redirect to the login screen if successful
        try:
            result = Account_Register.register(unique_code, username, password)
            self.ids.register_message.text = result
            self.ids.unique_code.text = ""
            self.ids.username.text = ""
            self.ids.password.text = ""
            self.ids.confirm_password.text = ""
            if result == "Registration successful!":
                komodoHubApp.sm.current = 'login'
        except Exception as e:
            self.ids.register_message.text = str(e)

class ChangePasswordScreen(Screen):
    def submit_password_change(self):
        username = self.ids.username.text
        current_password = self.ids.current_password.text
        new_password = self.ids.new_password.text
        confirm_new_password = self.ids.confirm_new_password.text

        if new_password != confirm_new_password:
            print("New passwords do not match")
            return

        message = change_password(username, current_password, new_password)
        print(message)

class OrganisationsScreen(BaseScreen):
    """
    Screen to display a list of organisations.
    The organisations are retrieved from the database and displayed as buttons.
    When a button is clicked, the user is redirected to the community posts screen for that organisation.
    """
    def on_enter(self):
        # Clear the organisation layout before adding new buttons
        org_layout = self.ids.org_layout
        org_layout.clear_widgets()

        # Retrieve the list of organisations from the database
        organisations = database.get_organisations()

        # Create a button for each organisation and bind the on_release event
        for org in organisations:
            org_name = org[0]
            btn = Button(text=org_name, size_hint_y=None, height=40)
            btn.bind(on_release=lambda btn: self.on_release(btn.text))
            org_layout.add_widget(btn)

    # Redirect to the community posts screen for the selected organisation
    def on_release(self, org_name):
        if(database.get_org_type(org_name) != "school"):
            app = App.get_running_app()
            app.current_org = org_name
            komodoHubApp.sm.current = 'community_posts'



class LibraryScreen(BaseScreen):
    def on_enter(self):
        # Clear the organisation layout before adding new buttons
        org_layout = self.ids.org_layout
        org_layout.clear_widgets()

        # Retrieve the list of organisations from the database
        libraries = database.get_libraries()

        # Create a button for each organisation and bind the on_release event
        for org in libraries:
            org_name = org[0]
            btn = Button(text=org_name, size_hint_y=None, height=40)
            btn.bind(on_release=lambda btn: self.on_release(btn.text))
            org_layout.add_widget(btn)

    # Redirect to the community posts screen for the selected organisation
    def on_release(self, org_name):
        app = App.get_running_app()
        app.current_org = org_name
        komodoHubApp.sm.current = 'library_posts'

class LibraryPostsScreen(BaseScreen):
    """
    Screen to display a list of library posts.
    The posts are retrieved from the database and displayed as widgets.
    If an image is present, it is displayed in the widget.
    """
    def on_enter(self):
        # Call the function to display library posts
        self.display_library_posts()

    def display_library_posts(self):
        # Retrieve the layout where posts will be displayed
        posts_layout = self.ids.posts_layout
        posts_layout.clear_widgets()

        app = App.get_running_app()
        org_id = database.get_org_id(app.current_org)
        posts = database.get_library_posts(org_id)

        # Loop through the posts and create widgets to display them
        for post in posts:
            post_title, post_content, post_image = post

            # Create a BoxLayout for each post to contain the title, content, and image
            post_box = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(250))  # Increased height

            # Title label
            title_label = Label(
                text=post_title,
                size_hint_y=None,
                height=dp(40),
                font_size='18sp',
                bold=True
            )

            # Content label
            content_label = Label(
                text=post_content,
                size_hint_y=None,
                height=dp(80),
                font_size='14sp',
                text_size=(self.width * 0.8, None),
                halign='left',
                valign='top'
            )

            # Image handling
            image_widget = Image(
                size_hint=(None, None),
                size=(dp(150), dp(150)),
                allow_stretch=True,
                keep_ratio=True,
                pos_hint={'center_x': 0.5}
            )

            post_box.add_widget(title_label)

            # Check if there's a valid image path
            if post_image and os.path.exists(post_image):
                image_widget.source = post_image
                post_box.add_widget(image_widget)

            post_box.add_widget(content_label)

            posts_layout.add_widget(post_box)

class MessageScreen(BaseScreen):
    """
    Screen to display messages between two users.
    The messages are retrieved from the database and displayed as labels.
    """
    def on_enter(self):
        # When the screen is entered, display the messages
        self.display_messages()

    def display_messages(self):
        # Clear the messages box before adding new messages
        app = App.get_running_app()
        messages_box = self.ids.messages_box
        messages_box.clear_widgets()

        # Retrieve the messages from the database
        messages = database.get_messages(app.current_user, app.current_contact)

        # Create a label for each message
        for message in messages:
            sender, receiver, content, time, encrypted_aes = message

            # Decrypt the message
            rsa_key = database.get_user_info(receiver)[2]
            encryptor = Encryption.HybridEncryptor(encrypted_aes, rsa_key)
            decrypted_content = encryptor.decrypt_aes(content)

            # Combine time, sender, and message content into a single Label using markup
            message_text = (
                f"[size=16][b]{sender}[/b][/size] [size=12]{time}[/size]\n"  # Bold username and smaller time
                f"{decrypted_content}"  # Message content
            )

            # Create a Label for the message
            # Allow text to wrap and markup which allows for bold and size manipulation
            message_label = Label(
                text=message_text,
                size_hint_y=None,
                height=dp(60),
                halign='left',
                valign='top',
                font_size='14sp',
                text_size=(self.width * 0.8, None),
                padding=[dp(10), dp(5)],
                markup=True
            )

            # Adjust alignment and text color based on the sender
            if sender == app.current_user:
                # Align to the right for the current user
                message_label.halign = 'right'
                message_label.color = (0, 0.5, 0, 1)  # Dark green for current user
            else:
                # Align to the left for the contact
                message_label.halign = 'left'
                message_label.color = (0.8, 0.8, 0.8, 1)  # Light gray for contact

            # Add the message label to the messages_box
            messages_box.add_widget(message_label)

        # Scroll to the bottom of the messages box
        self.ids.messages_layout.scroll_to(messages_box.children[0])

    def send_message(self):
        """
        Send a message to the current contact.
        The message is encrypted using AES and RSA.
        """
        app = App.get_running_app()

        # Get the message from the input field
        message = self.ids.message_input.text.strip()
        # Clear the input field
        self.ids.message_input.text = ''

        # Check if the message is not empty
        if message:
            # Encrypt the message
            rsa_key = database.execute_query("SELECT rsa_key FROM user_info WHERE username = ?", (app.current_contact,), fetch_one=True)
            encryptor = Encryption.HybridEncryptor(None, rsa_key[0])
            encrypted_message, encrypted_aes, rsa_key = encryptor.encrypt_aes(message)
            # Insert the message into the database using the function from database.py
            database.insert_message(app.current_user, app.current_contact, encrypted_message, encrypted_aes)

            # Refresh the messages
            self.display_messages()


class ContactsScreen(BaseScreen):
    """
    Screen to display a list of contacts that the user has messaged.
    The contacts are retrieved from the database and displayed as buttons.
    Optionally, a new contact can be added.
    """
    def on_enter(self):
        app = App.get_running_app()
        contacts_layout = self.ids.contacts_layout
        contacts_layout.clear_widgets()

        # Retrieve the contacts from the database
        contacts = database.get_contacts(app.current_user)

        # Create a button for each contact
        for contact in contacts:
            contact_name = contact[0]
            btn = Button(text=contact_name, size_hint_y=None, height=40)
            btn.bind(on_release=lambda btn, name=contact_name: self.continue_messaging(name))
            contacts_layout.add_widget(btn)

    def continue_messaging(self, contact_name):
        """
        Change the current screen to the message screen for the selected contact.
        """
        app = App.get_running_app()
        app.current_contact = contact_name
        komodoHubApp.sm.current = 'messages'

    def start_messaging(self):
        """
        Change the current screen to the message screen with a new contact.
        Checks if the contact exists in the database.
        Makes sure the contact is of the same type as the current user.
        """
        app = App.get_running_app()

        # Get the new contact from the input field
        new_contact = self.ids.new_user_input.text.strip()

        # Clear the input field and error message
        self.ids.new_user_input.text = ''
        self.ids.user_error_message.text = ''

        # Check if new contact is empty
        if new_contact:
            result = database.execute_query("SELECT username, org_type FROM user_info WHERE username = ?", (new_contact,), fetch_one=True)
            # Check if the contact exists
            if result:
                # Check if the contact is of the same type as the current user
                if app.current_org_type != result[1]:
                    self.ids.user_error_message.text = 'You cannot message a ' + result[1] + ' account.'
                else:
                    if app.current_user_type == 'teacher':
                        if new_contact not in database.get_students(app.current_user) or new_contact not in database.get_org_admins(app.current_user):
                            self.ids.user_error_message.text = 'This student is not in your class.'
                    if app.current_user_type == 'standard':
                        if new_contact not in database.get_teacher(app.current_user):
                            self.ids.user_error_message.text = 'This teacher is not in your class.'
                    app.current_contact = new_contact
                    komodoHubApp.sm.current = 'messages'
            else:
                self.ids.user_error_message.text = 'User not found!'


class ReportScreen(BaseScreen):


    def open_popup(self):
        # FileChooser in Popup
        file_chooser = FileChooserListView()
        popup_layout = BoxLayout(orientation="vertical")
        popup_layout.add_widget(file_chooser)

        close_button = Button(text="Close", size_hint_y=0.1)
        close_button.bind(on_release=lambda x: self.popup.dismiss())
        popup_layout.add_widget(close_button)

        self.popup = Popup(title="Upload File", content=popup_layout, size_hint=(0.9, 0.9))
        self.popup.open()


class SchoolScreen(BaseScreen):
    pass

class Posts(RecycleView):
        """
        The recycleview that displays the posts that users make in the school content and home page
        """
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            app = App.get_running_app()
            self.data = []
            self.refresh_from_data()


        def reload(self):
            app = App.get_running_app()
            if(app.current_org_type == "school"):
                org_id = database.get_user_org(app.current_user)
            else:
                org_id = database.get_org_id(app.current_org)[0]
            #print(org_id)
            newData = database.get_community_posts(org_id)
            self.data = []
            if newData:
                for i in newData[::-1]:
                    self.data.append({"username": i[0], "message": i[1]})
            self.refresh_from_data()

class Post(BoxLayout, RecycleDataViewBehavior):
    """
    The standard structure for posts uses stringproperties to have the user change the text
    """
    username = StringProperty()
    profilePicture = StringProperty()
    message = StringProperty()

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        return super().refresh_view_attrs(rv, index, data)

class ClassContentScreen(BaseScreen):
    def on_pre_enter(self, *args):
        self.ids.schlPosts.reload()
        return super().on_enter(*args)

class SchoolAssignmentsScreen(BaseScreen):
    def on_enter(self):
        """
        Screen to load list of assignments for user's class
        """
        app = App.get_running_app()
        user_class = app.current_class
        self.display_assignments(user_class)

    def display_assignments(self, class_id):
        #display assignments from database
        app = App.get_running_app()
        assignments = database.get_class_assignments(class_id)

        assignments_layout = self.ids.assignment_layout
        assignments_layout.clear_widgets() #clear previous assignments


        for assignment in assignments:
            assignment_id, content, creator, classid, deadline, title = assignment

            #Bold the variable names & have assignment_id and classid on the same line
            assignment_text = f"[b]ID:[/b] {assignment_id}  |  [b]Class:[/b] {classid}\n[b]Content:[/b] {content}\n[b]Deadline:[/b] {deadline}"

            assignment_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))

            #Create a Button for assignments in order to be able to submit work
            #markup allows for Bold feature of texts
            assignment_button = Button(
                text = assignment_text,
                size_hint_y = None,
                size_hint_x=None,
                height = dp(70),
                width = dp(530),
                markup = True,
                on_release = lambda assignment_button, a=assignment: self.open_assignment_details(a)
            )

            assignment_box.add_widget(assignment_button)

            if app.current_user_type == 'teacher':
                #Create a button in order to be able to delete assignments
                assignment_deletion = Button(
                    text = 'Delete',
                    size_hint_y = None,
                    size_hint_x=None,
                    height = dp(70),
                    width = dp(50),
                    on_release = lambda assignment_deletion, a=assignment: self.delete_assignment(a)
                )

                #Create a button in order to change screens to grading assignments screen
                assignment_grading = Button(
                    text = 'Grade',
                    size_hint_y = None,
                    size_hint_x=None,
                    height = dp(70),
                    width = dp(50),
                    on_release = lambda assignment_grading, a=assignment: self.open_grading_screen(a)
                )

                #Add assignment, deletion and grading button to the assignment horizontal layout

                assignment_box.add_widget(assignment_deletion)
                assignment_box.add_widget(assignment_grading)

            #Add assignments horizontal button layout to assignments_list
            assignments_layout.add_widget(assignment_box)


    def open_assignment_details(self, assignment):
        """
        Retreieve assignment details
        """
        app = App.get_running_app()
        app.assignment_data = assignment
        app.root.current = 'assignment_details'

    def delete_assignment(self, assignment_id):
        """
        Delete any assignment created
        """
        app = App.get_running_app()

        #calls the database function delete_assignment to delete an assignment created using the id
        database.delete_assignment(assignment_id)

        #refresh assignment list
        self.display_assignments(app.current_class)

        app.root.current = 'school_assignments'

    def open_grading_screen(self, assignment):
        """
        Open the AssignmentGradingScreen by clicking the button
        """
        app = App.get_running_app()
        app.assignment_data = assignment
        app.root.current = 'grade_assignment'

class AssignmentSubmissionScreen(BaseScreen):
    """
    Screen where user can submit assignments
    """
    def on_enter(self):
        #load selected assignment details
        app = App.get_running_app()
        assignment_id, content, creator, classid, deadline = app.assignment_data

        self.ids.assignment_title.text = f"Assignment {assignment_id}"
        self.ids.assignment_content.text = f"Content {content}"
        self.ids.assignment_deadline.text = f"Deadline {deadline}"

    def submit_assignment(self, assignment_id=None):
        #where user can submit assignment
        submission_content = self.ids.submission_content.text.strip() #strip() is used to make sure an empty submission isn't made
        app = App.get_running_app()

        database.get_assignment_id() #getting the assignment id
        submission_creator = app.current_user #get current users name

        if submission_content:

            #calls the database function insert_submission to save the submission information
            database.insert_submission(assignment_id, submission_creator, submission_content)

            print("Submission made successfully")

            #clear input field so if user wants to make another submission the field is empty
            self.ids.submission_content.text = ""

        else:
            print("Please enter a submission")



class AddAssignmentScreen(BaseScreen):
    """
    Screen where user can create assignments
    """
    def create_assignment(self):
        content = self.ids.assignment_content.text
        deadline = self.ids.assignment_deadline.text
        title = self.ids.assignment_title.text
        time = self.ids.assignment_time.text
        app = App.get_running_app()
        current_user = app.current_user
        class_id = app.current_class

        if content and deadline and title and time:
            database.insert_assignments(content, deadline, title, time, current_user, class_id)
            print("Assignment added successfully!")

            #clear input fields so if user wants to add another assignment the field is empty
            self.ids.assignment_content.text = ""
            self.ids.assignment_deadline.text = ""
            self.ids.assignment_title.text = ""
            self.ids.assignment_time.text = ""

            # Navigate back to the assignments screen
            App.get_running_app().root.current = "school_assignments"

        else:
            print("Please fill in all fields.")

class AssignmentGradingScreen(BaseScreen):

    def submit_grading(self):
        #where teachers can submit grades for work submissions

        grade = self.ids.assignment_grade.text.strip() #no empty value entered
        feedback = self.ids.assignment_feedback.text.strip()  # no empty value entered
        app = App.get_running_app()

        database.get_assignment_id()

        if grade and feedback:
            database.insert_feedback(grade, feedback)

            self.ids.assignment_grade.text = ""
            self.ids.assignment_feedback.text = ""

            print("Grading submitted successfully")

        else:
            print("Please enter a grade and feedback")



class CommunityPostsScreen(BaseScreen):
    def on_pre_enter(self, *args):
        self.ids.commPosts.reload()
        return super().on_enter(*args)

class CommunityCreatePostScreen(BaseScreen):
    def create_post(self, text):
        if len(text) > 0:
            app = App.get_running_app()
            if(app.current_org_type == "school"):
                org_id = database.get_user_org(app.current_user)
            else:
                org_id = database.get_org_id(app.current_org)[0]

            print(org_id, text, app.current_user)

            database.insert_community_post(org_id, text, app.current_user)

            if(app.current_org_type == "school"):
                komodoHubApp.sm.current = 'school_content'
            else:
                komodoHubApp.sm.current = 'community_posts'

    def decide_post_return(self):
        app = App.get_running_app()
        if(app.current_org_type == "school"):
            komodoHubApp.sm.current = 'school_content'
        else:
            komodoHubApp.sm.current = 'community_posts'


class SchoolGameScreen(BaseScreen):
    pass

class AccountPage(BaseScreen):
    def log_out(self):
        app = App.get_running_app()
        komodoHubApp.sm.current = 'login'
        app.current_user = None
        app.current_org_type = None
        app.current_class = None
        app.current_user_type = None


class HomeScreen(BaseScreen):
    pass

class BackArrow(Button):
    pass
"""
Organisation management screen
User management screen
Content management screen
Permissions management screen
Dashboard screen
School management screen
"""

class KomodoHubApp(App):
    def build(self):
        self.sm = ScreenManager()
        self.current_org_type = None
        self.current_org = None
        self.current_user = None
        self.current_user_type = None
        self.current_class = None

        self.sm.add_widget(LoginScreen(name="login"))
        self.sm.add_widget(RegisterScreen(name="register"))
        self.sm.add_widget(HomeScreen(name="home"))
        self.sm.add_widget(ReportScreen(name="report"))

        self.sm.add_widget(LibraryScreen(name="library"))
        self.sm.add_widget(LibraryPostsScreen(name="library_posts"))

        self.sm.add_widget(SchoolScreen(name="school"))
        self.sm.add_widget(ClassContentScreen(name="school_content"))
        self.sm.add_widget(SchoolGameScreen(name="school_game"))

        self.sm.add_widget(SchoolAssignmentsScreen(name="school_assignments"))
        self.sm.add_widget(AddAssignmentScreen(name="add_assignment"))
        self.sm.add_widget(AssignmentSubmissionScreen(name="submit_assignment"))
        self.sm.add_widget(AssignmentGradingScreen(name="grade_assignment"))

        self.sm.add_widget(OrganisationsScreen(name='organisations'))
        self.sm.add_widget(CommunityPostsScreen(name='community_posts'))
        self.sm.add_widget(CommunityCreatePostScreen(name='community_create_post'))

        self.sm.add_widget(AccountPage(name="account_page"))

        self.sm.add_widget(ContactsScreen(name="contacts"))
        self.sm.add_widget(MessageScreen(name="messages"))

        return self.sm

if __name__ == "__main__":
    komodoHubApp = KomodoHubApp()
    komodoHubApp.run()
