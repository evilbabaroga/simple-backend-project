from enum import Enum
from functools import reduce
from getpass import getpass

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
            self.array[self.top] = None
            self.top -= 1
            return removed_item
        else:
            print("Stack empty, can't pop.")

    def is_empty(self):
        return self.top == -1

class Mode(Enum):
    CHOOSE_SERVICE = 0
    LOG_IN = 1
    SIGN_UP = 2
    CHOOSE_SERVICE_LOGGED_IN = 3
    CHANGE_USER_PASSWORD = 4

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
        self.depth_modes = [Mode.CHOOSE_SERVICE, Mode.CHOOSE_SERVICE_LOGGED_IN]
        self.mode = Stack()
        self.enter_mode(Mode.CHOOSE_SERVICE)
        self.logged_in_user = None
        self.quit = False
        self.run()

    def run_mode(self, mode):
        try:
            return getattr(self, f"{mode.name.lower()}")()
        except:
            self.quit = True

    def back(self):
        self.mode.pop()

    def run(self):
        while not self.quit and not self.mode.is_empty():
            self.run_mode(self.mode.peek())
            print(self.quit, self.mode.peek())

    def exit(self):
        self.quit = True

    def enter_mode(self, mode):
        if mode == Mode.CHOOSE_SERVICE:
            print("Enter 'login' for logging in, 'signup' for signing up, 'q' for back, 'exit' to quit.")
        if mode == Mode.CHOOSE_SERVICE_LOGGED_IN:
           print(f"Welcome {self.logged_in_user.get_username()}. Type 'pass' to change password or 'logout' to log out.") 
        if not self.mode.is_empty() and self.mode.peek() not in self.depth_modes:
            self.mode.pop()
        self.mode.push(mode)

    def get_print_from_mode(self, mode):
        match mode:
            case Mode.CHOOSE_SERVICE:
                return "system"
            case Mode.CHOOSE_SERVICE_LOGGED_IN:
                return str(self.logged_in_user.get_username())
        return ''

    def print_at_depth(self):
        return reduce(lambda mode1, mode2: mode1 + '>' + mode2, list(map(self.get_print_from_mode, list(filter(lambda curr_mode: curr_mode in self.depth_modes, self.mode.array))))) + '>' if self.mode.peek() in self.depth_modes else ''

    def choose_service(self):
        service = input(self.print_at_depth()).lower()
        if self.check_back(service):
            self.back()
            return
        if service == 'login':
            self.log_in()
        elif service == 'signup':
            self.sign_up()
        elif service == 'exit':
            self.back()
        else:
            print("Invalid command.")

    def sign_up(self):
        username = self.username_input()
        if self.check_back(username):
            return
        password = self.password_input()
        if self.check_back(password):
            return
        self.users[username] = User(username, password)
        self.write_user_to_file(username, password)
        print('Success!')
        self.back()

    def write_user_to_file(self, username, password):
        self.file_format += f"{' ' if len(self.file_format) > 0 else ''}{username},{password}"
        with open('users', 'w') as f:
            f.write(self.file_format)

    def rewrite_changed_password_to_file(self, username, old_password, new_password):
            self.file_format = self.file_format.replace(f"{username},{old_password}", f"{username},{new_password}")
            with open('users', 'w') as f:
                f.write(self.file_format)

    def check_back(self, entered_string):
        if entered_string.lower() == 'q':
            return True
        return False

    def log_in(self):
        username = self.enter_username()
        if username not in self.users:
            if not self.check_back(username):
                print(f"User '{username}' doesn't exist. Try again or enter 'q' to go back.")
            return
        count = 3
        password = self.enter_password()
        while count > 0:
            if self.check_back(password):
                return
            if not self.users[username].check_password(password):
                print(f"Wrong password. {count} {'tries' if count > 1 else 'try'} left.")
                password = self.enter_password()
                count -= 1
            if self.users[username].check_password(password):
                self.logged_in_user = self.users[username]
                self.enter_mode(Mode.CHOOSE_SERVICE_LOGGED_IN)
                return
        print("Login failed.")
        self.back()

    def choose_service_logged_in(self):
        service = input(self.print_at_depth()).lower()
        if self.check_back(service):
            self.back()
            return
        if service == 'pass':
            self.change_user_password()
        if service == 'logout':
            self.back()
        if service == 'exit':
            self.exit()

    def change_user_password(self):
        old_password = self.password_input(check=False, pass_type='old')
        print(self.mode)
        if self.check_back(old_password):
            return
        if not self.logged_in_user.check_password(old_password):
            print("Wrong password.")
            self.back()
        else:
            new_password = self.password_input()
            self.logged_in_user.change_password(new_password)
            self.rewrite_changed_password_to_file(self.logged_in_user.get_username(), old_password, new_password)
            print("Password changed successfully.")
            self.back()

    def username_input(self):
        while True:
            username = self.enter_username()
            if self.check_back(username):
                return
            if self.valid_username(username):
                return username
            else:
                print(f"Invalid username: {(', '.join(self.get_username_violations(username))).capitalize()}")

    def password_input(self, check=True, pass_type=''):
        while True:
            password = self.enter_password(pass_type=pass_type)
            if self.check_back(password):
                return
            if not check or self.valid_password(password):
                return password
            else:
                print(f"Invalid password: {(', '.join(self.get_password_violations(password))).capitalize()}")

    def enter_username(self):
        return input('Enter username: ')

    def enter_password(self, pass_type=''):
        return getpass(f"Enter {pass_type + ' ' if pass_type != '' else ''}password: ")

    def valid_username(self, username):
        return 3 <= len(username) <= 40 and username.isalpha() and username not in self.users.keys()

    def valid_password(self, password):
        return 16 <= len(password) <= 40 and password != password.lower() and not password.isalnum()

    def get_password_violations(self, password):
        violations = []
        if len(password) < MIN_PASS_LEN:
            violations.append(f'too short (must be between {MIN_PASS_LEN} and {MAX_PASS_LEN} characters long)')
        if len(password) > MAX_PASS_LEN:
            violations.append(f'too long (must be between {MIN_PASS_LEN} and {MAX_PASS_LEN} characters long)')
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
            violations.append(f'too short (must be between {MIN_USER_LEN} and {MAX_USER_LEN} characters long)')
        if len(username) > MAX_USER_LEN:
            violations.append(f'too long (must be between {MIN_USER_LEN} and {MAX_USER_LEN} characters long)')
        if not username.isalpha():
            violations.append('only letters allowed')
        return violations

if __name__ == '__main__':
    system = System()
