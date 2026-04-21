import tkinter as tk
from tkinter import ttk, messagebox
from modules.db_config import DBConnection
from modules.password_helper import PasswordHelper
from modules.forms.register_form import RegisterForm


class LoginForm:
    """Форма авторизации пользователя"""

    def __init__(self, parent, on_login_success):
        self.parent = parent
        self.on_login_success = on_login_success

        self.window = tk.Toplevel(parent)
        self.window.title("Авторизация - OrderAccounting")
        self.window.geometry("350x250")
        self.window.resizable(False, False)

        # Центрирование
        self.window.transient(parent)
        self.window.grab_set()

        # Заголовок
        ttk.Label(self.window, text="Вход в систему учёта заказов",
                  font=('Arial', 12, 'bold')).pack(pady=20)

        # Форма
        frame = ttk.Frame(self.window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Логин:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.entry_login = ttk.Entry(frame, width=25)
        self.entry_login.grid(row=0, column=1, pady=5)

        ttk.Label(frame, text="Пароль:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.entry_password = ttk.Entry(frame, width=25, show="*")
        self.entry_password.grid(row=1, column=1, pady=5)

        # Кнопки
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=20)

        ttk.Button(btn_frame, text="Войти", command=self.login).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Регистрация", command=self.open_register).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Отмена", command=self.window.destroy).pack(side=tk.LEFT, padx=10)

        self.entry_login.focus()

    def login(self):
        """Проверка логина и пароля"""
        login = self.entry_login.get().strip()
        password = self.entry_password.get()

        if not login or not password:
            messagebox.showwarning("Ошибка", "Введите логин и пароль")
            return

        conn = DBConnection.get_connection()
        try:
            cursor = conn.cursor()

            # Получить соль, хэш и данные пользователя
            cursor.execute("""
                SELECT u.user_id, u.full_name, u.password_salt, u.password_hash, r.role_name
                FROM users u
                JOIN roles r ON u.role_id = r.role_id
                WHERE u.login = %s AND u.is_active = 1
            """, (login,))

            user = cursor.fetchone()

            if not user:
                messagebox.showerror("Ошибка", "Неверный логин или пароль")
                return

            # Проверка пароля
            if PasswordHelper.verify_password(password, user['password_salt'], user['password_hash']):
                # Успешный вход
                self.on_login_success(
                    user_id=user['user_id'],
                    login=login,
                    full_name=user['full_name'],
                    role_name=user['role_name']
                )
                self.window.destroy()
            else:
                messagebox.showerror("Ошибка", "Неверный логин или пароль")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при входе: {e}")
        finally:
            conn.close()

    def open_register(self):
        """Открыть форму регистрации"""
        RegisterForm(self.window)