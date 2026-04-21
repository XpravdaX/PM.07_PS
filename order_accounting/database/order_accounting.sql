-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Хост: 127.0.0.1:3306
-- Время создания: Апр 21 2026 г., 13:24
-- Версия сервера: 8.0.30
-- Версия PHP: 7.2.34

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- База данных: `order_accounting`
--

DELIMITER $$
--
-- Процедуры
--
CREATE DEFINER=`root`@`%` PROCEDURE `sp_add_order_item` (IN `p_order_id` INT, IN `p_product_id` INT, IN `p_quantity` INT)   BEGIN
    DECLARE v_price DECIMAL(10,2);
    
    -- Получить текущую цену товара
    SELECT price INTO v_price FROM products WHERE product_id = p_product_id;
    
    -- Добавить позицию
    INSERT INTO order_items (order_id, product_id, quantity, price_at_moment)
    VALUES (p_order_id, p_product_id, p_quantity, v_price);
    
    -- Пересчитать сумму заказа
    CALL sp_recalc_order_total(p_order_id);
END$$

CREATE DEFINER=`root`@`%` PROCEDURE `sp_change_order_status` (IN `p_order_id` INT, IN `p_new_status` VARCHAR(30), IN `p_user_id` INT)   BEGIN
    -- Обновить статус заказа
    UPDATE orders
    SET status = p_new_status
    WHERE order_id = p_order_id;
END$$

CREATE DEFINER=`root`@`%` PROCEDURE `sp_recalc_order_total` (IN `p_order_id` INT)   BEGIN
    DECLARE v_new_total DECIMAL(10,2);
    
    SELECT IFNULL(SUM(quantity * price_at_moment), 0)
    INTO v_new_total
    FROM order_items
    WHERE order_id = p_order_id;
    
    UPDATE orders
    SET total_amount = v_new_total
    WHERE order_id = p_order_id;
END$$

CREATE DEFINER=`root`@`%` PROCEDURE `sp_register_user` (IN `p_login` VARCHAR(80), IN `p_salt` VARCHAR(32), IN `p_hash` VARCHAR(64), IN `p_fullname` VARCHAR(150), IN `p_email` VARCHAR(150), IN `p_role_id` INT)   BEGIN
    -- Проверить, не занят ли логин
    IF EXISTS (SELECT 1 FROM users WHERE login = p_login) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Логин уже занят';
    END IF;
    
    -- Проверить, не занят ли email
    IF EXISTS (SELECT 1 FROM users WHERE email = p_email) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Email уже зарегистрирован';
    END IF;
    
    -- Вставить пользователя
    INSERT INTO users (login, password_salt, password_hash, full_name, email, role_id, is_active)
    VALUES (p_login, p_salt, p_hash, p_fullname, p_email, p_role_id, 1);
END$$

DELIMITER ;

-- --------------------------------------------------------

--
-- Структура таблицы `clients`
--

CREATE TABLE `clients` (
  `client_id` int NOT NULL,
  `full_name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `email` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Дамп данных таблицы `clients`
--

INSERT INTO `clients` (`client_id`, `full_name`, `phone`, `email`) VALUES
(1, 'ООО \"Компьютерный мир\"', '+7(495)123-45-67', 'info@compworld.ru'),
(2, 'ИП Смирнов Алексей', '+7(916)987-65-43', 'smirnov@mail.ru'),
(3, 'АО \"Рога и Копыта\"', '+7(495)555-33-22', 'roga@bk.ru');

-- --------------------------------------------------------

--
-- Структура таблицы `orders`
--

CREATE TABLE `orders` (
  `order_id` int NOT NULL,
  `client_id` int NOT NULL,
  `manager_id` int NOT NULL,
  `order_date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `status` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'new',
  `total_amount` decimal(10,2) NOT NULL DEFAULT '0.00'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Дамп данных таблицы `orders`
--

INSERT INTO `orders` (`order_id`, `client_id`, `manager_id`, `order_date`, `status`, `total_amount`) VALUES
(1, 1, 2, '2026-04-21 11:40:56', 'shipped', '273500.00'),
(2, 2, 2, '2026-04-19 11:40:56', 'in_work', '34400.00'),
(3, 1, 2, '2026-04-16 11:40:56', 'completed', '85000.00');

--
-- Триггеры `orders`
--
DELIMITER $$
CREATE TRIGGER `trg_log_status_change` AFTER UPDATE ON `orders` FOR EACH ROW BEGIN
    IF OLD.status <> NEW.status THEN
        INSERT INTO order_status_log (order_id, old_status, new_status)
        VALUES (OLD.order_id, OLD.status, NEW.status);
    END IF;
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Структура таблицы `order_items`
--

CREATE TABLE `order_items` (
  `order_item_id` int NOT NULL,
  `order_id` int NOT NULL,
  `product_id` int NOT NULL,
  `quantity` int NOT NULL,
  `price_at_moment` decimal(10,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Дамп данных таблицы `order_items`
--

INSERT INTO `order_items` (`order_item_id`, `order_id`, `product_id`, `quantity`, `price_at_moment`) VALUES
(1, 1, 1, 2, '85000.00'),
(2, 1, 3, 3, '2500.00'),
(3, 2, 2, 1, '32000.00'),
(4, 2, 4, 2, '1200.00'),
(5, 3, 1, 1, '85000.00'),
(6, 1, 2, 1, '32000.00'),
(7, 1, 2, 1, '32000.00'),
(8, 1, 2, 1, '32000.00');

-- --------------------------------------------------------

--
-- Структура таблицы `order_status_log`
--

CREATE TABLE `order_status_log` (
  `log_id` int NOT NULL,
  `order_id` int NOT NULL,
  `old_status` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `new_status` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `changed_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Дамп данных таблицы `order_status_log`
--

INSERT INTO `order_status_log` (`log_id`, `order_id`, `old_status`, `new_status`, `changed_at`) VALUES
(1, 1, 'in_work', 'shipped', '2026-04-21 12:40:04');

-- --------------------------------------------------------

--
-- Структура таблицы `products`
--

CREATE TABLE `products` (
  `product_id` int NOT NULL,
  `name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `price` decimal(10,2) NOT NULL,
  `stock_quantity` int NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Дамп данных таблицы `products`
--

INSERT INTO `products` (`product_id`, `name`, `price`, `stock_quantity`) VALUES
(1, 'Ноутбук Lenovo ThinkPad', '85000.00', 10),
(2, 'Монитор Dell 27\"', '32000.00', 5),
(3, 'Клавиатура Logitech', '2500.00', 20),
(4, 'Мышь беспроводная', '1200.00', 15);

-- --------------------------------------------------------

--
-- Структура таблицы `roles`
--

CREATE TABLE `roles` (
  `role_id` int NOT NULL,
  `role_name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Дамп данных таблицы `roles`
--

INSERT INTO `roles` (`role_id`, `role_name`) VALUES
(1, 'admin'),
(2, 'manager'),
(3, 'storekeeper');

-- --------------------------------------------------------

--
-- Структура таблицы `users`
--

CREATE TABLE `users` (
  `user_id` int NOT NULL,
  `login` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL,
  `full_name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `role_id` int NOT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `password_salt` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password_hash` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Дамп данных таблицы `users`
--

INSERT INTO `users` (`user_id`, `login`, `full_name`, `email`, `role_id`, `is_active`, `password_salt`, `password_hash`) VALUES
(1, 'admin', 'Соколов Андрей Игоревич', 'admin@techplus.ru', 1, 1, '', ''),
(2, 'manager1', 'Петрова Марина Сергеевна', 'manager@techplus.ru', 2, 1, '', ''),
(3, 'storek1', 'Иванов Пётр Николаевич', 'store@techplus.ru', 3, 1, '', ''),
(4, 'PRAVDA_SEMPAI', 'PRAVDA_SEMPAI', 'pravdasempai@mail.ru', 2, 1, 'c333bdff1a1ccdbc1075448148a230fb', '8529713862201737bdc114406f742f78f9376dedd3e457c708abb24c53d4c043');

-- --------------------------------------------------------

--
-- Дублирующая структура для представления `v_manager_stats`
-- (См. Ниже фактическое представление)
--
CREATE TABLE `v_manager_stats` (
`user_id` int
,`manager_name` varchar(150)
,`orders_count` bigint
,`total_sum` decimal(32,2)
,`avg_order_amount` decimal(14,6)
);

-- --------------------------------------------------------

--
-- Дублирующая структура для представления `v_orders_full`
-- (См. Ниже фактическое представление)
--
CREATE TABLE `v_orders_full` (
`order_id` int
,`order_date` varchar(21)
,`client_name` varchar(150)
,`client_phone` varchar(20)
,`status` varchar(30)
,`total_amount` decimal(10,2)
,`manager_name` varchar(150)
,`sort_date` datetime
);

-- --------------------------------------------------------

--
-- Структура для представления `v_manager_stats`
--
DROP TABLE IF EXISTS `v_manager_stats`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`%` SQL SECURITY DEFINER VIEW `v_manager_stats`  AS SELECT `u`.`user_id` AS `user_id`, `u`.`full_name` AS `manager_name`, count(`o`.`order_id`) AS `orders_count`, ifnull(sum(`o`.`total_amount`),0) AS `total_sum`, ifnull(avg(`o`.`total_amount`),0) AS `avg_order_amount` FROM (`users` `u` left join `orders` `o` on((`u`.`user_id` = `o`.`manager_id`))) WHERE (`u`.`role_id` = (select `roles`.`role_id` from `roles` where (`roles`.`role_name` = 'manager'))) GROUP BY `u`.`user_id`, `u`.`full_name``full_name`  ;

-- --------------------------------------------------------

--
-- Структура для представления `v_orders_full`
--
DROP TABLE IF EXISTS `v_orders_full`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`%` SQL SECURITY DEFINER VIEW `v_orders_full`  AS SELECT `o`.`order_id` AS `order_id`, date_format(`o`.`order_date`,'%Y-%m-%d %H:%i') AS `order_date`, `c`.`full_name` AS `client_name`, `c`.`phone` AS `client_phone`, `o`.`status` AS `status`, `o`.`total_amount` AS `total_amount`, `u`.`full_name` AS `manager_name`, `o`.`order_date` AS `sort_date` FROM ((`orders` `o` join `clients` `c` on((`o`.`client_id` = `c`.`client_id`))) join `users` `u` on((`o`.`manager_id` = `u`.`user_id`))) ORDER BY `o`.`order_date` AS `DESCdesc` ASC  ;

--
-- Индексы сохранённых таблиц
--

--
-- Индексы таблицы `clients`
--
ALTER TABLE `clients`
  ADD PRIMARY KEY (`client_id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Индексы таблицы `orders`
--
ALTER TABLE `orders`
  ADD PRIMARY KEY (`order_id`),
  ADD KEY `idx_orders_client` (`client_id`),
  ADD KEY `idx_orders_manager` (`manager_id`),
  ADD KEY `idx_orders_status` (`status`);

--
-- Индексы таблицы `order_items`
--
ALTER TABLE `order_items`
  ADD PRIMARY KEY (`order_item_id`),
  ADD KEY `idx_order_items_order` (`order_id`),
  ADD KEY `idx_order_items_product` (`product_id`);

--
-- Индексы таблицы `order_status_log`
--
ALTER TABLE `order_status_log`
  ADD PRIMARY KEY (`log_id`);

--
-- Индексы таблицы `products`
--
ALTER TABLE `products`
  ADD PRIMARY KEY (`product_id`);

--
-- Индексы таблицы `roles`
--
ALTER TABLE `roles`
  ADD PRIMARY KEY (`role_id`),
  ADD UNIQUE KEY `role_name` (`role_name`);

--
-- Индексы таблицы `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_id`),
  ADD UNIQUE KEY `login` (`login`),
  ADD UNIQUE KEY `email` (`email`),
  ADD KEY `role_id` (`role_id`);

--
-- AUTO_INCREMENT для сохранённых таблиц
--

--
-- AUTO_INCREMENT для таблицы `clients`
--
ALTER TABLE `clients`
  MODIFY `client_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT для таблицы `orders`
--
ALTER TABLE `orders`
  MODIFY `order_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT для таблицы `order_items`
--
ALTER TABLE `order_items`
  MODIFY `order_item_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT для таблицы `order_status_log`
--
ALTER TABLE `order_status_log`
  MODIFY `log_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT для таблицы `products`
--
ALTER TABLE `products`
  MODIFY `product_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT для таблицы `roles`
--
ALTER TABLE `roles`
  MODIFY `role_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT для таблицы `users`
--
ALTER TABLE `users`
  MODIFY `user_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- Ограничения внешнего ключа сохраненных таблиц
--

--
-- Ограничения внешнего ключа таблицы `orders`
--
ALTER TABLE `orders`
  ADD CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`client_id`) REFERENCES `clients` (`client_id`),
  ADD CONSTRAINT `orders_ibfk_2` FOREIGN KEY (`manager_id`) REFERENCES `users` (`user_id`);

--
-- Ограничения внешнего ключа таблицы `order_items`
--
ALTER TABLE `order_items`
  ADD CONSTRAINT `order_items_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `order_items_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`);

--
-- Ограничения внешнего ключа таблицы `users`
--
ALTER TABLE `users`
  ADD CONSTRAINT `users_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`role_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
