MIN_PASS_LEN = 16
MAX_PASS_LEN = 40

MIN_USER_LEN = 3
MAX_USER_LEN = 40

class User:
    def __init__(self, username, password):
        self.username = username
        self._password = password

class Mode(Enum):
    CHOOSE_SERVICE = 0
    LOGIN = 1
    SIGN_UP = 2

class System:
    def __init__(self):
        self.users = dict()
        self.mode = Mode.CHOOSE_SERVICE
        self.run()

    def add_user(self, user):
        self.users[user.username] = user.password

    def sign_up(self):
        username = self.username_input()
        password = self.password_input()
        self.users[username] = User(username, password)
        print('Success!')

    def get_password_violations(self, password):
        violations = []
        if len(password) < MIN_PASS_LEN:
            violations.append('too short (must be between 3 and 40 characters long)')
        if len(password) > MAX_PASS_LEN:
            violaitons.append('too long (must be between 3 and 40 characters long)')
        if password == password.lower():
            violations.append('must have upper and lower case letters')
        if password.alpha():
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

    def valid_username(self, username):
        return 3 <= len(username) <= 40 and username.isalpha() and username not in self.users.keys()

    def valid_password(self, password):
        return 16 <= len(password) <= 40 and password != password.lower() and not password.isalnum()

    def username_input(self):
        while True:
            username = input('Enter username: ')
            if self.valid_username(username):
                return username
            else:
                print(f"Invalid username: {(', '.join(self.get_username_violations(username))).capitalize()}")

    def password_input(self):
        while True:
            password = input('Enter password: ')
            if self.valid_password(password):
                return password
            else:
                print(f"Invalid password: {(', '.join(self.get_password_violations(password))).capitalize()}")

    def run(self):
        while True:
            if self.mode == Mode.CHOOSE_SERVICE:
                mode = input("Enter 'login' for logging in, 'signup' for signing up: ").lower()
            if mode == 'sign':
                mode = self.sign_up()


if __name__ == '__main__':
    system = System()

