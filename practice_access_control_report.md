# Практическая работа: представления и управление доступом в PostgreSQL

## Цель работы

Освоить создание пользователей и групповых ролей PostgreSQL, выдачу табличных и столбцовых привилегий, создание однотабличных и многотабличных представлений, реализацию вставки через многотабличное представление, а также проверку контроля доступа от имени ограниченного пользователя.

Работа выполняется с базой данных `tourism_firm`, созданной в первом семестре.

Исполняемый скрипт настройки находится в файле:

```text
/Users/lubovgoraeva/Downloads/practice_access_control.sql
```

## 1. Созданные пользователи и роли

В работе используются:

- `test` — пользователь с правом входа в PostgreSQL;
- `hotel_view_editor` — групповая роль без права самостоятельного входа.

Пользователь создаётся следующим образом:

```sql
CREATE ROLE test LOGIN;

ALTER ROLE test
WITH LOGIN INHERIT
PASSWORD 'Test_2026_ChangeMe!';
```

Групповая роль создаётся без возможности входа:

```sql
CREATE ROLE hotel_view_editor NOLOGIN;
```

Пользователю предоставляется доступ к базе и схеме:

```sql
GRANT CONNECT ON DATABASE tourism_firm TO test;
GRANT USAGE ON SCHEMA public TO test;
```

`CONNECT` разрешает подключаться к базе `tourism_firm`, а `USAGE` разрешает обращаться к объектам схемы `public`. Эти привилегии сами по себе не дают доступа к данным таблиц.

## 2. Права на таблицы

### 2.1. Полные права SELECT, INSERT и UPDATE

На таблицу `destinations` пользователь получает полные права чтения, вставки и изменения:

```sql
GRANT SELECT, INSERT, UPDATE
ON TABLE public.destinations
TO test;
```

Для работы автоматического identity-идентификатора дополнительно выдаются права на последовательность:

```sql
GRANT USAGE, SELECT
ON SEQUENCE public.destinations_destination_id_seq
TO test;
```

### 2.2. SELECT и UPDATE только выбранных столбцов

В таблице `hotels` пользователь может читать только четыре столбца:

```sql
GRANT SELECT (
    hotel_id,
    name,
    category,
    meal_type
)
ON TABLE public.hotels
TO test;
```

Изменять разрешено только `category` и `meal_type`:

```sql
GRANT UPDATE (category, meal_type)
ON TABLE public.hotels
TO test;
```

Адрес отеля и его направление остаются недоступными пользователю `test`.

### 2.3. Только SELECT

Для таблицы `tours` разрешено только чтение:

```sql
GRANT SELECT
ON TABLE public.tours
TO test;
```

Команды `INSERT`, `UPDATE` и `DELETE` для этой таблицы будут отклонены.

### 2.4. Сводная таблица прав

| Объект | SELECT | INSERT | UPDATE | DELETE |
|---|---:|---:|---:|---:|
| `destinations` | Все столбцы | Да | Все столбцы | Нет |
| `hotels` | `hotel_id`, `name`, `category`, `meal_type` | Нет | Только `category`, `meal_type` | Нет |
| `tours` | Все столбцы | Нет | Нет | Нет |
| `tourists` | Нет | Нет | Нет | Нет |
| `employees` | Нет | Нет | Нет | Нет |
| `bookings` | Нет напрямую | Нет напрямую | Нет | Нет |
| `payments` | Нет | Нет | Нет | Нет |

## 3. Однотабличные представления

### 3.1. Каталог доступных туров

```sql
CREATE OR REPLACE VIEW public.v_tour_catalog AS
SELECT
    tour_id,
    name AS tour_name,
    start_date,
    end_date,
    price,
    available_seats
FROM public.tours
WHERE available_seats > 0;
```

Представление упрощает получение доступных туров и не показывает внешние ключи `destination_id` и `hotel_id`.

Пользователю предоставляется право чтения:

```sql
GRANT SELECT
ON TABLE public.v_tour_catalog
TO test;
```

### 3.2. Представление для редактирования отелей

```sql
CREATE OR REPLACE VIEW public.v_hotel_editor AS
SELECT
    hotel_id,
    name AS hotel_name,
    category,
    meal_type
FROM public.hotels;
```

Представление скрывает адрес и направление отеля. Групповая роль получает право чтения и право изменения только двух столбцов:

```sql
GRANT SELECT
ON TABLE public.v_hotel_editor
TO hotel_view_editor;

GRANT UPDATE (category, meal_type)
ON TABLE public.v_hotel_editor
TO hotel_view_editor;
```

Роль назначается пользователю:

```sql
GRANT hotel_view_editor TO test;
```

Благодаря атрибуту `INHERIT` пользователь автоматически получает привилегии назначенной роли.

## 4. Многотабличное представление

```sql
CREATE OR REPLACE VIEW public.v_booking_details AS
SELECT
    b.booking_id,
    b.tourist_id,
    tr.full_name AS tourist_name,
    b.tour_id,
    t.name AS tour_name,
    b.employee_id,
    e.full_name AS employee_name,
    b.booking_date,
    b.number_of_people,
    b.status,
    b.discount
FROM public.bookings AS b
JOIN public.tourists AS tr
    ON tr.tourist_id = b.tourist_id
JOIN public.tours AS t
    ON t.tour_id = b.tour_id
JOIN public.employees AS e
    ON e.employee_id = b.employee_id;
```

Представление объединяет четыре таблицы и показывает бронирование в удобном виде. Контактные данные, паспорта туристов и электронные адреса сотрудников через него не раскрываются.

Обычное многотабличное представление автоматически не поддерживает вставку. Поэтому для него создан `INSTEAD OF INSERT`-триггер. Триггер принимает идентификаторы туриста, тура и сотрудника и добавляет строку в таблицу `bookings`.

Функция объявлена как `SECURITY DEFINER`, поэтому выполняется с правами владельца функции. Пользователю не требуется прямое право `INSERT` на `bookings`.

```sql
GRANT SELECT, INSERT
ON TABLE public.v_booking_details
TO test;
```

Полный код функции и триггера приведён в `practice_access_control.sql`.

## 5. Пошаговое выполнение в pgAdmin

### Шаг 1. Выполнение скрипта владельцем базы

1. Открыть pgAdmin.
2. Подключиться к локальному серверу под владельцем базы `lubovgoraeva`.
3. В дереве объектов выбрать `Databases → tourism_firm`.
4. Нажать правой кнопкой по базе и выбрать **Query Tool**.
5. Нажать кнопку открытия файла.
6. Выбрать:

```text
/Users/lubovgoraeva/Downloads/practice_access_control.sql
```

7. Выполнить скрипт кнопкой **Execute** или клавишей `F5`.
8. Вкладка **Messages** должна содержать сообщения `CREATE VIEW`, `CREATE FUNCTION`, `CREATE TRIGGER` и `GRANT` без ошибок.

Для создания пользователей текущая роль должна иметь атрибут `CREATEROLE` или быть суперпользователем. Локальный пользователь, создавший кластер Homebrew PostgreSQL, обычно обладает необходимыми правами.

### Шаг 2. Создание подключения пользователя test

1. В дереве pgAdmin нажать правой кнопкой по **Servers**.
2. Выбрать **Register → Server**.
3. Во вкладке **General** указать:

```text
Name: Tourism — test
```

4. Во вкладке **Connection** указать:

```text
Host name/address: 127.0.0.1
Port: 5432
Maintenance database: tourism_firm
Username: test
Password: Test_2026_ChangeMe!
```

5. Включить **Save password** и нажать **Save**.
6. Открыть для базы `tourism_firm` нового подключения отдельный **Query Tool**.

### Шаг 3. Проверка текущего пользователя

Выполнить от имени `test`:

```sql
SELECT
    current_user,
    session_user,
    current_database();
```

Ожидается:

```text
current_user     = test
session_user     = test
current_database = tourism_firm
```

Проверка членства в групповой роли:

```sql
SELECT pg_has_role(
    current_user,
    'hotel_view_editor',
    'member'
) AS is_hotel_editor;
```

Ожидаемый результат: `true`.

## 6. Проверка разрешённых операций

### 6.1. Таблица destinations

Чтение разрешено:

```sql
SELECT *
FROM destinations
ORDER BY destination_id;
```

Вставка разрешена:

```sql
INSERT INTO destinations (
    country,
    city,
    description,
    visa_required
)
VALUES (
    'Страна проверки доступа',
    'Город проверки доступа',
    'Запись добавлена пользователем test',
    FALSE
)
RETURNING *;
```

Изменение разрешено:

```sql
UPDATE destinations
SET description = 'Описание изменено пользователем test'
WHERE country = 'Страна проверки доступа'
  AND city = 'Город проверки доступа'
RETURNING *;
```

### 6.2. Разрешённые столбцы hotels

```sql
SELECT
    hotel_id,
    name,
    category,
    meal_type
FROM hotels
ORDER BY hotel_id;
```

Изменение разрешённого столбца:

```sql
UPDATE hotels
SET category = CASE
    WHEN category = 5 THEN 4
    ELSE 5
END
WHERE hotel_id = (
    SELECT MIN(hotel_id)
    FROM hotels
)
RETURNING hotel_id, name, category, meal_type;
```

### 6.3. Чтение tours

```sql
SELECT
    tour_id,
    name,
    price,
    available_seats
FROM tours
ORDER BY tour_id;
```

### 6.4. Чтение представлений

```sql
SELECT *
FROM v_tour_catalog
ORDER BY price;
```

```sql
SELECT *
FROM v_hotel_editor
ORDER BY hotel_id;
```

```sql
SELECT *
FROM v_booking_details
ORDER BY booking_id;
```

### 6.5. UPDATE представления через групповую роль

```sql
UPDATE v_hotel_editor
SET meal_type = 'завтрак'
WHERE hotel_id = (
    SELECT MIN(hotel_id)
    FROM v_hotel_editor
)
RETURNING *;
```

Изменение передаётся автоматически в базовую таблицу `hotels`, поскольку `v_hotel_editor` является простым однотабличным представлением.

### 6.6. INSERT в многотабличное представление

```sql
WITH booking_actor AS (
    SELECT
        tourist_id,
        employee_id
    FROM v_booking_details
    ORDER BY booking_id
    LIMIT 1
),
chosen_tour AS (
    SELECT tour_id
    FROM tours
    WHERE available_seats > 0
    ORDER BY available_seats DESC, tour_id
    LIMIT 1
)
INSERT INTO v_booking_details (
    tourist_id,
    tour_id,
    employee_id,
    booking_date,
    number_of_people,
    status,
    discount
)
SELECT
    a.tourist_id,
    t.tour_id,
    a.employee_id,
    CURRENT_DATE,
    1,
    'new',
    0
FROM booking_actor AS a
CROSS JOIN chosen_tour AS t
RETURNING *;
```

После выполнения новая строка должна появиться в `v_booking_details` и в базовой таблице `bookings`. При этом прямого права `INSERT` на `bookings` у пользователя `test` нет.

## 7. Проверка запрещённых операций

Каждый запрос следует выполнять отдельно. Если запрос запускается внутри явной транзакции и завершается ошибкой, перед следующей проверкой нужно выполнить `ROLLBACK`.

### 7.1. Недоступный столбец hotels

```sql
SELECT hotel_id, address
FROM hotels;
```

Ожидается ошибка:

```text
ERROR: permission denied for table hotels
```

Попытка изменить недоступный столбец:

```sql
UPDATE hotels
SET address = 'Новый адрес'
WHERE hotel_id = 1;
```

Операция должна быть отклонена.

### 7.2. Попытка изменить tours

```sql
UPDATE tours
SET price = price + 1000
WHERE tour_id = 1;
```

Ожидается ошибка отсутствия права `UPDATE`.

### 7.3. Попытка удалить направление

```sql
DELETE FROM destinations
WHERE country = 'Страна проверки доступа';
```

Операция должна быть отклонена, поскольку пользователю не выдавалось право `DELETE`.

### 7.4. Попытка обратиться к закрытой таблице

```sql
SELECT *
FROM tourists;
```

Пользователь не имеет прямого права чтения паспортных и контактных данных туристов, поэтому запрос должен завершиться ошибкой.

### 7.5. Попытка прямой вставки в bookings

```sql
INSERT INTO bookings (
    tourist_id,
    tour_id,
    employee_id,
    number_of_people,
    status,
    discount
)
VALUES (1, 1, 1, 1, 'new', 0);
```

Операция должна быть отклонена. Добавление бронирования разрешено только через `v_booking_details`.

## 8. Проверка прав через psql

В условии указана команда `/dp`, но правильная макрокоманда `psql` начинается с обратной косой черты:

```text
\dp
```

Подключение через терминал:

```bash
psql -h 127.0.0.1 -p 5432 -U test -d tourism_firm -W
```

После подключения:

```text
\dp
\dp public.destinations
\dp public.hotels
\dp public.tours
\dp public.v_tour_catalog
\dp public.v_hotel_editor
\dp public.v_booking_details
```

Команда `\dp` и её синоним `\z` показывают права таблиц, представлений, последовательностей и других объектов.

Формат записи ACL:

```text
пользователь=флаги/кто_выдал
```

Например:

```text
test=arw/lubovgoraeva
```

означает, что пользователь `test` получил `INSERT`, `SELECT` и `UPDATE`, а права выданы пользователем `lubovgoraeva`.

### Флаги доступа psql

| Флаг | Привилегия | Значение |
|---|---|---|
| `r` | `SELECT` | Чтение строк |
| `a` | `INSERT` | Добавление строк |
| `w` | `UPDATE` | Изменение строк |
| `d` | `DELETE` | Удаление строк |
| `D` | `TRUNCATE` | Полная очистка таблицы |
| `x` | `REFERENCES` | Создание внешних ключей, ссылающихся на объект |
| `t` | `TRIGGER` | Создание триггеров |
| `X` | `EXECUTE` | Выполнение функции или процедуры |
| `U` | `USAGE` | Использование схемы, последовательности или другого объекта |
| `C` | `CREATE` | Создание объектов |
| `c` | `CONNECT` | Подключение к базе |
| `T` | `TEMPORARY` | Создание временных таблиц |
| `*` | Grant option | Получатель может выдавать соответствующее право другим ролям |

Полный набор типичных табличных прав:

```text
arwdDxt
```

означает `INSERT`, `SELECT`, `UPDATE`, `DELETE`, `TRUNCATE`, `REFERENCES` и `TRIGGER`.

Столбцовые права могут отображаться отдельно возле конкретных столбцов таблицы.

Дополнительные полезные команды:

```text
\du                 -- список пользователей и ролей
\l+                 -- базы данных и права на них
\dn+                -- схемы и права на них
\d+ public.hotels   -- структура таблицы и столбцовые права
```

## 9. Результаты проверки

| Проверка | Ожидаемый результат |
|---|---|
| Подключение `test` к `tourism_firm` | Разрешено |
| `SELECT`, `INSERT`, `UPDATE` для `destinations` | Разрешены |
| `DELETE` для `destinations` | Запрещён |
| Чтение разрешённых столбцов `hotels` | Разрешено |
| Чтение `hotels.address` | Запрещено |
| Изменение `hotels.category` | Разрешено |
| Изменение `hotels.address` | Запрещено |
| Чтение `tours` | Разрешено |
| Изменение `tours` | Запрещено |
| Чтение `v_tour_catalog` | Разрешено напрямую |
| Чтение `v_hotel_editor` | Разрешено через роль |
| Изменение `category`, `meal_type` через `v_hotel_editor` | Разрешено через роль |
| Вставка через `v_booking_details` | Разрешена триггером |
| Прямая вставка в `bookings` | Запрещена |
| Прямое чтение `tourists` | Запрещено |

## 10. Вывод

В ходе работы создан ограниченный пользователь `test` и групповая роль `hotel_view_editor`. Для разных таблиц назначены различные наборы прав: полные права `SELECT`, `INSERT`, `UPDATE`; столбцовые права `SELECT` и `UPDATE`; а также право только на чтение.

Однотабличные представления используются для упрощения запросов и ограничения доступного набора столбцов. Многотабличное представление объединяет сведения о бронировании, туристе, туре и сотруднике, не раскрывая паспортные и контактные данные.

Вставка в многотабличное представление реализована через `INSTEAD OF INSERT`-триггер с контролируемой функцией `SECURITY DEFINER`. Пользователь может создавать бронирования через представление, но не имеет прямого доступа на изменение базовой таблицы `bookings`.

Проверки разрешённых и запрещённых операций подтверждают, что PostgreSQL корректно применяет табличные, столбцовые и ролевые привилегии.
