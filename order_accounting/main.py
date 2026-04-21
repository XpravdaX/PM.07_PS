import tkinter as tk
from tkinter import ttk, messagebox
from modules.app_session import AppSession
from modules.db_config import DBConnection
from modules.order_service import OrderService
from modules.forms.login_form import LoginForm


class MainApplication:
    def __init__(self, root):
        self.root = root
        self.root.title("OrderAccounting - Система учёта заказов")
        self.root.geometry("1200x700")

        # Показать форму входа
        self.show_login()

    def show_login(self):
        """Показать форму входа"""
        LoginForm(self.root, self.on_login_success)

    def on_login_success(self, user_id, login, full_name, role_name):
        """Обработчик успешного входа"""
        AppSession.set_user(user_id, login, full_name, role_name)

        # Очистить окно
        for widget in self.root.winfo_children():
            widget.destroy()

        # Создать интерфейс
        self.create_interface()

    def create_interface(self):
        """Создание основного интерфейса"""
        # Строка статуса
        status_bar = ttk.Frame(self.root)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        ttk.Label(status_bar,
                  text=f"👤 {AppSession.get_full_name()} | Роль: {AppSession.get_role_name()}").pack(side=tk.LEFT,
                                                                                                    padx=10)

        ttk.Button(status_bar, text="🚪 Выйти", command=self.logout).pack(side=tk.RIGHT, padx=10)

        # Вкладки
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Вкладка "Заказы"
        self.orders_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.orders_frame, text="📦 Заказы")
        self.setup_orders_tab()

        # Вкладка "Клиенты"
        self.clients_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.clients_frame, text="👥 Клиенты")
        self.setup_clients_tab()

        # Вкладка "Товары"
        self.products_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.products_frame, text="📦 Товары")
        self.setup_products_tab()

        # Вкладка "Статистика"
        self.stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="📊 Статистика")
        self.setup_stats_tab()

        # Загрузить данные
        self.load_all_data()

    def setup_orders_tab(self):
        """Настройка вкладки заказов"""
        # Панель инструментов
        toolbar = ttk.Frame(self.orders_frame)
        toolbar.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(toolbar, text="➕ Новый заказ", command=self.create_order).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="✏️ Сменить статус", command=self.change_status).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="📋 Детали заказа", command=self.view_order_details).pack(side=tk.LEFT, padx=2)

        if AppSession.is_admin():
            ttk.Button(toolbar, text="🗑️ Удалить заказ", command=self.delete_order).pack(side=tk.LEFT, padx=2)

        ttk.Label(toolbar, text="Фильтр:").pack(side=tk.LEFT, padx=(20, 5))
        self.status_filter = ttk.Combobox(toolbar,
                                          values=['Все', 'new', 'in_work', 'shipped', 'completed', 'cancelled'],
                                          width=15)
        self.status_filter.pack(side=tk.LEFT, padx=2)
        self.status_filter.set('Все')
        ttk.Button(toolbar, text="🔍 Применить", command=self.load_orders).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🔄 Обновить", command=self.load_orders).pack(side=tk.LEFT, padx=2)

        # Таблица заказов
        columns = ('order_id', 'order_date', 'client_name', 'status', 'total_amount', 'manager_name')
        self.orders_tree = ttk.Treeview(self.orders_frame, columns=columns, show='headings', height=20)

        self.orders_tree.heading('order_id', text='№')
        self.orders_tree.heading('order_date', text='Дата')
        self.orders_tree.heading('client_name', text='Клиент')
        self.orders_tree.heading('status', text='Статус')
        self.orders_tree.heading('total_amount', text='Сумма (руб.)')
        self.orders_tree.heading('manager_name', text='Менеджер')

        self.orders_tree.column('order_id', width=60)
        self.orders_tree.column('order_date', width=140)
        self.orders_tree.column('client_name', width=250)
        self.orders_tree.column('status', width=100)
        self.orders_tree.column('total_amount', width=120)
        self.orders_tree.column('manager_name', width=180)

        scrollbar = ttk.Scrollbar(self.orders_frame, orient=tk.VERTICAL, command=self.orders_tree.yview)
        self.orders_tree.configure(yscrollcommand=scrollbar.set)

        self.orders_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 5), pady=5)

        # Статусная строка
        self.orders_status = ttk.Label(self.orders_frame, text="", anchor=tk.W)
        self.orders_status.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

    def setup_clients_tab(self):
        """Настройка вкладки клиентов"""
        toolbar = ttk.Frame(self.clients_frame)
        toolbar.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(toolbar, text="➕ Добавить клиента", command=self.add_client).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="✏️ Редактировать", command=self.edit_client).pack(side=tk.LEFT, padx=2)

        if AppSession.is_admin():
            ttk.Button(toolbar, text="🗑️ Удалить", command=self.delete_client).pack(side=tk.LEFT, padx=2)

        ttk.Button(toolbar, text="🔄 Обновить", command=self.load_clients).pack(side=tk.LEFT, padx=2)

        columns = ('client_id', 'full_name', 'phone', 'email')
        self.clients_tree = ttk.Treeview(self.clients_frame, columns=columns, show='headings', height=20)

        self.clients_tree.heading('client_id', text='ID')
        self.clients_tree.heading('full_name', text='Наименование')
        self.clients_tree.heading('phone', text='Телефон')
        self.clients_tree.heading('email', text='Email')

        self.clients_tree.column('client_id', width=50)
        self.clients_tree.column('full_name', width=300)
        self.clients_tree.column('phone', width=150)
        self.clients_tree.column('email', width=250)

        scrollbar = ttk.Scrollbar(self.clients_frame, orient=tk.VERTICAL, command=self.clients_tree.yview)
        self.clients_tree.configure(yscrollcommand=scrollbar.set)

        self.clients_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 5), pady=5)

    def setup_products_tab(self):
        """Настройка вкладки товаров"""
        toolbar = ttk.Frame(self.products_frame)
        toolbar.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(toolbar, text="➕ Добавить товар", command=self.add_product).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="✏️ Редактировать", command=self.edit_product).pack(side=tk.LEFT, padx=2)

        if AppSession.is_admin():
            ttk.Button(toolbar, text="🗑️ Удалить", command=self.delete_product).pack(side=tk.LEFT, padx=2)

        ttk.Button(toolbar, text="🔄 Обновить", command=self.load_products).pack(side=tk.LEFT, padx=2)

        columns = ('product_id', 'name', 'price', 'stock_quantity')
        self.products_tree = ttk.Treeview(self.products_frame, columns=columns, show='headings', height=20)

        self.products_tree.heading('product_id', text='ID')
        self.products_tree.heading('name', text='Товар')
        self.products_tree.heading('price', text='Цена (руб.)')
        self.products_tree.heading('stock_quantity', text='Остаток')

        self.products_tree.column('product_id', width=50)
        self.products_tree.column('name', width=350)
        self.products_tree.column('price', width=120)
        self.products_tree.column('stock_quantity', width=100)

        scrollbar = ttk.Scrollbar(self.products_frame, orient=tk.VERTICAL, command=self.products_tree.yview)
        self.products_tree.configure(yscrollcommand=scrollbar.set)

        self.products_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 5), pady=5)

    def setup_stats_tab(self):
        """Настройка вкладки статистики"""
        columns = ('manager_name', 'orders_count', 'total_sum', 'avg_order_amount')
        self.stats_tree = ttk.Treeview(self.stats_frame, columns=columns, show='headings', height=20)

        self.stats_tree.heading('manager_name', text='Менеджер')
        self.stats_tree.heading('orders_count', text='Кол-во заказов')
        self.stats_tree.heading('total_sum', text='Общая сумма (руб.)')
        self.stats_tree.heading('avg_order_amount', text='Средний чек (руб.)')

        self.stats_tree.column('manager_name', width=250)
        self.stats_tree.column('orders_count', width=120)
        self.stats_tree.column('total_sum', width=180)
        self.stats_tree.column('avg_order_amount', width=180)

        scrollbar = ttk.Scrollbar(self.stats_frame, orient=tk.VERTICAL, command=self.stats_tree.yview)
        self.stats_tree.configure(yscrollcommand=scrollbar.set)

        self.stats_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 5), pady=5)

        ttk.Button(self.stats_frame, text="🔄 Обновить статистику", command=self.load_stats).pack(pady=5)

    def load_all_data(self):
        """Загрузка всех данных"""
        self.load_orders()
        self.load_clients()
        self.load_products()
        self.load_stats()

    def load_orders(self):
        """Загрузка заказов из VIEW"""
        for item in self.orders_tree.get_children():
            self.orders_tree.delete(item)

        try:
            orders = OrderService.get_orders_from_view()
            status_filter = self.status_filter.get()

            count = 0
            for order in orders:
                if status_filter != 'Все' and order['status'] != status_filter:
                    continue
                self.orders_tree.insert('', tk.END, values=(
                    order['order_id'],
                    order['order_date'],
                    order['client_name'],
                    order['status'],
                    f"{order['total_amount']:,.2f}",
                    order['manager_name']
                ))
                count += 1

            self.orders_status.config(text=f"📋 Всего заказов: {count}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить заказы: {e}")

    def load_clients(self):
        """Загрузка клиентов"""
        for item in self.clients_tree.get_children():
            self.clients_tree.delete(item)

        conn = DBConnection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT client_id, full_name, phone, email FROM clients ORDER BY full_name")
            for row in cursor.fetchall():
                self.clients_tree.insert('', tk.END, values=(
                    row['client_id'], row['full_name'], row['phone'], row['email']
                ))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить клиентов: {e}")
        finally:
            conn.close()

    def load_products(self):
        """Загрузка товаров"""
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)

        conn = DBConnection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT product_id, name, price, stock_quantity FROM products ORDER BY name")
            for row in cursor.fetchall():
                self.products_tree.insert('', tk.END, values=(
                    row['product_id'], row['name'], f"{row['price']:,.2f}", row['stock_quantity']
                ))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить товары: {e}")
        finally:
            conn.close()

    def load_stats(self):
        """Загрузка статистики из VIEW"""
        for item in self.stats_tree.get_children():
            self.stats_tree.delete(item)

        try:
            stats = OrderService.get_manager_stats()
            for stat in stats:
                self.stats_tree.insert('', tk.END, values=(
                    stat['manager_name'],
                    stat['orders_count'],
                    f"{stat['total_sum']:,.2f}",
                    f"{stat['avg_order_amount']:,.2f}"
                ))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить статистику: {e}")

    def create_order(self):
        """Создание нового заказа"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Новый заказ")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="Создание нового заказа", font=('Arial', 12, 'bold')).pack(pady=10)

        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        # Выбор клиента
        ttk.Label(frame, text="Клиент:").grid(row=0, column=0, sticky=tk.W, pady=5)
        client_combo = ttk.Combobox(frame, width=30)
        client_combo.grid(row=0, column=1, pady=5)

        # Загрузка клиентов в комбобокс
        conn = DBConnection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT client_id, full_name FROM clients ORDER BY full_name")
            clients = cursor.fetchall()
            client_list = [f"{c['client_id']} - {c['full_name']}" for c in clients]
            client_combo['values'] = client_list
        finally:
            conn.close()

        def save_order():
            if not client_combo.get():
                messagebox.showwarning("Внимание", "Выберите клиента")
                return

            client_id = int(client_combo.get().split(' - ')[0])

            try:
                conn = DBConnection.get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO orders (client_id, manager_id, status, total_amount)
                    VALUES (%s, %s, 'new', 0.00)
                """, (client_id, AppSession.get_user_id()))
                conn.commit()

                new_id = cursor.lastrowid
                messagebox.showinfo("Успех", f"Заказ №{new_id} создан")
                dialog.destroy()
                self.load_orders()

            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось создать заказ: {e}")
            finally:
                conn.close()

        ttk.Button(frame, text="Создать", command=save_order).grid(row=2, column=0, columnspan=2, pady=20)
        ttk.Button(frame, text="Отмена", command=dialog.destroy).grid(row=3, column=0, columnspan=2)

    def change_status(self):
        """Смена статуса заказа"""
        selected = self.orders_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите заказ")
            return

        order_id = self.orders_tree.item(selected[0])['values'][0]

        # Диалог выбора статуса
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Смена статуса заказа №{order_id}")
        dialog.geometry("350x250")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text=f"Заказ №{order_id}", font=('Arial', 12, 'bold')).pack(pady=10)

        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Новый статус:").grid(row=0, column=0, sticky=tk.W, pady=5)

        # Ограничение доступных статусов в зависимости от роли
        if AppSession.is_storekeeper():
            statuses = ['shipped']
        else:
            statuses = ['in_work', 'shipped', 'completed', 'cancelled']

        status_combo = ttk.Combobox(frame, values=statuses, width=20)
        status_combo.grid(row=0, column=1, pady=5)
        status_combo.set(statuses[0])

        ttk.Label(frame, text="Примечание:").grid(row=1, column=0, sticky=tk.W, pady=5)
        note_text = tk.Text(frame, width=30, height=5)
        note_text.grid(row=1, column=1, pady=5)

        def apply():
            new_status = status_combo.get()
            if not new_status:
                messagebox.showwarning("Внимание", "Выберите статус")
                return

            try:
                OrderService.change_order_status(order_id, new_status, AppSession.get_user_id())
                messagebox.showinfo("Успех", f"Статус заказа №{order_id} изменён на '{new_status}'")
                dialog.destroy()
                self.load_orders()
                self.load_stats()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

        ttk.Button(frame, text="Применить", command=apply).grid(row=2, column=0, columnspan=2, pady=20)
        ttk.Button(frame, text="Отмена", command=dialog.destroy).grid(row=3, column=0, columnspan=2)

    def view_order_details(self):
        """Просмотр деталей заказа"""
        selected = self.orders_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите заказ")
            return

        order_id = self.orders_tree.item(selected[0])['values'][0]

        dialog = tk.Toplevel(self.root)
        dialog.title(f"Детали заказа №{order_id}")
        dialog.geometry("600x400")
        dialog.transient(self.root)

        # Загрузка позиций заказа
        conn = DBConnection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT oi.order_item_id, p.name, oi.quantity, oi.price_at_moment,
                       (oi.quantity * oi.price_at_moment) as total
                FROM order_items oi
                JOIN products p ON oi.product_id = p.product_id
                WHERE oi.order_id = %s
            """, (order_id,))
            items = cursor.fetchall()

            # Таблица позиций
            columns = ('name', 'quantity', 'price', 'total')
            tree = ttk.Treeview(dialog, columns=columns, show='headings', height=15)
            tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            tree.heading('name', text='Товар')
            tree.heading('quantity', text='Кол-во')
            tree.heading('price', text='Цена')
            tree.heading('total', text='Сумма')

            tree.column('name', width=300)
            tree.column('quantity', width=80)
            tree.column('price', width=100)
            tree.column('total', width=100)

            total_sum = 0
            for item in items:
                tree.insert('', tk.END, values=(
                    item['name'],
                    item['quantity'],
                    f"{item['price_at_moment']:,.2f}",
                    f"{item['total']:,.2f}"
                ))
                total_sum += item['total']

            # Итоговая сумма
            ttk.Label(dialog, text=f"Итого: {total_sum:,.2f} руб.",
                      font=('Arial', 12, 'bold')).pack(pady=10)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить детали: {e}")
        finally:
            conn.close()

        ttk.Button(dialog, text="Закрыть", command=dialog.destroy).pack(pady=10)

    def delete_order(self):
        """Удаление заказа"""
        selected = self.orders_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите заказ")
            return

        order_id = self.orders_tree.item(selected[0])['values'][0]

        result = messagebox.askyesno(
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить заказ №{order_id}?\n\n"
            "Вместе с заказом будут удалены все его позиции.",
            icon='warning'
        )

        if not result:
            return

        conn = DBConnection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM orders WHERE order_id = %s", (order_id,))
            conn.commit()

            messagebox.showinfo("Успех", f"Заказ №{order_id} удалён")
            self.load_orders()
            self.load_stats()

        except Exception as e:
            conn.rollback()
            messagebox.showerror("Ошибка", f"Не удалось удалить заказ: {e}")
        finally:
            conn.close()

    def add_client(self):
        """Добавление нового клиента"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавление клиента")
        dialog.geometry("400x250")
        dialog.transient(self.root)
        dialog.grab_set()

        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Наименование:").grid(row=0, column=0, sticky=tk.W, pady=5)
        entry_name = ttk.Entry(frame, width=30)
        entry_name.grid(row=0, column=1, pady=5)

        ttk.Label(frame, text="Телефон:").grid(row=1, column=0, sticky=tk.W, pady=5)
        entry_phone = ttk.Entry(frame, width=30)
        entry_phone.grid(row=1, column=1, pady=5)

        ttk.Label(frame, text="Email:").grid(row=2, column=0, sticky=tk.W, pady=5)
        entry_email = ttk.Entry(frame, width=30)
        entry_email.grid(row=2, column=1, pady=5)

        def save():
            name = entry_name.get().strip()
            phone = entry_phone.get().strip()
            email = entry_email.get().strip()

            if not name or not email:
                messagebox.showwarning("Внимание", "Заполните наименование и email")
                return

            conn = DBConnection.get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO clients (full_name, phone, email)
                    VALUES (%s, %s, %s)
                """, (name, phone, email))
                conn.commit()

                messagebox.showinfo("Успех", f"Клиент '{name}' добавлен")
                dialog.destroy()
                self.load_clients()

            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось добавить клиента: {e}")
            finally:
                conn.close()

        ttk.Button(frame, text="Сохранить", command=save).grid(row=3, column=0, columnspan=2, pady=20)
        ttk.Button(frame, text="Отмена", command=dialog.destroy).grid(row=4, column=0, columnspan=2)

    def edit_client(self):
        """Редактирование клиента"""
        selected = self.clients_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите клиента")
            return

        values = self.clients_tree.item(selected[0])['values']
        client_id = values[0]
        current_name = values[1]
        current_phone = values[2] if values[2] else ""
        current_email = values[3]

        dialog = tk.Toplevel(self.root)
        dialog.title(f"Редактирование клиента ID {client_id}")
        dialog.geometry("400x250")
        dialog.transient(self.root)
        dialog.grab_set()

        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Наименование:").grid(row=0, column=0, sticky=tk.W, pady=5)
        entry_name = ttk.Entry(frame, width=30)
        entry_name.insert(0, current_name)
        entry_name.grid(row=0, column=1, pady=5)

        ttk.Label(frame, text="Телефон:").grid(row=1, column=0, sticky=tk.W, pady=5)
        entry_phone = ttk.Entry(frame, width=30)
        entry_phone.insert(0, current_phone)
        entry_phone.grid(row=1, column=1, pady=5)

        ttk.Label(frame, text="Email:").grid(row=2, column=0, sticky=tk.W, pady=5)
        entry_email = ttk.Entry(frame, width=30)
        entry_email.insert(0, current_email)
        entry_email.grid(row=2, column=1, pady=5)

        def save():
            name = entry_name.get().strip()
            phone = entry_phone.get().strip()
            email = entry_email.get().strip()

            if not name or not email:
                messagebox.showwarning("Внимание", "Заполните наименование и email")
                return

            conn = DBConnection.get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE clients SET full_name = %s, phone = %s, email = %s
                    WHERE client_id = %s
                """, (name, phone, email, client_id))
                conn.commit()

                messagebox.showinfo("Успех", f"Клиент ID {client_id} обновлён")
                dialog.destroy()
                self.load_clients()

            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось обновить клиента: {e}")
            finally:
                conn.close()

        ttk.Button(frame, text="Сохранить", command=save).grid(row=3, column=0, columnspan=2, pady=20)
        ttk.Button(frame, text="Отмена", command=dialog.destroy).grid(row=4, column=0, columnspan=2)

    def delete_client(self):
        """Удаление клиента"""
        selected = self.clients_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите клиента")
            return

        values = self.clients_tree.item(selected[0])['values']
        client_id = values[0]
        client_name = values[1]

        result = messagebox.askyesno(
            "Подтверждение удаления",
            f"Удалить клиента '{client_name}'?\n\n"
            "Внимание! Если у клиента есть заказы, удаление будет невозможно.",
            icon='warning'
        )

        if not result:
            return

        conn = DBConnection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM clients WHERE client_id = %s", (client_id,))
            conn.commit()

            messagebox.showinfo("Успех", f"Клиент '{client_name}' удалён")
            self.load_clients()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить клиента: {e}")
        finally:
            conn.close()

    def add_product(self):
        """Добавление нового товара"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавление товара")
        dialog.geometry("400x250")
        dialog.transient(self.root)
        dialog.grab_set()

        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Наименование:").grid(row=0, column=0, sticky=tk.W, pady=5)
        entry_name = ttk.Entry(frame, width=30)
        entry_name.grid(row=0, column=1, pady=5)

        ttk.Label(frame, text="Цена (руб.):").grid(row=1, column=0, sticky=tk.W, pady=5)
        entry_price = ttk.Entry(frame, width=30)
        entry_price.grid(row=1, column=1, pady=5)

        ttk.Label(frame, text="Остаток на складе:").grid(row=2, column=0, sticky=tk.W, pady=5)
        entry_stock = ttk.Entry(frame, width=30)
        entry_stock.insert(0, "0")
        entry_stock.grid(row=2, column=1, pady=5)

        def save():
            name = entry_name.get().strip()
            try:
                price = float(entry_price.get().replace(',', '.'))
                stock = int(entry_stock.get())
            except ValueError:
                messagebox.showwarning("Внимание", "Введите корректные цену и остаток")
                return

            if not name or price <= 0:
                messagebox.showwarning("Внимание", "Заполните наименование и цену")
                return

            conn = DBConnection.get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO products (name, price, stock_quantity)
                    VALUES (%s, %s, %s)
                """, (name, price, stock))
                conn.commit()

                messagebox.showinfo("Успех", f"Товар '{name}' добавлен")
                dialog.destroy()
                self.load_products()

            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось добавить товар: {e}")
            finally:
                conn.close()

        ttk.Button(frame, text="Сохранить", command=save).grid(row=3, column=0, columnspan=2, pady=20)
        ttk.Button(frame, text="Отмена", command=dialog.destroy).grid(row=4, column=0, columnspan=2)

    def edit_product(self):
        """Редактирование товара"""
        selected = self.products_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите товар")
            return

        values = self.products_tree.item(selected[0])['values']
        product_id = values[0]
        current_name = values[1]
        current_price = float(values[2].replace(',', '')) if values[2] else 0
        current_stock = values[3]

        dialog = tk.Toplevel(self.root)
        dialog.title(f"Редактирование товара ID {product_id}")
        dialog.geometry("400x250")
        dialog.transient(self.root)
        dialog.grab_set()

        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Наименование:").grid(row=0, column=0, sticky=tk.W, pady=5)
        entry_name = ttk.Entry(frame, width=30)
        entry_name.insert(0, current_name)
        entry_name.grid(row=0, column=1, pady=5)

        ttk.Label(frame, text="Цена (руб.):").grid(row=1, column=0, sticky=tk.W, pady=5)
        entry_price = ttk.Entry(frame, width=30)
        entry_price.insert(0, str(current_price))
        entry_price.grid(row=1, column=1, pady=5)

        ttk.Label(frame, text="Остаток на складе:").grid(row=2, column=0, sticky=tk.W, pady=5)
        entry_stock = ttk.Entry(frame, width=30)
        entry_stock.insert(0, str(current_stock))
        entry_stock.grid(row=2, column=1, pady=5)

        def save():
            name = entry_name.get().strip()
            try:
                price = float(entry_price.get().replace(',', '.'))
                stock = int(entry_stock.get())
            except ValueError:
                messagebox.showwarning("Внимание", "Введите корректные цену и остаток")
                return

            if not name or price <= 0:
                messagebox.showwarning("Внимание", "Заполните наименование и цену")
                return

            conn = DBConnection.get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE products SET name = %s, price = %s, stock_quantity = %s
                    WHERE product_id = %s
                """, (name, price, stock, product_id))
                conn.commit()

                messagebox.showinfo("Успех", f"Товар '{name}' обновлён")
                dialog.destroy()
                self.load_products()

            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось обновить товар: {e}")
            finally:
                conn.close()

        ttk.Button(frame, text="Сохранить", command=save).grid(row=3, column=0, columnspan=2, pady=20)
        ttk.Button(frame, text="Отмена", command=dialog.destroy).grid(row=4, column=0, columnspan=2)

    def delete_product(self):
        """Удаление товара"""
        selected = self.products_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите товар")
            return

        values = self.products_tree.item(selected[0])['values']
        product_id = values[0]
        product_name = values[1]

        result = messagebox.askyesno(
            "Подтверждение удаления",
            f"Удалить товар '{product_name}'?\n\n"
            "Внимание! Если товар есть в заказах, удаление будет невозможно.",
            icon='warning'
        )

        if not result:
            return

        conn = DBConnection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM products WHERE product_id = %s", (product_id,))
            conn.commit()

            messagebox.showinfo("Успех", f"Товар '{product_name}' удалён")
            self.load_products()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить товар: {e}")
        finally:
            conn.close()

    def logout(self):
        """Выход из системы"""
        AppSession.clear()
        for widget in self.root.winfo_children():
            widget.destroy()
        self.show_login()


# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()