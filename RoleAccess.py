#Role based access control
#assigning different roles and permissions to different users
#umight need to advance this code and use flask and SQLAlchemy

class role_based_access_control:
    def _init_(self):    #defining the different roles and their permissions 
        self.roles = {
            "student":{"access personal account", "message teachers", "play games", "access enrolled programs",
            "submit assignments"},
            "teacher":{"access personal account", "edit content", "manage content", "message students", "access student contributions"},
            "principle": {"access student data", "access admin account"},
            "school admin": {"access admin account", "access business dashboard"},
            "community": {"access personal account", "access Komodo Hub library", "access programs", "access and edit their contribution pages"}
        }
        self.user_roles = {} #stores data of users and their roles
       
    def assign_role(self, user, role):      #assigning the role to each user
        self.user = user     
        self.user_roles[user] = role

    def user_has_permission(self, user, permission):           #giving permission to each user
        role = self.user_roles.get(user)
        return permission in self.roles.get(role, set())

#examples to use
role_access = role_based_access_control()
role_access.assign_role("Gloria", "student")
