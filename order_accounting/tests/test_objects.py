from modules.order_service import OrderService


def test_views():
    print("=" * 50)
    print("Тестирование VIEW v_orders_full")
    print("=" * 50)
    orders = OrderService.get_orders_from_view()
    for order in orders:
        print(f"№{order['order_id']} | {order['client_name']} | {order['status']} | {order['total_amount']:.2f} руб.")

    print("\n" + "=" * 50)
    print("Тестирование VIEW v_manager_stats")
    print("=" * 50)
    stats = OrderService.get_manager_stats()
    for stat in stats:
        print(f"{stat['manager_name']}: {stat['orders_count']} заказов, сумма {stat['total_sum']:.2f} руб.")


def test_procedures():
    print("\n" + "=" * 50)
    print("Тестирование процедур")
    print("=" * 50)

    # Добавление позиции
    print("1. Добавляем позицию в заказ №1...")
    OrderService.add_order_item(1, 2, 1)

    # Пересчёт суммы
    print("2. Пересчитываем сумму заказа №1...")
    OrderService.recalc_order_total(1)

    # Смена статуса
    print("3. Меняем статус заказа №1 на 'shipped'...")
    OrderService.change_order_status(1, 'shipped', 2)

    # Проверка
    orders = OrderService.get_orders_from_view()
    for order in orders:
        if order['order_id'] == 1:
            print(f"\n✅ Заказ №{order['order_id']}: статус '{order['status']}', сумма {order['total_amount']:.2f} руб.")


if __name__ == "__main__":
    test_views()
    test_procedures()