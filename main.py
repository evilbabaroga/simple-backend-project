from enum import Enum

MIN_PASS_LEN = 16
MAX_PASS_LEN = 40

MIN_USER_LEN = 3
MAX_USER_LEN = 40

USERS_FROM_FILE = []
READ_FILE = []

try:
    with open('users', 'r') as f:
        READ_FILE = f.readlines()
except FileNotFoundError:
    with open('users', 'w') as f:
        f.write('')

try:
    USERS_FROM_FILE = [_.split(',') for _ in READ_FILE[0].split()]
except IndexError:
    READ_FILE = ['']
print(READ_FILE)
print(USERS_FROM_FILE)

class Stack():
    def __init__(self, size=10):
        self.array = [None] * size
        self.top = -1

    def push(self, item):
        if self.top < len(self.array) - 1:
            self.array[self.top + 1] = item
            self.top += 1
        else:
            print("Stack overflow, can't push.")

    def peek(self):
        if self.top == -1:
            print("Stack empty, can't peek.")
        else:
            return self.array[self.top]

    def pop(self):
        if self.top >= 0:
            removed_item = self.array[self.top]
            self.top -= 1
            return removed_item
        else:
            print("Stack empty, can't pop.")

    def is_empty(self):
        return self.top == -1

class Mode(Enum):
    CHOOSE_SERVICE = 0
    LOGIN = 1
    SIGN_UP = 2
    CHOOSE_SERVICE_LOGGED_IN = 3
    CHANGE_PASSWORD = 4

class User:
    def __init__(self, username, password):
        self._username = username
        self.__password = password

    def check_password(self, password):
        return password == self.__password

    def get_username(self):
        return self._username

    def change_password(self, new_password):
        self.__password = new_password

class System:
    def __init__(self):
        self.users = dict()
        self.file_format = READ_FILE[0]
        for user in USERS_FROM_FILE:
            username = user[0]
            password = user[1]
            self.users[username] = User(username, password)
        self.mode = stack()
        self.mode.push(Mode.CHOOSE_SERVICE)
        self.logged_in_user = None
        self.run()

    def run(self):
        while True:
            if self.mode == Mode.CHOOSE_SERVICE:
                self.mode = self.choose_service()
            if self.mode == Mode.SIGN_UP:
                self.mode = self.sign_up()
            if self.mode == Mode.LOGIN:
                self.mode = self.log_in()
            if self.mode == Mode.CHOOSE_SERVICE_LOGGED_IN:
                self.mode = self.choose_service_logged_in()
            if self.mode == Mode.CHANGE_PASSWORD:
                self.mode = self.change_user_password()

    def choose_service(self):
        service = input("Enter 'login' for logging in, 'signup' for signing up: ").lower()
        if service == 'login':
            return Mode.LOGIN
        if service == 'signup':
            return Mode.SIGN_UP
        return Mode.CHOOSE_SERVICE

    def sign_up(self):
        username = self.username_input()
        password = self.password_input()
        self.users[username] = User(username, password)
        self.write_user_to_file(username, password)
        print('Success!')
        return Mode.CHOOSE_SERVICE

    def write_user_to_file(self, username, password):
        self.file_format += f"{' ' if len(self.file_format) > 0 else ''}{username},{password}"
        with open('users', 'w') as f:
            f.write(self.file_format)

    def rewrite_changed_password_to_file(self, username, old_password, new_password):
            print(f"{username},{old_password}", f"{username},{new_password}")
            self.file_format = self.file_format.replace(f"{username},{old_password}", f"{username},{new_password}")
            with open('users', 'w') as f:
                f.write(self.file_format)

    def log_in(self):
        username = self.enter_username()
        if username not in self.users:
            if username.lower() == 'q':
                return Mode.CHOOSE_SERVICE
            print("User doesn't exist. Try again or enter 'q' to go back.")
            return self.mode
        count = 3
        password = self.enter_password()
        while count > 0:
            if not self.users[username].check_password(password):
                print(f"Wrong password. {count} {'tries' if count > 1 else 'try'} left.")
                password = self.enter_password()
                count -= 1
            if self.users[username].check_password(password):
                self.logged_in_user = self.users[username]
                return Mode.CHOOSE_SERVICE_LOGGED_IN
        print("Login failed.")
        return self.mode

    def choose_service_logged_in(self):
        service = input(f"Welcome {self.logged_in_user.get_username()}. Type 'pass' to change password or 'logout' to log out: ").lower()
        if service == 'pass':
            return Mode.CHANGE_PASSWORD
        if service == 'logout':
            return Mode.CHOOSE_SERVICE
        return self.mode

    def change_user_password(self):
        old_password = input("Enter old password: ")
        if not self.logged_in_user.check_password(old_password):
            print("Wrong password.")
            return Mode.CHOOSE_SERVICE_LOGGED_IN
        else:
            new_password = self.password_input()
            self.logged_in_user.change_password(new_password)
            self.rewrite_changed_password_to_file(self.logged_in_user.get_username(), old_password, new_password)
            print("Password changed successfully.")
            return Mode.CHOOSE_SERVICE_LOGGED_IN

    def username_input(self):
        while True:
            username = self.enter_username()
            if self.valid_username(username):
                return username
            else:
                print(f"Invalid username: {(', '.join(self.get_username_violations(username))).capitalize()}")

    def password_input(self, change=False):
        while True:
            password = self.enter_password(change=change)
            if self.valid_password(password):
                return password
            else:
                print(f"Invalid password: {(', '.join(self.get_password_violations(password))).capitalize()}")

    def enter_username(self):
        return input('Enter username: ')

    def enter_password(self, change=False):
        return input(f"Enter {'new ' if change else ''}password: ")

    def valid_username(self, username):
        return 3 <= len(username) <= 40 and username.isalpha() and username not in self.users.keys()

    def valid_password(self, password):
        return 16 <= len(password) <= 40 and password != password.lower() and not password.isalnum()

    def get_password_violations(self, password):
        violations = []
        if len(password) < MIN_PASS_LEN:
            violations.append('too short (must be between 3 and 40 characters long)')
        if len(password) > MAX_PASS_LEN:
            violations.append('too long (must be between 3 and 40 characters long)')
        if password == password.lower():
            violations.append('must have upper and lower case letters')
        if password.isalpha():
            violations.append('add numbers')
        if password.isalnum():
            violations.append('add symbols')
        return violations

    def get_username_violations(self, username):
        violations = []
        if username in self.users.keys():
            violations.append('username taken')
        if len(username) < MIN_USER_LEN:
            violations.append('too short (must be between 3 and 40 characters long)')
        if len(username) > MAX_USER_LEN:
            violations.append('too long (must be between 3 and 40 characters long)')
        if not username.isalpha():
            violations.append('only letters allowed')
        return violations

if __name__ == '__main__':
    system = System()
