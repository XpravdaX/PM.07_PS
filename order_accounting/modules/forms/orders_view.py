import tkinter as tk
from tkinter import ttk, messagebox
from db_config import DBConnection


class OrdersForm:
    """Форма для отображения заказов из VIEW v_orders_full"""

    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Заголовок
        lbl_title = ttk.Label(self.frame, text="Список заказов", font=('Arial', 16, 'bold'))
        lbl_title.pack(pady=10)

        # Фрейм для фильтров
        filter_frame = ttk.LabelFrame(self.frame, text="Фильтр по статусу")
        filter_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(filter_frame, text="Статус:").pack(side=tk.LEFT, padx=5)
        self.status_filter = ttk.Combobox(filter_frame,
                                          values=['Все', 'new', 'in_work', 'shipped', 'completed', 'cancelled'],
                                          width=20)
        self.status_filter.pack(side=tk.LEFT, padx=5)
        self.status_filter.set('Все')

        btn_filter = ttk.Button(filter_frame, text="Применить фильтр", command=self.load_orders)
        btn_filter.pack(side=tk.LEFT, padx=10)

        btn_refresh = ttk.Button(filter_frame, text="Обновить", command=self.load_orders)
        btn_refresh.pack(side=tk.LEFT, padx=5)

        # Таблица (Treeview)
        columns = ('order_id', 'order_date', 'client_name', 'status', 'total_amount', 'manager_name')
        self.tree = ttk.Treeview(self.frame, columns=columns, show='headings', height=15)

        self.tree.heading('order_id', text='№ заказа')
        self.tree.heading('order_date', text='Дата')
        self.tree.heading('client_name', text='Клиент')
        self.tree.heading('status', text='Статус')
        self.tree.heading('total_amount', text='Сумма (руб.)')
        self.tree.heading('manager_name', text='Менеджер')

        self.tree.column('order_id', width=80)
        self.tree.column('order_date', width=150)
        self.tree.column('client_name', width=200)
        self.tree.column('status', width=100)
        self.tree.column('total_amount', width=120)
        self.tree.column('manager_name', width=150)

        scrollbar = ttk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=10)

        self.load_orders()

    def load_orders(self):
        """Загрузка данных из VIEW v_orders_full"""
        for row in self.tree.get_children():
            self.tree.delete(row)

        status = self.status_filter.get()

        conn = DBConnection.get_connection()
        if not conn:
            messagebox.showerror("Ошибка", "Не удалось подключиться к базе данных")
            return

        try:
            cursor = conn.cursor()

            if status == 'Все':
                query = """
                    SELECT order_id, order_date, client_name, status, total_amount, manager_name
                    FROM v_orders_full
                    ORDER BY order_date DESC
                """
                cursor.execute(query)
            else:
                query = """
                    SELECT order_id, order_date, client_name, status, total_amount, manager_name
                    FROM v_orders_full
                    WHERE status = %s
                    ORDER BY order_date DESC
                """
                cursor.execute(query, (status,))

            rows = cursor.fetchall()

            for row in rows:
                self.tree.insert('', tk.END, values=(
                    row[0],  # order_id
                    row[1].strftime('%Y-%m-%d %H:%M') if row[1] else '',
                    row[2],  # client_name
                    row[3],  # status
                    f"{row[4]:,.2f}" if row[4] else "0.00",
                    row[5]  # manager_name
                ))

            cursor.close()
            messagebox.showinfo("Информация", f"Загружено {len(rows)} заказов")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки данных: {e}")
        finally:
            conn.close()