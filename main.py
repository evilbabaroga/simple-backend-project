from os import getlogin
from functools import reduce
from getpass import getpass
from abc import ABC, abstractmethod

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

class Phase(ABC):
    def __init__(self):
        self.print_arrival_message()
        self.functions = {
            'exit': 'exit',
            'q': 'back'
        }

    @abstractmethod
    def print_arrival_message(self):
        pass

    @abstractmethod
    def console_string(self):
        pass

    def get_function(self, func):
        return self.functions[func]
    
    def __repr__(self):
        return f"{self.__class__.__name__}(functions={self.functions})" 

    def __str__(self):
        return self.__class__.__name__

    def to_function(self):
        name = self.__class__.__name__
        return ''.join([name[i] if not name[i].isupper() else f"_{name[i].lower()}" for i in range(len(name))])[1:]

class ChooseService(Phase):
    def __init__(self):
        super().__init__() 
        self.functions.update({ 
            'login': 'log_in',
            'signup': 'sign_up'
         })

    def print_arrival_message(self):
        print("Enter 'login' for logging in, 'signup' for signing up, 'q' for back, 'exit' to exit program.")

    def console_string(self):
        return 'Login Form'

class ChooseServiceLoggedIn(Phase):
    def __init__(self, logged_in_user: User):
        self.logged_in_user = logged_in_user
        super().__init__()
        self.functions.update({
            'pass': 'change_user_password',
            'logout': 'log_out'
        })

    def print_arrival_message(self):
        print(f"Welcome {self.logged_in_user.get_username()}. Type 'pass' to change password or 'logout'/'q' to log out.")

    def console_string(self):
        return self.logged_in_user.get_username()

class System:
    def __init__(self):
        self.users = dict()
        self.file_format = READ_FILE[0]
        try:
            for user in USERS_FROM_FILE:
                username = user[0]
                password = user[1]
                self.users[username] = User(username, password)
        except:
            with open('users', 'w') as f:
                f.write('')
            self.file_format = ''
            self.users = dict()
            getpass("Corrupt database, purging. ¯\_(ツ)_/¯\nPress enter to continue... ")
        self.logged_in_user = None
        self.quit = False
        self.phases = Stack()
        self.enter_phase(ChooseService())
        self.run()

    def enter_phase(self, phase):
        self.phases.push(phase)

    def run(self):
        while not self.quit and not self.phases.is_empty():
            self.run_phase()

    def run_phase(self):
        service = input(self.print_console_line()).lower()
        self.run_service(service)

    def run_service(self, service):
        if service in self.phases.peek().functions.keys():
            self.run_function(service)
        elif type(service) is Phase:
            self.run_phase(service)
        elif service == '':
            return
        else:
            print("Invalid command.")

    def run_function(self, function):
        function = self.phases.peek().get_function(function)
        getattr(self, function)()

    def print_console_line(self):
        return f"{getlogin()}>" + reduce(lambda mode1, mode2: mode1 + '>' + mode2, [phase.console_string() for phase in self.phases.array if phase is not None]) + '>'

    def back(self):
        self.phases.pop()

    def exit(self):
        self.quit = True

    def sign_up(self):
        username, is_back = self.username_input()
        if is_back:
            return
        password, is_back = self.password_input()
        if is_back:
            return
        self.users[username] = User(username, password)
        self.write_user_to_file(username, password)
        print('Success!')

    def log_in(self):
        username = self.enter_username()
        while username not in self.users:
            if self.check_back(username):
                return
            else:
                print(f"User '{username}' doesn't exist. Try again or enter 'q' to go back.")
                username = self.enter_username()
        count = 3
        password = self.enter_password()
        while count > 0:
            if self.check_back(password):
                return
            if not self.users[username].check_password(password):
                print(f"Wrong password. {count} {'tries' if count > 1 else 'try'} left.")
                password = self.enter_password()
                if self.check_back(password):
                    return
                count -= 1
            if self.users[username].check_password(password):
                self.logged_in_user = self.users[username]
                self.enter_phase(ChooseServiceLoggedIn(self.logged_in_user))
                return
        print("Login failed.")

    def change_user_password(self):
        old_password, is_back = self.password_input(check=False, pass_type='old')
        if is_back:
            return
        if not self.logged_in_user.check_password(old_password):
            print("Wrong password.")
        else:
            new_password, is_back = self.password_input()
            if is_back:
                return
            self.logged_in_user.change_password(new_password)
            self.rewrite_changed_password_to_file(self.logged_in_user.get_username(), old_password, new_password)
            print("Password changed successfully.")

    def log_out(self):
        self.logged_in_user = None
        self.back()

    def username_input(self):
        while True:
            username = self.enter_username()
            if self.check_back(username):
                return username, True
            if self.valid_username(username):
                return username, False
            else:
                print(f"Invalid username: {(', '.join(self.get_username_violations(username))).capitalize()}")

    def password_input(self, check=True, pass_type=''):
        while True:
            password = self.enter_password(pass_type=pass_type)
            if self.check_back(password):
                return password, True
            if not check or self.valid_password(password):
                return password, False
            else:
                print(f"Invalid password: {(', '.join(self.get_password_violations(password))).capitalize()}")

    def check_back(self, entered_string):
        if entered_string.lower() == 'q':
            print('Cancelled, going back.')
            return True
        return False

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

    def write_user_to_file(self, username, password):
        self.file_format += f"{' ' if len(self.file_format) > 0 else ''}{username},{password}"
        with open('users', 'w') as f:
            f.write(self.file_format)

    def rewrite_changed_password_to_file(self, username, old_password, new_password):
        self.file_format = self.file_format.replace(f"{username},{old_password}", f"{username},{new_password}")
        with open('users', 'w') as f:
                f.write(self.file_format)

if __name__ == '__main__':
    system = System()
