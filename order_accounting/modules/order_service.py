from modules.db_config import DBConnection


class OrderService:

    @staticmethod
    def change_order_status(order_id: int, new_status: str, user_id: int):
        """Вызов процедуры sp_change_order_status"""
        conn = DBConnection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.callproc('sp_change_order_status', (order_id, new_status, user_id))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def recalc_order_total(order_id: int):
        """Вызов процедуры sp_recalc_order_total"""
        conn = DBConnection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.callproc('sp_recalc_order_total', (order_id,))
            conn.commit()
            return True
        finally:
            conn.close()

    @staticmethod
    def add_order_item(order_id: int, product_id: int, quantity: int):
        """Вызов процедуры sp_add_order_item"""
        conn = DBConnection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.callproc('sp_add_order_item', (order_id, product_id, quantity))
            conn.commit()
            return True
        finally:
            conn.close()

    @staticmethod
    def get_orders_from_view():
        """Получение данных из VIEW v_orders_full"""
        conn = DBConnection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM v_orders_full")
            return cursor.fetchall()
        finally:
            conn.close()

    @staticmethod
    def get_manager_stats():
        """Получение статистики из VIEW v_manager_stats"""
        conn = DBConnection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM v_manager_stats")
            return cursor.fetchall()
        finally:
            conn.close()