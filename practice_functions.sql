-- Практическая работа: функции PL/pgSQL
-- База данных: tourism_firm
-- Выполнять от имени владельца базы данных.

-- ================================================================
-- 1. Расчёт полной стоимости бронирования
-- Переменные, SELECT INTO, ветвления, пользовательское исключение.
-- ================================================================

CREATE OR REPLACE FUNCTION public.calculate_booking_cost(
    p_booking_id BIGINT
)
RETURNS NUMERIC
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_price      NUMERIC(12, 2);
    v_people     INTEGER;
    v_discount   NUMERIC(5, 2);
    v_total_cost NUMERIC(12, 2);
BEGIN
    IF p_booking_id IS NULL OR p_booking_id <= 0 THEN
        RAISE EXCEPTION
            'Идентификатор бронирования должен быть положительным числом'
            USING ERRCODE = '22023';
    END IF;

    SELECT
        t.price,
        b.number_of_people,
        b.discount
    INTO
        v_price,
        v_people,
        v_discount
    FROM public.bookings AS b
    JOIN public.tours AS t
        ON t.tour_id = b.tour_id
    WHERE b.booking_id = p_booking_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Бронирование с идентификатором % не найдено',
            p_booking_id
            USING ERRCODE = 'P0002';
    END IF;

    v_total_cost := ROUND(
        v_price * v_people * (1 - v_discount / 100),
        2
    );

    RETURN v_total_cost;
END;
$$;


-- ================================================================
-- 2. Каталог туров по стране
-- Параметризованный явный курсор, LOOP, FETCH, EXIT, ветвление.
-- ================================================================

CREATE OR REPLACE FUNCTION public.get_tour_catalog_by_country(
    p_country TEXT DEFAULT NULL
)
RETURNS TABLE (
    tour_id         BIGINT,
    tour_name       TEXT,
    country         TEXT,
    city            TEXT,
    price           NUMERIC,
    available_seats INTEGER,
    price_category  TEXT
)
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    r_tour RECORD;

    c_tours CURSOR (v_country TEXT) FOR
        SELECT
            t.tour_id,
            t.name AS tour_name,
            d.country,
            d.city,
            t.price,
            t.available_seats
        FROM public.tours AS t
        JOIN public.destinations AS d
            ON d.destination_id = t.destination_id
        WHERE v_country IS NULL
           OR LOWER(d.country) = LOWER(v_country)
        ORDER BY t.price, t.start_date, t.tour_id;
BEGIN
    OPEN c_tours(p_country);

    LOOP
        FETCH c_tours INTO r_tour;
        EXIT WHEN NOT FOUND;

        tour_id := r_tour.tour_id;
        tour_name := r_tour.tour_name;
        country := r_tour.country;
        city := r_tour.city;
        price := r_tour.price;
        available_seats := r_tour.available_seats;

        IF r_tour.price < 100000 THEN
            price_category := 'бюджетный';
        ELSIF r_tour.price <= 200000 THEN
            price_category := 'средний';
        ELSE
            price_category := 'премиальный';
        END IF;

        RETURN NEXT;
    END LOOP;

    CLOSE c_tours;
    RETURN;
END;
$$;


-- ================================================================
-- 3. Регистрация платежа
-- Переменные, ветвления, блокировка, агрегирование, исключения.
-- ================================================================

CREATE OR REPLACE FUNCTION public.register_booking_payment(
    p_booking_id BIGINT,
    p_amount NUMERIC,
    p_payment_method TEXT
)
RETURNS BIGINT
LANGUAGE plpgsql
VOLATILE
AS $$
DECLARE
    v_total_cost NUMERIC(12, 2);
    v_paid_amount NUMERIC(12, 2);
    v_payment_id BIGINT;
BEGIN
    IF p_amount IS NULL OR p_amount <= 0 THEN
        RAISE EXCEPTION
            'Сумма платежа должна быть больше нуля'
            USING ERRCODE = '22023';
    END IF;

    IF p_payment_method IS NULL
       OR p_payment_method NOT IN ('cash', 'card', 'bank_transfer') THEN
        RAISE EXCEPTION
            'Недопустимый способ оплаты: %',
            COALESCE(p_payment_method, 'NULL')
            USING ERRCODE = '22023';
    END IF;

    SELECT ROUND(
        t.price
        * b.number_of_people
        * (1 - b.discount / 100),
        2
    )
    INTO STRICT v_total_cost
    FROM public.bookings AS b
    JOIN public.tours AS t
        ON t.tour_id = b.tour_id
    WHERE b.booking_id = p_booking_id
    FOR UPDATE OF b;

    SELECT COALESCE(
        SUM(p.amount) FILTER (WHERE p.status = 'paid'),
        0
    )
    INTO v_paid_amount
    FROM public.payments AS p
    WHERE p.booking_id = p_booking_id;

    IF v_paid_amount + p_amount > v_total_cost THEN
        RAISE EXCEPTION
            'Платёж превышает остаток: стоимость %, оплачено %, новый платёж %',
            v_total_cost,
            v_paid_amount,
            p_amount
            USING ERRCODE = '23514';
    END IF;

    INSERT INTO public.payments (
        booking_id,
        amount,
        payment_date,
        payment_method,
        status
    )
    VALUES (
        p_booking_id,
        p_amount,
        CURRENT_TIMESTAMP(0),
        p_payment_method,
        'paid'
    )
    RETURNING payment_id INTO v_payment_id;

    RETURN v_payment_id;

EXCEPTION
    WHEN NO_DATA_FOUND THEN
        RAISE EXCEPTION
            'Бронирование с идентификатором % не найдено',
            p_booking_id
            USING ERRCODE = 'P0002';
END;
$$;


-- ================================================================
-- 4. Групповое назначение скидок
-- Переменные, цикл FOR, ветвления, CONTINUE, GET DIAGNOSTICS.
-- ================================================================

CREATE OR REPLACE FUNCTION public.apply_group_discounts(
    p_min_people INTEGER DEFAULT 3,
    p_discount NUMERIC DEFAULT 10
)
RETURNS INTEGER
LANGUAGE plpgsql
VOLATILE
AS $$
DECLARE
    r_booking RECORD;
    v_changed_in_iteration INTEGER;
    v_total_updated INTEGER := 0;
BEGIN
    IF p_min_people IS NULL OR p_min_people <= 0 THEN
        RAISE EXCEPTION
            'Минимальное количество человек должно быть больше нуля'
            USING ERRCODE = '22023';
    END IF;

    IF p_discount IS NULL
       OR p_discount < 0
       OR p_discount > 100 THEN
        RAISE EXCEPTION
            'Скидка должна находиться в диапазоне от 0 до 100'
            USING ERRCODE = '22023';
    END IF;

    FOR r_booking IN
        SELECT
            booking_id,
            number_of_people,
            discount,
            status
        FROM public.bookings
        ORDER BY booking_id
    LOOP
        IF r_booking.status = 'cancelled' THEN
            CONTINUE;
        END IF;

        IF r_booking.number_of_people >= p_min_people
           AND r_booking.discount < p_discount THEN
            UPDATE public.bookings
            SET discount = p_discount
            WHERE booking_id = r_booking.booking_id;

            GET DIAGNOSTICS
                v_changed_in_iteration = ROW_COUNT;

            v_total_updated :=
                v_total_updated + v_changed_in_iteration;
        END IF;
    END LOOP;

    RETURN v_total_updated;
END;
$$;


-- ================================================================
-- 5. Справочная информация о созданных функциях
-- ================================================================

SELECT
    routine_name,
    data_type,
    routine_type
FROM information_schema.routines
WHERE routine_schema = 'public'
  AND routine_name IN (
      'calculate_booking_cost',
      'get_tour_catalog_by_country',
      'register_booking_payment',
      'apply_group_discounts'
  )
ORDER BY routine_name;
