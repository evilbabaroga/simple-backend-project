from os import getlogin
from copy import deepcopy
import cryptocode
import json
from functools import reduce
from getpass import getpass
from abc import ABC, abstractmethod

PASSWORD = "qwerasdfzxcv123123123;;;"

MIN_PASS_LEN = 16
MAX_PASS_LEN = 40

MIN_USER_LEN = 3
MAX_USER_LEN = 40

MIN_NAME_LEN = 2
MAX_NAME_LEN = 20

json_file_name = 'users.json'
users = {'users': []}

# Обид за читање и parse на JSON file
try:
    with open(json_file_name, 'r') as f:
        json_file_read = f.read()
        try:
            users = json.loads(json_file_read)
        except json.decoder.JSONDecodeError:
            with open(json_file_name, 'w') as f1:
                getpass("JSON file corrupted, purging. ¯\_(ツ)_/¯\nPress enter to continue... ")
                json.dump(users, f1, indent=4)
except FileNotFoundError:
    getpass('JSON file not found. Recreating it... ')
    with open(json_file_name, 'w') as f:
        json.dump(users, f, indent=4)

# Дата структури што ги поддржува JSON
json_types = [str, int, list, dict, tuple, float, bool, None]
def json_dictify_recursive(var):
    """
    Конверзија на објект во JSON-компатибилен речник рекурзивно.
    Три можни сценарија:
        1. iterable: за секој член ја пуштаме функцијата (може да биде non_json или iterable што содржи non_json),
        2. non_json тип: го конвертираме во речник со __dict__ и го третираме како iterable,
        3. non-iterable json_tip: само враќаме вредност
    Keyword arguments:
    var -- object to be converted
    """
    # iterable
    if type(var) in [list, tuple]:
        print(var)
        dictified = [None] * len(var)
        for i in range(len(var)):
            dictified[i] = json_dictify_recursive(var[i])
        if type(var) is tuple:
            dictified = tuple(dictified)
        return dictified.copy()
    if type(var) is dict:
        for key, val in var.items():
            var[key] = json_dictify_recursive(val)
        return var.copy()
    # non_json тип
    if type(var) not in json_types:
        dict_var: dict = var.__dict__.copy()
        for key, val in list(dict_var.items()):
            if val not in json_types:
                dict_var[key] = json_dictify_recursive(val)
        return dict_var
    # non-iterable json_tip
    return var

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
    def __init__(self, username, password, first_name, last_name):
        self._username = username
        self.__password = password
        self.first_name = first_name
        self.last_name =last_name

    def check_password(self, password):
        return password == self.__password

    def get_username(self):
        return self._username

    def get_encrypted_password(self):
        return cryptocode.encrypt(self.__password, PASSWORD)

    def change_password(self, new_password):
        self.__password = new_password

    def __repr__(self):
        return f"{self.__class__.__name__}(username={self._username}, password={len(self.__password) * '*'} first_name={self.first_name}, last_name={self.last_name})"

    def __str__(self):
        return f"username: {self._username}\nfull name: {self.first_name} {self.last_name}"

    def to_JSON(self):
        return {'username': self._username, 'password': len(self.__password) * '*', 'first_name': self.first_name, 'last_name': self.last_name}

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
        print(f"Welcome {self.logged_in_user.first_name} {self.logged_in_user.last_name}. Type 'pass' to change password or 'logout'/'q' to log out.")

    def console_string(self):
        return self.logged_in_user.get_username()

class System:
    def __init__(self):
        self.users = {
            user['_username']: User(
                user['_username'],
                # Декрипција на password
                cryptocode.decrypt(user['_User__password'], PASSWORD),
                user['first_name'],
                user['last_name']
            ) for user in users['users']
        }
        self.logged_in_user = None
        self.quit = False
        self.phases = Stack()
        self.enter_phase(ChooseService())
        self.run()

    # Се повикува секогаш кога имаме промена на self.users (додавање корисник, менување pass).
    def update_json(self):
        with open(json_file_name, 'w') as f:
            users_dict = {'users': []}
            encrypted_users = self.users.copy()
            for user in encrypted_users.values():
                # Целта е во json.dump да се pass-не аргумент речник од корисници со енкриптиран pass. 
                # Се креира копија на секој корисник со цел да не се промени pass-от на корисниците во RAM.
                encrypted_user: User = deepcopy(user)
                encrypted_user.change_password(encrypted_user.get_encrypted_password())
                users_dict['users'].append(json_dictify_recursive(encrypted_user))
            json.dump(users_dict, f, indent=4)

    def enter_phase(self, phase):
        self.phases.push(phase)

    def run(self):
        while not self.quit and not self.phases.is_empty():
            self.run_phase()
        self.update_json()

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
        first_name, isback = self.name_input('first')
        if isback:
            return
        last_name, isback = self.name_input('last')
        if isback:
            return
        self.users[username] = User(username, password, first_name, last_name)
        self.update_json()
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
            new_password, is_back = self.password_input(pass_type='new')
            if is_back:
                return
            self.logged_in_user.change_password(new_password)
            self.update_json()
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

    def name_input(self, name_type):
        while True:
            name = self.enter_name(name_type=name_type)
            if self.check_back(name):
                return name, True
            if self.valid_name(name):
                return name, False
            else:
                print(f"Invalid {name_type} name: {(', '.join(self.get_name_violations(name))).capitalize()}")

    def check_back(self, entered_string):
        if entered_string.lower() == 'q':
            print('Cancelled, going back.')
            return True
        return False

    def enter_username(self):
        return input('Enter username: ')

    def enter_password(self, pass_type=''):
        return getpass(f"Enter {pass_type + ' ' if pass_type != '' else ''}password: ")

    def enter_name(self, name_type='first'):
        return input(f"Enter {name_type} name: ")

    def valid_username(self, username):
        return MIN_USER_LEN <= len(username) <= MAX_USER_LEN and username.isalpha() and username not in self.users.keys()

    def valid_password(self, password):
        return MIN_PASS_LEN <= len(password) <= MAX_PASS_LEN and password != password.upper() and password != password.lower() and not password.isalnum()

    def valid_name(self, name):
        return MIN_NAME_LEN <= len(name) <= MAX_NAME_LEN and name.isalpha()

    def get_password_violations(self, password):
        violations = []
        if len(password) < MIN_PASS_LEN:
            violations.append(f'too short (must be between {MIN_PASS_LEN} and {MAX_PASS_LEN} characters long)')
        if len(password) > MAX_PASS_LEN:
            violations.append(f'too long (must be between {MIN_PASS_LEN} and {MAX_PASS_LEN} characters long)')
        if password == password.lower() or password == password.upper():
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

    def get_name_violations(self, name):
        violations = []
        if len(name) < MIN_NAME_LEN:
            violations.append(f'too short (must be between {MIN_NAME_LEN} and {MAX_NAME_LEN} characters long)')
        if len(name) > MAX_NAME_LEN:
            violations.append(f'too long (must be between {MIN_NAME_LEN} and {MAX_NAME_LEN} characters long)')
        if not name.isalpha():
            violations.append('only letters allowed')
        return violations

if __name__ == '__main__':
    system = System()

