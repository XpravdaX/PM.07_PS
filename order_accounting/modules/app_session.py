class AppSession:
    """Статический класс для хранения данных текущей сессии пользователя"""

    _user_id = None
    _login = None
    _full_name = None
    _role_name = None

    @classmethod
    def set_user(cls, user_id: int, login: str, full_name: str, role_name: str):
        """Установка данных текущего пользователя"""
        cls._user_id = user_id
        cls._login = login
        cls._full_name = full_name
        cls._role_name = role_name

    @classmethod
    def get_user_id(cls):
        return cls._user_id

    @classmethod
    def get_login(cls):
        return cls._login

    @classmethod
    def get_full_name(cls):
        return cls._full_name

    @classmethod
    def get_role_name(cls):
        return cls._role_name

    @classmethod
    def is_admin(cls):
        return cls._role_name == 'admin'

    @classmethod
    def is_manager(cls):
        return cls._role_name == 'manager'

    @classmethod
    def is_storekeeper(cls):
        return cls._role_name == 'storekeeper'

    @classmethod
    def is_authenticated(cls):
        return cls._user_id is not None

    @classmethod
    def clear(cls):
        """Очистка сессии (при выходе)"""
        cls._user_id = None
        cls._login = None
        cls._full_name = None
        cls._role_name = None