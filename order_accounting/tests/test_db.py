import pymysql


def test_connection():
    try:
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='',
            database='order_accounting',
            charset='utf8mb4'
        )
        print("✅ Подключение к MySQL успешно!")

        cursor = conn.cursor()

        # Проверка таблиц
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print("\n--- Таблицы в базе данных ---")
        for table in tables:
            print(f"  - {table[0]}")

        # Проверка количества заказов
        cursor.execute("SELECT COUNT(*) FROM orders")
        count = cursor.fetchone()[0]
        print(f"\n📦 Количество заказов: {count}")

        # Проверка данных из orders
        cursor.execute("""
            SELECT o.order_id, c.full_name, o.status, o.total_amount 
            FROM orders o
            JOIN clients c ON o.client_id = c.client_id
        """)
        rows = cursor.fetchall()
        print("\n--- Список заказов ---")
        for row in rows:
            print(f"  Заказ №{row[0]}: {row[1]} | {row[2]} | {row[3]:.2f} руб.")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    test_connection()