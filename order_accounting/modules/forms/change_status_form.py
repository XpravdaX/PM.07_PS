import tkinter as tk
from tkinter import ttk, messagebox
from modules.order_service import OrderService


class ChangeStatusForm:
    """Форма для изменения статуса заказа через хранимую процедуру"""

    def __init__(self, parent, order_id: int, current_status: str, user_id: int):
        self.parent = parent
        self.order_id = order_id
        self.current_status = current_status
        self.user_id = user_id

        self.window = tk.Toplevel(parent)
        self.window.title(f"Изменение статуса заказа №{order_id}")
        self.window.geometry("400x250")
        self.window.resizable(False, False)

        # Центрирование окна
        self.window.transient(parent)
        self.window.grab_set()

        # Поля формы
        ttk.Label(self.window, text=f"Заказ №{order_id}", font=('Arial', 12, 'bold')).pack(pady=10)

        frame = ttk.Frame(self.window)
        frame.pack(pady=10)

        ttk.Label(frame, text="Текущий статус:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Label(frame, text=current_status, foreground="blue").grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(frame, text="Новый статус:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.status_var = tk.StringVar()
        self.status_combo = ttk.Combobox(frame, textvariable=self.status_var,
                                         values=['in_work', 'shipped', 'completed', 'cancelled'],
                                         width=20)
        self.status_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(frame, text="Примечание:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.note_text = tk.Text(frame, width=30, height=5)
        self.note_text.grid(row=2, column=1, padx=5, pady=5)

        # Кнопки
        btn_frame = ttk.Frame(self.window)
        btn_frame.pack(pady=20)

        ttk.Button(btn_frame, text="Сохранить", command=self.save_status).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Отмена", command=self.window.destroy).pack(side=tk.LEFT, padx=10)

    def save_status(self):
        """Сохранение нового статуса через хранимую процедуру"""
        new_status = self.status_var.get()

        if not new_status:
            messagebox.showwarning("Внимание", "Выберите новый статус")
            return

        try:
            OrderService.change_order_status(
                self.order_id,
                new_status,
                self.user_id,
                self.note_text.get("1.0", tk.END).strip()
            )

            messagebox.showinfo("Успех", f"Статус заказа №{self.order_id} изменён на '{new_status}'")
            self.window.destroy()

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))