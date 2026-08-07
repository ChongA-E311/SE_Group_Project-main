from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.lang import Builder
from kivy.uix.behaviors import ButtonBehavior, FocusBehavior
from kivy.properties import StringProperty, BooleanProperty, ListProperty, StringProperty, ObjectProperty, NumericProperty
from kivy.uix.recyclegridlayout import RecycleGridLayout
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.metrics import dp
from kivy.uix.popup import Popup
import os
import sqlite3
import Encryption
import database
import Account_Register
import UniqueCodedGenerator

#Fetch user_info and organisations table
connection = sqlite3.connect("project_database.db")
cursor = connection.cursor()
cursor.execute("SELECT user_id, username, user_org, user_class, password FROM user_info")
loaded_db_rows = cursor.fetchall()
cursor.execute("SELECT * FROM organisations")
loaded_org_rows = cursor.fetchall()

# Load all .kv files from the UI_Menus directory
for file in os.listdir("UI_Menus"):
    if file.endswith(".kv"):
        with open(os.path.join("UI_Menus", file), encoding="utf-8") as f:
            Builder.load_string(f.read())

class AdminBaseScreen(Screen):
    def on_enter(self):
        app = App.get_running_app()
        if app.current_user_type == "komodo_admin":    #Change this to komodo_admin after login fix
            self.ids.org_button.opacity = 1
            self.ids.org_button.disabled = False
        if app.current_user_type in ["komodo_admin", "org_admin", "org_leader"]:
            self.ids.dashboard_button.opacity = 1
            self.ids.dashboard_button.disabled = False
        else:
            self.ids.dashboard_button.opacity = 0
            self.ids.dashboard_button.disabled = True
            self.ids.org_button.opacity = 0
            self.ids.org_button.disabled = True

    class OrgButton(Button):
        def on_release(self):
            app = App.get_running_app()
            if app.current_user_type not in ["org_admin", "komodo_admin"]:
                return
            else:
                komodoHubAppAdmin.sm.current = 'org_admin'

    class DashboardButton(Button):
        def on_release(self):
            app = App.get_running_app()
            if app.current_user_type not in ["org_admin", "komodo_admin", "org_leader"]:
                return
            else:
                komodoHubAppAdmin.sm.current = 'AdminDash'


class TextInputPopup(Popup): #For user edit
    """ Edit name popup """
    obj = ObjectProperty()
    obj_text = StringProperty()
    obj_id = NumericProperty()

    def __init__(self, obj, **kwargs):
        super(TextInputPopup, self).__init__(**kwargs)
        self.obj = obj
        self.obj_text = obj.text

class OrgInputPopup(Popup): #For Org edit
    def __init__(self, parent, **kwargs):
        super(OrgInputPopup, self).__init__(**kwargs)
        self.obj = parent

        #Creates structure of popup
        layout = BoxLayout(orientation='vertical')
        self.idinput = TextInput(hint_text="Enter Organization New ID")
        layout.add_widget(self.idinput)
        self.nameinput = TextInput(hint_text="Enter New Organization Name")
        layout.add_widget(self.nameinput)
        self.typeinput = TextInput(hint_text="Enter New Organization Type")
        layout.add_widget(self.typeinput)
        confirm_button = Button(text='Confirm')
        confirm_button.bind(on_release=self.on_confirm)
        layout.add_widget(confirm_button)
        cancel_button = Button(text='Cancel')
        cancel_button.bind(on_release=self.dismiss)
        layout.add_widget(cancel_button)

        self.content = layout

    def on_confirm(self, instance):
        """ Handle confirmation: Collect text input and update changes """
        org_id = self.idinput.text
        org_name = self.nameinput.text
        org_type = self.typeinput.text

        #Prevent unknown type
        if org_type in ['school', 'community', 'komodo']:
            self.obj.add_changes(org_id, org_name, org_type)
        else:
            print("Cannot add org type") # better error handling [fix]

        self.dismiss()

class SelectableRecycleGridLayout(FocusBehavior, LayoutSelectionBehavior, RecycleGridLayout):
    ''' Adds selection and focus behaviour to the view. '''


class UserSelectableButton(RecycleDataViewBehavior, Button):
    """Button with selection support and password reset confirmation"""
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)
    r_v = None

    def refresh_view_attrs(self, rv, index, data):
        """Handle view changes"""
        self.index = index
        self.r_v = rv
        return super().refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        """Handle touch selection"""
        if super().on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        """Respond to selection changes"""
        self.selected = is_selected

    def on_press(self):
        """Handle button press based on column"""
        column_index = self.index % 6

        if column_index == 2:
            self.change_user_type()
        elif column_index == 5:
            self.show_reset_confirmation()

    def change_user_type(self):
        app = App.get_running_app()
        row_index = self.index // 6
        target_user_type = self.r_v.data[row_index * 6 + 2]['text']
        current_user_type = app.current_user_type
        is_school_org = getattr(app, 'current_org_type', None) == 'school'

        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text=f"Change role for user:"))
        content.add_widget(Label(text=f"Current: {target_user_type}"))

        btn_box = BoxLayout(spacing=5, size_hint_y=None, height=50)

        self._promotion_popup = Popup(
            title="Change User Role",
            content=content,
            size_hint=(0.7, 0.4)) # Slightly wider for longer button text

        # Komodo Admin options
        if current_user_type == 'komodo_admin':
        # Promotion options
            if target_user_type != 'org_leader':
                btn_box.add_widget(Button(
                text="Org Leader",
                on_press=lambda x: self.update_user_type('org_leader')
        ))
        if target_user_type != 'org_admin':
            btn_box.add_widget(Button(
                text="Org Admin",
                on_press=lambda x: self.update_user_type('org_admin')
            ))

        # Demotion options
        if target_user_type != 'standard':
            btn_box.add_widget(Button(
                text="Standard",
                on_press=lambda x: self.update_user_type('standard'),
                background_color=(0.8, 0.2, 0.2, 1)
            ))


        if is_school_org:
            if target_user_type != 'teacher':
                btn_box.add_widget(Button(
                    text="Make Teacher",
                    on_press=lambda x: self.update_user_type('teacher')
        ))


        elif current_user_type == 'org_admin':

            if is_school_org:
                if target_user_type != 'teacher':
                    btn_box.add_widget(Button(
                        text="Make Teacher",
                        on_press=lambda x: self.update_user_type('teacher')
            ))


        btn_box.add_widget(Button(
            text="Cancel",
            on_press=lambda x: self._promotion_popup.dismiss()
        ))

        if len(btn_box.children) > 1:
            content.add_widget(btn_box)
        self._promotion_popup.open()


    def update_user_type(self, new_type):
        row_index = self.index // 6
        user_id = self.r_v.data[row_index * 6]['text']
        username = self.r_v.data[row_index * 6 + 1]['text']
        current_type = self.r_v.data[row_index * 6 + 2]['text']
        app = App.get_running_app()


        if (app.current_user_type == 'org_admin' and
                current_type in ['org_leader', 'org_admin']):
            return

        database.update_user_type(user_id, new_type)
        users_screen = app.root.get_screen('AdminDash')
        users_screen.refresh_users()
        self._promotion_popup.dismiss()

    def show_reset_confirmation(self):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text="Are you sure you want to reset\nthis user's password?"))

        btn_box = BoxLayout(spacing=5, size_hint_y=0.4)
        btn_box.add_widget(Button(text="Cancel", on_press=lambda x: self.popup.dismiss()))

        confirm_btn = Button(text="Confirm", background_color=(0.8, 0.2, 0.2, 1))
        confirm_btn.bind(on_press=lambda x: self.execute_password_reset())
        btn_box.add_widget(confirm_btn)

        content.add_widget(btn_box)

        self.popup = Popup(title="Confirm Password Reset",
                      content=content,
                      size_hint=(0.6, 0.3))
        self.popup.open()

    def execute_password_reset(self):
        row_index = self.index // 6
        username = self.r_v.data[row_index * 6 + 1]['text']
        encrypted_aes, rsa_key = database.get_encryption_keys(username)
        encryptor = Encryption.HybridEncryptor(encrypted_aes, rsa_key)
        password, encrypted_aes, rsa_key = encryptor.encrypt_aes("password")
        database.reset_password(username, password)

        self.popup.dismiss()

class OrgSelectableButton(RecycleDataViewBehavior, Button): #For org dashoard
    """ Add selection support to the Button """
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty()
    r_v = None

    def refresh_view_attrs(self, rv, index, data):
        """ Catch and handle the view changes """
        self.index = index
        self.r_v = rv
        return super(OrgSelectableButton, self).refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        """ Add selection on touch down """
        if super(OrgSelectableButton, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        """ Respond to the selection of items in the view. """
        self.selected = is_selected

    def on_press(self):
        """ user pressed edit button """
        pass

    def update_changes(self, idx, txt):
        pass

class LoginScreen(AdminBaseScreen):
    def validate_login(self):
        """
        Validate the user's login credentials.
        Takes in the username and password entered by the user.
        Checks if the username and password match a record in the database.
        If a match is found, the user is redirected to the appropriate screen based on their account type.
        """
        username = self.ids.username.text
        password = self.ids.password.text

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
                app.current_org = user_org
                if user_type in ['org_leader', 'org_admin', 'komodo_admin']:
                    komodoHubAppAdmin.sm.current = 'AdminDash'
                else:
                    self.ids.login_message.text = "Admin only access!"
            else:
                self.ids.login_message.text = "Incorrect password!"
        else:
            self.ids.login_message.text = "User not found!"

class RegisterScreen(AdminBaseScreen):
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
                komodoHubAppAdmin.sm.current = 'login'
        except Exception as e:
            self.ids.register_message.text = str(e)


class UsersConsole(AdminBaseScreen, BoxLayout):
    """ RecycleView with 6 columns """
    data_items = ListProperty([])

    def __init__(self, **kwargs):
        """ Initialize RecycleView """
        super(UsersConsole, self).__init__(**kwargs)
        self.get_users()

    def on_pre_enter(self, *args):
        """ Called before the screen is displayed """
        super(UsersConsole, self).on_pre_enter(*args)  # Maintain parent class functionality
        self.refresh_users()

    def refresh_users(self):
        """ Clear and reload user data """
        self.data_items = []
        self.get_users()

    def get_users(self):
        """ Load user data into data_items with 6 columns """
        app = App.get_running_app()

        # Get appropriate user data based on permissions
        if app.current_user_type == 'komodo_admin':
            loaded_db_rows = database.get_all_users()
        else:
            loaded_db_rows = database.get_org_users(app.current_org)

        # Process each row - now expecting 6 columns
        for row in loaded_db_rows:
            for index, col in enumerate(row):
                if index == 4:  # Password column is now index 5 (6th column)
                    self.data_items.append(col)
                    self.data_items.append('reset')
                else:
                    self.data_items.append(col)

    def show_code_popup(self):
        """Show code generation dialog with proper permissions"""
        app = App.get_running_app()

        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self._code_popup = Popup(
            title="Generate Access Codes",
            content=content,
            size_hint=(0.8, 0.6))

        # Amount input
        content.add_widget(Label(text="Number of codes to generate:"))
        amount_input = TextInput(multiline=False)
        content.add_widget(amount_input)

        # Org selection (only for komodo_admins)
        if app.current_user_type == 'komodo_admin':
            content.add_widget(Label(text="Organization ID:"))
            org_input = TextInput(multiline=False)
            content.add_widget(org_input)
        else:
            org_input = None  # Will use current org

        # Class selection (only for school orgs)
        if getattr(app, 'current_org_type', None) == 'school':
            content.add_widget(Label(text="Class ID (leave blank for org-wide):"))
            class_input = TextInput(multiline=False)
            content.add_widget(class_input)
        else:
            class_input = None

        # Generate button
        btn_generate = Button(
            text="Generate Codes",
            size_hint_y=None,
            height=50,
            on_press=lambda x: self.execute_code_generation(
                amount_input.text,
                org_input.text if org_input else app.current_org,
                class_input.text if class_input else None
            )
        )
        content.add_widget(btn_generate)

        # Cancel button
        btn_cancel = Button(
            text="Cancel",
            size_hint_y=None,
            height=40,
            on_press=lambda x: self._code_popup.dismiss()
        )
        content.add_widget(btn_cancel)

        self._code_popup.open()

    def execute_code_generation(self, amount_str, org_id, class_id=None):
        """Handle the code generation process"""
        try:
            amount = int(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            App.get_running_app().show_toast("Please enter a valid number")
            return

        # Validate org_id for non-komodo admins
        app = App.get_running_app()
        if app.current_user_type != 'komodo_admin' and org_id != app.current_org:
            app.show_toast("Cannot generate codes for other organizations")
            return

        # Generate codes
        generated_codes = UniqueCodedGenerator.generate_code(amount, org_id, class_id)
        print("Generated codes:", generated_codes)

        # Close the generation popup
        self._code_popup.dismiss()

class OrgConsole(AdminBaseScreen, BoxLayout):
    data_items = ListProperty([])

    def __init__(self, **kwargs):
        """ init RV """
        super(OrgConsole, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.get_org()
        self.add_new_org()

    def on_pre_enter(self, *args):
        """ Called before the screen is displayed """
        super(OrgConsole, self).on_pre_enter(*args)  # Maintain parent class functionality
        self.refresh_org()

    def refresh_org(self):
        """ Clear and reload user data """
        self.data_items = []
        self.get_org()

    def get_org(self):
        loaded_org_rows = database.get_org_rows()
        for row in loaded_org_rows:
            for col in row:
                self.data_items.append(col)

    def add_new_org(self):
        btn = Button(text="Add New organization",
                     size_hint_y=None,
                     height=40,
                     padding=[10, 20])
        btn.pos_hint = {'center_x': 0.5, 'center_y': 0.12}
        btn.bind(on_press=self.open_popup)
        self.add_widget(btn)

    def open_popup(self, instance):
        popup = OrgInputPopup(self)
        popup.open()

    def add_changes(self, org_id, org_name, org_type):
        if org_type in ['school', 'community', 'komodo']:
            cursor.execute(f"INSERT INTO organisations (org_id, org_name, org_type) VALUES ('{org_id}', '{org_name}', '{org_type}')")
            connection.commit()
            self.data_items.append(org_id)
            self.data_items.append(org_name)
            self.data_items.append(org_type)

        else:
            print("Org type error")

class KomodoHubAppAdmin(App):
    def build(self):
        self.sm = ScreenManager()
        self.current_org_type = None
        self.current_org = None
        self.current_user = None
        self.current_user_type = None
        self.sm.add_widget(LoginScreen(name="login"))
        self.sm.add_widget(UsersConsole(name="AdminDash"))
        self.sm.add_widget(OrgConsole(name="org_admin"))
        self.sm.add_widget(RegisterScreen(name="register"))
        return self.sm

if __name__ == "__main__":
    komodoHubAppAdmin = KomodoHubAppAdmin()
    komodoHubAppAdmin.run()


