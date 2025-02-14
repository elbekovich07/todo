from models import User

class Session:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Session, cls).__new__(cls)
            cls._instance.session = None
        return cls._instance

    def add_session(self, user: User):
        self.session = user

    def check_session(self) -> User | None:
        return self.session

    def remove_session(self):
        self.session = None
