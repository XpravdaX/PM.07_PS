import pymysql
from pymysql.cursors import DictCursor


class DBConnection:
    """Класс для управления подключением к MySQL"""

    _config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': '',
        'database': 'order_accounting',
        'charset': 'utf8mb4',
        'cursorclass': DictCursor
    }

    @classmethod
    def get_connection(cls):
        """Возвращает новое соединение с БД"""
        return pymysql.connect(**cls._config)