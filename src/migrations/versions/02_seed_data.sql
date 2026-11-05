-- 02_seed_data.sql
-- Первичное наполнение базы данных ConcertHub данными из ЛР №2 и ЛР №3

-- 1. Исполнители (Artist) - 7 записей
INSERT INTO public.artist (artist_id, stage_name, leader_full_name, music_genre) VALUES
(1, 'Дора', 'Шиханова Дарья Сергеевна', 'Pop'),
(2, 'МакSим', 'Абросимова Марина Сергеевна', 'Pop'),
(3, 'Мэйби Бэйби', 'Клюева Александра Игоревна', 'Hyperpop'),
(4, 'Кис-кис', 'Белякова Юлия Владимировна', 'Punk Rock'),
(5, 'ЛСП', 'Савельев Олег Викторович', 'Hip-Hop'),
(6, 'Монеточка', 'Лизогубова Елизавета Андреевна', 'Indie Pop'),
(7, 'Дима Билан', 'Белан Виктор Николаевич', 'Pop')
ON CONFLICT (artist_id) DO NOTHING;
SELECT setval('public.artist_artist_id_seq', (SELECT COALESCE(MAX(artist_id), 1) FROM public.artist));

-- 2. Организаторы (Promoter) - 7 записей
INSERT INTO public.promoter (promoter_id, company_name, contact_person, contact_phone) VALUES
(1, 'ООО Северный звук', 'Иванов Петр Игоревич', '+7-911-111-11-11'),
(2, 'ООО Мегаконцерт', 'Сидорова Анна Владимировна', '+7-912-222-22-22'),
(3, 'Агентство Мьюзик Тур', 'Козлов Дмитрий Юрьевич', '+7-913-333-33-33'),
(4, 'ООО Звездный дождь', 'Морозова Елена Сергеевна', '+7-914-444-44-44'),
(5, 'Event Factory', 'Волков Артем Мартинович', '+7-915-555-55-55'),
(6, 'ООО Импульс', 'Некрасова Ольга Константиновна', '+7-916-666-66-66'),
(7, 'Группа Компаний Арт-Холл', 'Тарасов Игорь Иванович', '+7-917-777-77-77')
ON CONFLICT (promoter_id) DO NOTHING;
SELECT setval('public.promoter_promoter_id_seq', (SELECT COALESCE(MAX(promoter_id), 1) FROM public.promoter));

-- 3. Площадки (Venue) - 7 записей
INSERT INTO public.venue (venue_id, venue_name, city, address, total_capacity) VALUES
(1, 'VK Stadium', 'Москва', 'Ленинградский пр-т, 80к17', 4200),
(2, 'МТС Live Холл', 'Москва', 'Шоссе Энтузиастов, 5', 3500),
(3, 'Крокус Сити Холл', 'Красногорск', 'ул. Международная, 20', 6200),
(4, 'Ледовый Дворец', 'Санкт-Петербург', 'пр-т Пятилеток, 1', 12500),
(5, 'ГлавClub', 'Санкт-Петербург', 'наб. Обводного канала, 118', 1500),
(6, 'Tele-Club', 'Екатеринбург', 'ул. Каменный цветок, 1', 1200),
(7, 'Космонавт', 'Пермь', 'ул. Ленина, 56', 800)
ON CONFLICT (venue_id) DO NOTHING;
SELECT setval('public.venue_venue_id_seq', (SELECT COALESCE(MAX(venue_id), 1) FROM public.venue));

-- 4. Секторы зала (Hall_Sector) - 8 записей
INSERT INTO public.hall_sector (sector_id, sector_name, sector_capacity, sector_type, venue_id) VALUES
(1, 'Танцпол', 1500, 'танцевальный', 1),
(2, 'Фан-зона', 800, 'танцевальный', 1),
(3, 'VIP Ложа', 300, 'сидячий', 1),
(4, 'Партер', 1200, 'сидячий', 2),
(5, 'Балкон', 800, 'сидячий', 2),
(6, 'Танцпол', 1000, 'танцевальный', 3),
(7, 'Фан-зона', 500, 'танцевальный', 3),
(8, 'VIP Ложа', 250, 'сидячий', 3)
ON CONFLICT (sector_id) DO NOTHING;
SELECT setval('public.hall_sector_sector_id_seq', (SELECT COALESCE(MAX(sector_id), 1) FROM public.hall_sector));

-- 5. Зрители (Customer) - 8 записей (включая birth_date из ЛР №2)
INSERT INTO public.customer (customer_id, customer_full_name, email, phone_number, birth_date) VALUES
(1, 'Смирнов Алексей Игоревич', 'alex@mail.ru', '+7-921-123-45-67', '1995-03-15'),
(2, 'Петрова Екатерина Дмитриевна', 'katya@gmail.com', '+7-922-234-56-78', '1998-07-22'),
(3, 'Иванов Сергей Петрович', 'ivanov@yandex.ru', '+7-923-345-67-89', '2000-11-05'),
(4, 'Козлова Анна Николаевна', 'anna@rambler.ru', '+7-924-456-78-90', '1997-09-30'),
(5, 'Морозов Денис Андреевич', 'denis@mail.ru', '+7-925-567-89-01', '1999-01-12'),
(6, 'Волкова Мария Владимировна', 'masha@gmail.com', '+7-926-678-90-12', '2002-05-18'),
(7, 'Некрасов Павел Игоревич', 'pavel@yandex.ru', '+7-927-789-01-23', '1996-08-25'),
(8, 'Тарасова Ольга Сергеевна', 'olga@mail.ru', '+7-928-890-12-34', '2001-12-10')
ON CONFLICT (customer_id) DO NOTHING;
SELECT setval('public.customer_customer_id_seq', (SELECT COALESCE(MAX(customer_id), 1) FROM public.customer));

-- 6. Концерты (Concert) - 8 записей
INSERT INTO public.concert (concert_id, program_name, start_datetime, age_restriction, artist_id, venue_id, promoter_id) VALUES
(1, 'Мэйбилэнд Тур', '2026-11-20 19:00:00', '16+', 3, 1, 1),
(2, 'Сольный концерт МакSим', '2026-11-25 20:00:00', '12+', 2, 2, 2),
(3, 'Акустический вечер Доры', '2026-12-01 18:30:00', '12+', 1, 3, 3),
(4, 'Концерт ЛСП', '2026-12-05 21:00:00', '18+', 5, 4, 4),
(5, 'Хит-парад Кис-кис', '2026-12-10 20:00:00', '12+', 4, 5, 5),
(6, 'Симфоническое шоу Монеточки', '2026-12-15 19:30:00', '6+', 6, 6, 6),
(7, 'Лучшее за 20 лет Димы Билана', '2026-12-20 18:00:00', '0+', 7, 7, 7),
(8, 'Невероятная Дора', '2026-12-25 20:00:00', '12+', 1, 1, 1)
ON CONFLICT (concert_id) DO NOTHING;
SELECT setval('public.concert_concert_id_seq', (SELECT COALESCE(MAX(concert_id), 1) FROM public.concert));

-- 7. Заказы (Ticket_Order) - 8 записей
INSERT INTO public.ticket_order (order_id, order_datetime, order_status, total_amount, customer_id) VALUES
(1, '2026-11-10 12:30:00', 'Оплачен', 7500.00, 1),
(2, '2026-11-15 15:45:00', 'Оплачен', 4200.00, 2),
(3, '2026-11-20 10:20:00', 'Оплачен', 12800.00, 3),
(4, '2026-11-28 18:00:00', 'Оплачен', 6800.00, 4),
(5, '2026-12-01 09:15:00', 'Возврат', 0.00, 5),
(6, '2026-12-03 14:30:00', 'Оплачен', 9500.00, 6),
(7, '2026-12-08 11:40:00', 'Оплачен', 5200.00, 7),
(8, '2026-12-12 16:20:00', 'Оплачен', 11300.00, 8)
ON CONFLICT (order_id) DO NOTHING;
SELECT setval('public.ticket_order_order_id_seq', (SELECT COALESCE(MAX(order_id), 1) FROM public.ticket_order));

-- 8. Билеты (Ticket) - 16 записей
INSERT INTO public.ticket (ticket_id, barcode, price, ticket_status, concert_id, sector_id, order_id) VALUES
(1, 'TK-990101', 3500.00, 'Продан', 1, 1, 1),
(2, 'TK-990102', 4000.00, 'Продан', 1, 3, 1),
(3, 'TK-990201', 4200.00, 'Продан', 2, 4, 2),
(4, 'TK-990202', 6200.00, 'Доступен', 2, 5, NULL),
(5, 'TK-990301', 6800.00, 'Продан', 3, 6, 3),
(6, 'TK-990302', 6000.00, 'Продан', 3, 7, 3),
(7, 'TK-990401', 3400.00, 'Продан', 4, 2, 4),
(8, 'TK-990402', 3400.00, 'Продан', 4, 2, 4),
(9, 'TK-990501', 2800.00, 'Продан', 5, 1, 5),
(10, 'TK-990502', 3500.00, 'Аннулирован', 5, 3, 5),
(11, 'TK-990601', 4500.00, 'Продан', 6, 4, 6),
(12, 'TK-990602', 5000.00, 'Продан', 6, 5, 6),
(13, 'TK-990701', 2600.00, 'Продан', 7, 6, 7),
(14, 'TK-990702', 2600.00, 'Продан', 7, 7, 7),
(15, 'TK-990801', 5500.00, 'Продан', 8, 1, 8),
(16, 'TK-990802', 5800.00, 'Продан', 8, 3, 8)
ON CONFLICT (ticket_id) DO NOTHING;
SELECT setval('public.ticket_ticket_id_seq', (SELECT COALESCE(MAX(ticket_id), 1) FROM public.ticket));

-- 9. Зашифрованные данные audit.secret_data (ЛР №3)
-- Ключ: SHA-256('NazmievSushkoMavliaviev') = '29aaa1424afb8e8c740fb247a9d44723c8b5c82d8a12994ee2ed8b64e4410b63'
INSERT INTO audit.secret_data (username, secret_token) VALUES
('admin_user', pgp_sym_encrypt('token_admin_supersecret_access', '29aaa1424afb8e8c740fb247a9d44723c8b5c82d8a12994ee2ed8b64e4410b63')),
('petrov_staff', pgp_sym_encrypt('token_staff_manager_credentials', '29aaa1424afb8e8c740fb247a9d44723c8b5c82d8a12994ee2ed8b64e4410b63'))
ON CONFLICT DO NOTHING;
