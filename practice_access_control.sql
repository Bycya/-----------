-- Практическая работа: представления и управление доступом
-- Выполнять от имени владельца базы tourism_firm или суперпользователя.

-- ================================================================
-- 1. Пользователь и групповая роль
-- ================================================================

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'test') THEN
        CREATE ROLE test LOGIN;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_roles WHERE rolname = 'hotel_view_editor'
    ) THEN
        CREATE ROLE hotel_view_editor NOLOGIN;
    END IF;
END;
$$;

-- Учебный пароль. Перед сдачей его можно заменить своим.
ALTER ROLE test WITH LOGIN INHERIT PASSWORD 'Test_2026_ChangeMe!';

GRANT CONNECT ON DATABASE tourism_firm TO test;
GRANT USAGE ON SCHEMA public TO test;


-- ================================================================
-- 2. Разные права на таблицы
-- ================================================================

-- Полные права SELECT, INSERT, UPDATE на destinations.
GRANT SELECT, INSERT, UPDATE
ON TABLE public.destinations
TO test;

-- Нужны для автоматического identity-идентификатора при INSERT.
GRANT USAGE, SELECT
ON SEQUENCE public.destinations_destination_id_seq
TO test;

-- SELECT только выбранных столбцов hotels.
GRANT SELECT (
    hotel_id,
    name,
    category,
    meal_type
)
ON TABLE public.hotels
TO test;

-- UPDATE только столбцов category и meal_type.
GRANT UPDATE (category, meal_type)
ON TABLE public.hotels
TO test;

-- На tours разрешено только чтение.
GRANT SELECT
ON TABLE public.tours
TO test;


-- ================================================================
-- 3. Однотабличные представления
-- ================================================================

-- Каталог туров без внутренних внешних ключей.
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

-- Представление для ограниченного редактирования данных отелей.
CREATE OR REPLACE VIEW public.v_hotel_editor AS
SELECT
    hotel_id,
    name AS hotel_name,
    category,
    meal_type
FROM public.hotels;

-- Прямое право test на чтение одного представления.
GRANT SELECT
ON TABLE public.v_tour_catalog
TO test;

-- Права назначаются групповой роли, а не напрямую пользователю.
GRANT SELECT
ON TABLE public.v_hotel_editor
TO hotel_view_editor;

GRANT UPDATE (category, meal_type)
ON TABLE public.v_hotel_editor
TO hotel_view_editor;

-- Включаем пользователя test в групповую роль.
GRANT hotel_view_editor TO test;


-- ================================================================
-- 4. Многотабличное представление
-- ================================================================

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


-- ================================================================
-- 5. Вставка в многотабличное представление
-- ================================================================

CREATE OR REPLACE FUNCTION public.insert_v_booking_details()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
DECLARE
    v_booking_id BIGINT;
BEGIN
    INSERT INTO public.bookings (
        tourist_id,
        tour_id,
        employee_id,
        booking_date,
        number_of_people,
        status,
        discount
    )
    VALUES (
        NEW.tourist_id,
        NEW.tour_id,
        NEW.employee_id,
        COALESCE(NEW.booking_date, CURRENT_DATE),
        COALESCE(NEW.number_of_people, 1),
        COALESCE(NEW.status, 'new'),
        COALESCE(NEW.discount, 0)
    )
    RETURNING booking_id INTO v_booking_id;

    NEW.booking_id := v_booking_id;

    SELECT full_name
    INTO NEW.tourist_name
    FROM public.tourists
    WHERE tourist_id = NEW.tourist_id;

    SELECT name
    INTO NEW.tour_name
    FROM public.tours
    WHERE tour_id = NEW.tour_id;

    SELECT full_name
    INTO NEW.employee_name
    FROM public.employees
    WHERE employee_id = NEW.employee_id;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_insert_v_booking_details
ON public.v_booking_details;

CREATE TRIGGER trg_insert_v_booking_details
INSTEAD OF INSERT
ON public.v_booking_details
FOR EACH ROW
EXECUTE FUNCTION public.insert_v_booking_details();

-- test видит только безопасный набор столбцов представления и может
-- добавлять бронирования через контролируемый SECURITY DEFINER-триггер.
GRANT SELECT, INSERT
ON TABLE public.v_booking_details
TO test;


-- ================================================================
-- 6. Справочная проверка выданных прав от имени владельца
-- ================================================================

SELECT
    grantee,
    table_name,
    privilege_type
FROM information_schema.table_privileges
WHERE grantee IN ('test', 'hotel_view_editor')
ORDER BY grantee, table_name, privilege_type;

SELECT
    grantee,
    table_name,
    column_name,
    privilege_type
FROM information_schema.column_privileges
WHERE grantee IN ('test', 'hotel_view_editor')
ORDER BY grantee, table_name, column_name, privilege_type;
