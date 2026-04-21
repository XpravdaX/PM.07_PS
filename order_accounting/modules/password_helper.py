import hashlib
import secrets


class PasswordHelper:
    """Вспомогательный класс для безопасного хэширования паролей"""

    @staticmethod
    def generate_salt() -> str:
        """
        Генерирует случайную соль: 16 случайных байт → hex-строка (32 символа)
        """
        return secrets.token_hex(16)  # 16 байт = 32 hex-символа

    @staticmethod
    def hash_password(password: str, salt: str) -> str:
        """
        Вычисляет SHA-256 хэш от строки (соль + пароль)
        Возвращает hex-строку (64 символа)
        """
        combined = salt + password
        return hashlib.sha256(combined.encode('utf-8')).hexdigest()

    @staticmethod
    def verify_password(input_password: str, salt: str, stored_hash: str) -> bool:
        """
        Проверяет введённый пароль: вычисляет хэш от (соль + пароль)
        и сравнивает с хранимым хэшем
        """
        computed_hash = PasswordHelper.hash_password(input_password, salt)
        return computed_hash == stored_hash