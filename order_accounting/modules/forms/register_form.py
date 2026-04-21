import tkinter as tk
from tkinter import ttk, messagebox
from modules.db_config import DBConnection
from modules.password_helper import PasswordHelper


class RegisterForm:
    """Форма регистрации нового пользователя"""

    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Регистрация нового пользователя")
        self.window.geometry("400x450")
        self.window.resizable(False, False)

        # Центрирование окна
        self.window.transient(parent)
        self.window.grab_set()

        # Заголовок
        ttk.Label(self.window, text="Регистрация пользователя",
                  font=('Arial', 14, 'bold')).pack(pady=10)

        # Форма
        frame = ttk.Frame(self.window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        # Поля ввода
        ttk.Label(frame, text="Логин:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.entry_login = ttk.Entry(frame, width=30)
        self.entry_login.grid(row=0, column=1, pady=5)

        ttk.Label(frame, text="Пароль:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.entry_password = ttk.Entry(frame, width=30, show="*")
        self.entry_password.grid(row=1, column=1, pady=5)

        ttk.Label(frame, text="Подтверждение пароля:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.entry_confirm = ttk.Entry(frame, width=30, show="*")
        self.entry_confirm.grid(row=2, column=1, pady=5)

        ttk.Label(frame, text="Полное имя:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.entry_fullname = ttk.Entry(frame, width=30)
        self.entry_fullname.grid(row=3, column=1, pady=5)

        ttk.Label(frame, text="Email:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.entry_email = ttk.Entry(frame, width=30)
        self.entry_email.grid(row=4, column=1, pady=5)

        ttk.Label(frame, text="Роль:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.role_combo = ttk.Combobox(frame, values=['manager', 'storekeeper'], width=27)
        self.role_combo.grid(row=5, column=1, pady=5)
        self.role_combo.set('manager')

        # Кнопки
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=20)

        ttk.Button(btn_frame, text="Зарегистрировать", command=self.register).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Отмена", command=self.window.destroy).pack(side=tk.LEFT, padx=10)

    def register(self):
        """Регистрация пользователя"""
        login = self.entry_login.get().strip()
        password = self.entry_password.get()
        confirm = self.entry_confirm.get()
        fullname = self.entry_fullname.get().strip()
        email = self.entry_email.get().strip()
        role_name = self.role_combo.get()

        # Валидация
        if not login or not password or not fullname or not email:
            messagebox.showwarning("Ошибка", "Заполните все поля")
            return

        if password != confirm:
            messagebox.showwarning("Ошибка", "Пароли не совпадают")
            return

        if len(password) < 6:
            messagebox.showwarning("Ошибка", "Пароль должен быть не менее 6 символов")
            return

        # Получаем role_id по имени роли
        role_id = 2 if role_name == 'manager' else 3

        # Генерация соли и хэша
        salt = PasswordHelper.generate_salt()
        password_hash = PasswordHelper.hash_password(password, salt)

        # Вызов хранимой процедуры
        conn = DBConnection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.callproc('sp_register_user', (login, salt, password_hash, fullname, email, role_id))
            conn.commit()

            messagebox.showinfo("Успех", f"Пользователь '{login}' успешно зарегистрирован")
            self.window.destroy()

        except Exception as e:
            conn.rollback()
            messagebox.showerror("Ошибка", f"Не удалось зарегистрировать пользователя: {e}")
        finally:
            conn.close()