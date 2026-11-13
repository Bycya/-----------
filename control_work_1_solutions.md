# Контрольная работа №1 — решения задач 1–60

## Принятые исходные данные

В приложенном PDF перечислены задания, но отсутствуют исходные таблицы. Ответы ниже рассчитаны по стандартной учебной базе поставщиков, деталей и проектов:

- `S(sno, sname, status, city)` — поставщики;
- `P(pno, pname, color, weight, city)` — детали;
- `J(jno, jname, city)` — проекты;
- `SPJ(sno, pno, jno, qty)` — поставки.

### Поставщики S

| sno | sname | status | city |
|---|---|---:|---|
| S1 | Smith | 20 | London |
| S2 | Jones | 10 | Paris |
| S3 | Blake | 30 | Paris |
| S4 | Clark | 20 | London |
| S5 | Adams | 30 | Athens |

### Детали P

| pno | pname | color | weight | city |
|---|---|---|---:|---|
| P1 | Nut | Red | 12 | London |
| P2 | Bolt | Green | 17 | Paris |
| P3 | Screw | Blue | 17 | Rome |
| P4 | Screw | Red | 14 | London |
| P5 | Cam | Blue | 12 | Paris |
| P6 | Cog | Red | 19 | London |

### Проекты J

| jno | jname | city |
|---|---|---|
| J1 | Sorter | Paris |
| J2 | Punch | Rome |
| J3 | Reader | Athens |
| J4 | Console | Athens |
| J5 | Collator | London |
| J6 | Terminal | Oslo |
| J7 | Tape | London |

### Обозначения

- `σ` — выборка строк;
- `π` — проекция столбцов;
- `⋈` — соединение;
- `ρ` — переименование;
- `×` — декартово произведение;
- `∪` — объединение;
- `÷` — реляционное деление;
- `γ` — группировка и агрегирование.

В реляционном исчислении используются переменные кортежей `s`, `p`, `j`, `x`. Для заданий с подсчётом применяется расширенное реляционное исчисление с `COUNT`.

---

## 1. Детали, поставляемые поставщиком из Афин

**Реляционная алгебра**

```text
πP.*(σS.city='Athens'(S ⋈S.sno=SPJ.sno SPJ ⋈SPJ.pno=P.pno P))
```

**Реляционное исчисление**

```text
{ p | P(p) ∧ ∃s∃x(S(s) ∧ SPJ(x) ∧ s.city='Athens'
                    ∧ s.sno=x.sno ∧ x.pno=p.pno) }
```

**SQL**

```sql
SELECT DISTINCT p.*
FROM P AS p
JOIN SPJ AS x ON x.pno = p.pno
JOIN S AS s ON s.sno = x.sno
WHERE s.city = 'Athens';
```

**Таблица-ответ**

| pno | pname | color | weight | city |
|---|---|---|---:|---|
| P1 | Nut | Red | 12 | London |
| P2 | Bolt | Green | 17 | Paris |
| P3 | Screw | Blue | 17 | Rome |
| P4 | Screw | Red | 14 | London |
| P5 | Cam | Blue | 12 | Paris |
| P6 | Cog | Red | 19 | London |

## 2. Детали от парижского поставщика или для парижского проекта

**Реляционная алгебра**

```text
πpno(σS.city='Paris'(S ⋈ SPJ)) ∪ πpno(σJ.city='Paris'(SPJ ⋈ J))
```

**Реляционное исчисление**

```text
{ x.pno | SPJ(x) ∧
  (∃s(S(s) ∧ s.sno=x.sno ∧ s.city='Paris') ∨
   ∃j(J(j) ∧ j.jno=x.jno ∧ j.city='Paris')) }
```

**SQL**

```sql
SELECT DISTINCT x.pno
FROM SPJ AS x
JOIN S AS s ON s.sno = x.sno
JOIN J AS j ON j.jno = x.jno
WHERE s.city = 'Paris' OR j.city = 'Paris'
ORDER BY x.pno;
```

**Ответ:** `P1, P3, P4, P5`.

## 3. Пары одинаковых городов поставщика и проекта

**Реляционная алгебра**

```text
πS.city→supplier_city,J.city→project_city
  (σS.city=J.city(S ⋈ SPJ ⋈ J))
```

**Реляционное исчисление**

```text
{ ⟨s.city,j.city⟩ | S(s) ∧ J(j) ∧
  ∃x(SPJ(x) ∧ x.sno=s.sno ∧ x.jno=j.jno ∧ s.city=j.city) }
```

**SQL**

```sql
SELECT DISTINCT
    s.city AS supplier_city,
    j.city AS project_city
FROM SPJ AS x
JOIN S AS s ON s.sno = x.sno
JOIN J AS j ON j.jno = x.jno
WHERE s.city = j.city
ORDER BY supplier_city;
```

**Ответ**

| supplier_city | project_city |
|---|---|
| Athens | Athens |
| London | London |
| Paris | Paris |

## 4. Поставки количеством от 300 до 750 включительно

**Реляционная алгебра**

```text
σ300≤qty∧qty≤750(SPJ)
```

**Реляционное исчисление**

```text
{ x | SPJ(x) ∧ 300 ≤ x.qty ∧ x.qty ≤ 750 }
```

**SQL**

```sql
SELECT *
FROM SPJ
WHERE qty BETWEEN 300 AND 750
ORDER BY sno, pno, jno;
```

**Ответ**

| sno | pno | jno | qty |
|---|---|---|---:|
| S1 | P1 | J4 | 700 |
| S2 | P3 | J1 | 400 |
| S2 | P3 | J4 | 500 |
| S2 | P3 | J5 | 600 |
| S2 | P3 | J6 | 400 |
| S3 | P4 | J2 | 500 |
| S4 | P6 | J3 | 300 |
| S4 | P6 | J7 | 300 |
| S5 | P5 | J4 | 400 |
| S5 | P5 | J5 | 500 |
| S5 | P6 | J4 | 500 |

## 5. Номера деталей для парижских проектов

**Реляционная алгебра**

```text
πpno(σJ.city='Paris'(SPJ ⋈ J))
```

**Реляционное исчисление**

```text
{ x.pno | SPJ(x) ∧ ∃j(J(j) ∧ j.jno=x.jno ∧ j.city='Paris') }
```

**SQL**

```sql
SELECT DISTINCT x.pno
FROM SPJ AS x
JOIN J AS j ON j.jno = x.jno
WHERE j.city = 'Paris'
ORDER BY x.pno;
```

**Ответ:** `P1, P3`.

## 6. Поставщики, поставляющие детали для всех проектов J1–J7

**Реляционная алгебра**

```text
πsno,jno(SPJ) ÷ πjno(J)
```

**Реляционное исчисление**

```text
{ s.sno | S(s) ∧ ∀j(J(j) →
  ∃x(SPJ(x) ∧ x.sno=s.sno ∧ x.jno=j.jno)) }
```

**SQL**

```sql
SELECT s.sno
FROM S AS s
WHERE NOT EXISTS (
    SELECT 1 FROM J AS j
    WHERE NOT EXISTS (
        SELECT 1 FROM SPJ AS x
        WHERE x.sno = s.sno AND x.jno = j.jno
    )
);
```

**Ответ:** `S2`.

## 7. Количество разных проектов поставщика S5

**Реляционная алгебра**

```text
γCOUNT(DISTINCT jno)→project_count(σsno='S5'(SPJ))
```

**Реляционное исчисление**

```text
{ COUNT({x.jno | SPJ(x) ∧ x.sno='S5'}) }
```

**SQL**

```sql
SELECT COUNT(DISTINCT jno) AS project_count
FROM SPJ
WHERE sno = 'S5';
```

**Ответ:** `4` проекта (`J2, J4, J5, J7`).

## 8. Тройки, в которых все три города попарно различны

**Реляционная алгебра**

```text
πsno,pno,jno(
  σS.city≠P.city∧S.city≠J.city∧P.city≠J.city(S ⋈ SPJ ⋈ P ⋈ J))
```

**Реляционное исчисление**

```text
{ ⟨x.sno,x.pno,x.jno⟩ | SPJ(x) ∧ ∃s∃p∃j(
  S(s) ∧ P(p) ∧ J(j) ∧ s.sno=x.sno ∧ p.pno=x.pno ∧ j.jno=x.jno ∧
  s.city≠p.city ∧ s.city≠j.city ∧ p.city≠j.city) }
```

**SQL**

```sql
SELECT DISTINCT x.sno, x.pno, x.jno
FROM SPJ AS x
JOIN S AS s ON s.sno = x.sno
JOIN P AS p ON p.pno = x.pno
JOIN J AS j ON j.jno = x.jno
WHERE s.city <> p.city
  AND s.city <> j.city
  AND p.city <> j.city
ORDER BY x.sno, x.pno, x.jno;
```

**Ответ**

| sno | pno | jno |
|---|---|---|
| S2 | P3 | J3 |
| S2 | P3 | J4 |
| S2 | P3 | J5 |
| S2 | P3 | J6 |
| S2 | P3 | J7 |
| S3 | P4 | J2 |
| S5 | P2 | J2 |
| S5 | P5 | J5 |
| S5 | P5 | J7 |
| S5 | P6 | J2 |

## 9. Тройки, в которых поставщик, деталь и проект из одного города

**Реляционная алгебра**

```text
πsno,pno,jno(σS.city=P.city∧P.city=J.city(S ⋈ SPJ ⋈ P ⋈ J))
```

**Реляционное исчисление**

```text
{ ⟨x.sno,x.pno,x.jno⟩ | SPJ(x) ∧ ∃s∃p∃j(
  S(s) ∧ P(p) ∧ J(j) ∧ s.sno=x.sno ∧ p.pno=x.pno ∧ j.jno=x.jno ∧
  s.city=p.city ∧ p.city=j.city) }
```

**SQL**

```sql
SELECT DISTINCT x.sno, x.pno, x.jno
FROM SPJ AS x
JOIN S AS s ON s.sno = x.sno
JOIN P AS p ON p.pno = x.pno
JOIN J AS j ON j.jno = x.jno
WHERE s.city = p.city AND p.city = j.city;
```

**Ответ**

| sno | pno | jno |
|---|---|---|
| S4 | P6 | J7 |

## 10. Детали, поставляемые поставщиком из Лондона

**Реляционная алгебра:** `πP.*(σS.city='London'(S ⋈ SPJ ⋈ P))`

**Реляционное исчисление**

```text
{ p | P(p) ∧ ∃s∃x(S(s) ∧ SPJ(x) ∧ s.city='London'
                    ∧ s.sno=x.sno ∧ x.pno=p.pno) }
```

**SQL**

```sql
SELECT DISTINCT p.*
FROM P AS p
JOIN SPJ AS x ON x.pno = p.pno
JOIN S AS s ON s.sno = x.sno
WHERE s.city = 'London';
```

**Ответ**

| pno | pname | color | weight | city |
|---|---|---|---:|---|
| P1 | Nut | Red | 12 | London |
| P6 | Cog | Red | 19 | London |

## 11. Детали от афинского поставщика для проекта в Осло

**Реляционная алгебра**

```text
πpno(σS.city='Athens'∧J.city='Oslo'(S ⋈ SPJ ⋈ J))
```

**Реляционное исчисление**

```text
{ x.pno | SPJ(x) ∧ ∃s∃j(S(s) ∧ J(j) ∧ s.sno=x.sno ∧ j.jno=x.jno
                         ∧ s.city='Athens' ∧ j.city='Oslo') }
```

**SQL**

```sql
SELECT DISTINCT x.pno
FROM SPJ AS x
JOIN S AS s ON s.sno = x.sno
JOIN J AS j ON j.jno = x.jno
WHERE s.city = 'Athens' AND j.city = 'Oslo';
```

**Ответ:** пустое множество.

## 12. Детали от парижского поставщика для проекта в Париже

**Реляционная алгебра:** `πpno(σS.city='Paris'∧J.city='Paris'(S ⋈ SPJ ⋈ J))`

**Реляционное исчисление**

```text
{ x.pno | SPJ(x) ∧ ∃s∃j(S(s) ∧ J(j) ∧ s.sno=x.sno ∧ j.jno=x.jno
                         ∧ s.city='Paris' ∧ j.city='Paris') }
```

**SQL**

```sql
SELECT DISTINCT x.pno
FROM SPJ AS x
JOIN S AS s ON s.sno = x.sno
JOIN J AS j ON j.jno = x.jno
WHERE s.city = 'Paris' AND j.city = 'Paris';
```

**Ответ:** `P3`.

## 13. Названия проектов для деталей из Осло

**Реляционная алгебра:** `πjname(σP.city='Oslo'(P ⋈ SPJ ⋈ J))`

**Реляционное исчисление**

```text
{ j.jname | J(j) ∧ ∃p∃x(P(p) ∧ SPJ(x) ∧ p.city='Oslo'
                         ∧ p.pno=x.pno ∧ x.jno=j.jno) }
```

**SQL**

```sql
SELECT DISTINCT j.jname
FROM J AS j
JOIN SPJ AS x ON x.jno = j.jno
JOIN P AS p ON p.pno = x.pno
WHERE p.city = 'Oslo';
```

**Ответ:** пустое множество, потому что в `P` нет деталей из Осло.

## 14. Цвета деталей поставщика S5

**Реляционная алгебра:** `πcolor(σsno='S5'(SPJ ⋈ P))`

**Реляционное исчисление**

```text
{ p.color | P(p) ∧ ∃x(SPJ(x) ∧ x.sno='S5' ∧ x.pno=p.pno) }
```

**SQL**

```sql
SELECT DISTINCT p.color
FROM P AS p
JOIN SPJ AS x ON x.pno = p.pno
WHERE x.sno = 'S5'
ORDER BY p.color;
```

**Ответ:** `Blue, Green, Red`.

## 15. Пары деталей, поставляемых одним поставщиком

**Реляционная алгебра**

```text
πX.pno→pno1,Y.pno→pno2(
  σX.sno=Y.sno∧X.pno<Y.pno(ρX(SPJ) × ρY(SPJ)))
```

**Реляционное исчисление**

```text
{ ⟨x.pno,y.pno⟩ | SPJ(x) ∧ SPJ(y) ∧ x.sno=y.sno ∧ x.pno<y.pno }
```

**SQL**

```sql
SELECT DISTINCT x.pno AS pno1, y.pno AS pno2
FROM SPJ AS x
JOIN SPJ AS y
    ON y.sno = x.sno AND x.pno < y.pno
ORDER BY pno1, pno2;
```

**Ответ:** `(P1,P2)`, `(P1,P3)`, `(P1,P4)`, `(P1,P5)`, `(P1,P6)`, `(P2,P3)`, `(P2,P4)`, `(P2,P5)`, `(P2,P6)`, `(P3,P4)`, `(P3,P5)`, `(P3,P6)`, `(P4,P5)`, `(P4,P6)`, `(P5,P6)`.

## 16. Детали от лондонского поставщика для проекта в Лондоне

**Реляционная алгебра:** `πpno(σS.city='London'∧J.city='London'(S ⋈ SPJ ⋈ J))`

**Реляционное исчисление**

```text
{ x.pno | SPJ(x) ∧ ∃s∃j(S(s) ∧ J(j) ∧ s.sno=x.sno ∧ j.jno=x.jno
                         ∧ s.city='London' ∧ j.city='London') }
```

**SQL**

```sql
SELECT DISTINCT x.pno
FROM SPJ AS x
JOIN S AS s ON s.sno = x.sno
JOIN J AS j ON j.jno = x.jno
WHERE s.city = 'London' AND j.city = 'London';
```

**Ответ:** `P6`.

## 17. Детали для афинских проектов

**Реляционная алгебра:** `πpno(σJ.city='Athens'(SPJ ⋈ J))`

**Реляционное исчисление:** `{ x.pno | SPJ(x) ∧ ∃j(J(j) ∧ j.jno=x.jno ∧ j.city='Athens') }`

**SQL**

```sql
SELECT DISTINCT x.pno
FROM SPJ AS x
JOIN J AS j ON j.jno = x.jno
WHERE j.city = 'Athens'
ORDER BY x.pno;
```

**Ответ:** `P1, P2, P3, P4, P5, P6`.

## 18. Количество разных проектов поставщика S1

**Реляционная алгебра:** `γCOUNT(DISTINCT jno)→project_count(σsno='S1'(SPJ))`

**Реляционное исчисление:** `{ COUNT({x.jno | SPJ(x) ∧ x.sno='S1'}) }`

**SQL**

```sql
SELECT COUNT(DISTINCT jno) AS project_count
FROM SPJ
WHERE sno = 'S1';
```

**Ответ:** `2` проекта (`J1, J4`).

## 19. Детали, поставляемые поставщиком из Парижа

**Реляционная алгебра:** `πP.*(σS.city='Paris'(S ⋈ SPJ ⋈ P))`

**Реляционное исчисление:** `{ p | P(p) ∧ ∃s∃x(S(s) ∧ SPJ(x) ∧ s.city='Paris' ∧ s.sno=x.sno ∧ x.pno=p.pno) }`

**SQL**

```sql
SELECT DISTINCT p.*
FROM P AS p
JOIN SPJ AS x ON x.pno = p.pno
JOIN S AS s ON s.sno = x.sno
WHERE s.city = 'Paris';
```

**Ответ**

| pno | pname | color | weight | city |
|---|---|---|---:|---|
| P3 | Screw | Blue | 17 | Rome |
| P4 | Screw | Red | 14 | London |
| P5 | Cam | Blue | 12 | Paris |

## 20. Детали от лондонского поставщика или для лондонского проекта

**Реляционная алгебра**

```text
πpno(σS.city='London'(S ⋈ SPJ)) ∪ πpno(σJ.city='London'(SPJ ⋈ J))
```

**Реляционное исчисление**

```text
{ x.pno | SPJ(x) ∧
  (∃s(S(s) ∧ s.sno=x.sno ∧ s.city='London') ∨
   ∃j(J(j) ∧ j.jno=x.jno ∧ j.city='London')) }
```

**SQL**

```sql
SELECT DISTINCT x.pno
FROM SPJ AS x
JOIN S AS s ON s.sno = x.sno
JOIN J AS j ON j.jno = x.jno
WHERE s.city = 'London' OR j.city = 'London'
ORDER BY x.pno;
```

**Ответ:** `P1, P3, P5, P6`.

## 21. Тройки, в которых поставщик, деталь и проект не все из одного города

**Реляционная алгебра**

```text
πsno,pno,jno(σ¬(S.city=P.city∧P.city=J.city)(S ⋈ SPJ ⋈ P ⋈ J))
```

**Реляционное исчисление**

```text
{ ⟨x.sno,x.pno,x.jno⟩ | SPJ(x) ∧ ∃s∃p∃j(
  S(s) ∧ P(p) ∧ J(j) ∧ s.sno=x.sno ∧ p.pno=x.pno ∧ j.jno=x.jno ∧
  ¬(s.city=p.city ∧ p.city=j.city)) }
```

**SQL**

```sql
SELECT DISTINCT x.sno, x.pno, x.jno
FROM SPJ AS x
JOIN S AS s ON s.sno = x.sno
JOIN P AS p ON p.pno = x.pno
JOIN J AS j ON j.jno = x.jno
WHERE NOT (s.city = p.city AND p.city = j.city)
ORDER BY x.sno, x.pno, x.jno;
```

**Ответ:** все строки `SPJ`, кроме `(S4,P6,J7)`. Полный результат:

```text
(S1,P1,J1) (S1,P1,J4)
(S2,P3,J1) (S2,P3,J2) (S2,P3,J3) (S2,P3,J4)
(S2,P3,J5) (S2,P3,J6) (S2,P3,J7) (S2,P5,J2)
(S3,P3,J1) (S3,P4,J2) (S4,P6,J3)
(S5,P1,J4) (S5,P2,J2) (S5,P2,J4) (S5,P3,J4)
(S5,P4,J4) (S5,P5,J4) (S5,P5,J5) (S5,P5,J7)
(S5,P6,J2) (S5,P6,J4)
```

## 22. Детали для лондонских проектов

**Реляционная алгебра:** `πpno(σJ.city='London'(SPJ ⋈ J))`

**Реляционное исчисление:** `{ x.pno | SPJ(x) ∧ ∃j(J(j) ∧ j.jno=x.jno ∧ j.city='London') }`

**SQL**

```sql
SELECT DISTINCT x.pno
FROM SPJ AS x
JOIN J AS j ON j.jno = x.jno
WHERE j.city = 'London'
ORDER BY x.pno;
```

**Ответ:** `P3, P5, P6`.

## 23. Количество разных проектов поставщика S2

**Реляционная алгебра:** `γCOUNT(DISTINCT jno)→project_count(σsno='S2'(SPJ))`

**Реляционное исчисление:** `{ COUNT({x.jno | SPJ(x) ∧ x.sno='S2'}) }`

**SQL**

```sql
SELECT COUNT(DISTINCT jno) AS project_count
FROM SPJ
WHERE sno = 'S2';
```

**Ответ:** `7` проектов (`J1–J7`).

## 24. Цвета деталей поставщика S1

**Реляционная алгебра:** `πcolor(σsno='S1'(SPJ ⋈ P))`

**Реляционное исчисление:** `{ p.color | P(p) ∧ ∃x(SPJ(x) ∧ x.sno='S1' ∧ x.pno=p.pno) }`

**SQL**

```sql
SELECT DISTINCT p.color
FROM P AS p
JOIN SPJ AS x ON x.pno = p.pno
WHERE x.sno = 'S1';
```

**Ответ:** `Red`.

## 25. Детали, поставляемые для проекта поставщиком из города проекта

**Реляционная алгебра:** `πpno(σS.city=J.city(S ⋈ SPJ ⋈ J))`

**Реляционное исчисление**

```text
{ x.pno | SPJ(x) ∧ ∃s∃j(S(s) ∧ J(j) ∧ s.sno=x.sno
                          ∧ j.jno=x.jno ∧ s.city=j.city) }
```

**SQL**

```sql
SELECT DISTINCT x.pno
FROM SPJ AS x
JOIN S AS s ON s.sno = x.sno
JOIN J AS j ON j.jno = x.jno
WHERE s.city = j.city
ORDER BY x.pno;
```

**Ответ:** `P1, P2, P3, P4, P5, P6`.

## 26. Поставщики со статусом меньше статуса S1

**Реляционная алгебра**

```text
πSX.sno(σSX.status<S1.status∧S1.sno='S1'(ρSX(S) × ρS1(S)))
```

**Реляционное исчисление**

```text
{ s.sno | S(s) ∧ ∃s1(S(s1) ∧ s1.sno='S1' ∧ s.status<s1.status) }
```

**SQL**

```sql
SELECT sno
FROM S
WHERE status < (
    SELECT status FROM S WHERE sno = 'S1'
);
```

**Ответ:** `S2` — его статус `10` меньше статуса `20` поставщика S1.

## 27. Поставки количеством от 200 до 500 включительно

**Реляционная алгебра:** `σ200≤qty∧qty≤500(SPJ)`

**Реляционное исчисление:** `{ x | SPJ(x) ∧ 200≤x.qty ∧ x.qty≤500 }`

**SQL**

```sql
SELECT *
FROM SPJ
WHERE qty BETWEEN 200 AND 500
ORDER BY sno, pno, jno;
```

**Ответ**

| sno | pno | jno | qty |
|---|---|---|---:|
| S1 | P1 | J1 | 200 |
| S2 | P3 | J1 | 400 |
| S2 | P3 | J2 | 200 |
| S2 | P3 | J3 | 200 |
| S2 | P3 | J4 | 500 |
| S2 | P3 | J6 | 400 |
| S3 | P3 | J1 | 200 |
| S3 | P4 | J2 | 500 |
| S4 | P6 | J3 | 300 |
| S4 | P6 | J7 | 300 |
| S5 | P2 | J2 | 200 |
| S5 | P3 | J4 | 200 |
| S5 | P5 | J4 | 400 |
| S5 | P5 | J5 | 500 |
| S5 | P6 | J2 | 200 |
| S5 | P6 | J4 | 500 |

## 28. Детали от афинского поставщика для проекта в Афинах

**Реляционная алгебра:** `πpno(σS.city='Athens'∧J.city='Athens'(S ⋈ SPJ ⋈ J))`

**Реляционное исчисление**

```text
{ x.pno | SPJ(x) ∧ ∃s∃j(S(s) ∧ J(j) ∧ s.sno=x.sno ∧ j.jno=x.jno
                         ∧ s.city='Athens' ∧ j.city='Athens') }
```

**SQL**

```sql
SELECT DISTINCT x.pno
FROM SPJ AS x
JOIN S AS s ON s.sno = x.sno
JOIN J AS j ON j.jno = x.jno
WHERE s.city = 'Athens' AND j.city = 'Athens'
ORDER BY x.pno;
```

**Ответ:** `P1, P2, P3, P4, P5, P6`.

## 29. Цвета деталей поставщика S3

**Реляционная алгебра:** `πcolor(σsno='S3'(SPJ ⋈ P))`

**Реляционное исчисление:** `{ p.color | P(p) ∧ ∃x(SPJ(x) ∧ x.sno='S3' ∧ x.pno=p.pno) }`

**SQL**

```sql
SELECT DISTINCT p.color
FROM P AS p
JOIN SPJ AS x ON x.pno = p.pno
WHERE x.sno = 'S3'
ORDER BY p.color;
```

**Ответ:** `Blue, Red`.

## 30. Номера проектов для поставщиков из Парижа

**Реляционная алгебра:** `πjno(σS.city='Paris'(S ⋈ SPJ))`

**Реляционное исчисление:** `{ x.jno | SPJ(x) ∧ ∃s(S(s) ∧ s.sno=x.sno ∧ s.city='Paris') }`

**SQL**

```sql
SELECT DISTINCT x.jno
FROM SPJ AS x
JOIN S AS s ON s.sno = x.sno
WHERE s.city = 'Paris'
ORDER BY x.jno;
```

**Ответ:** `J1, J2, J3, J4, J5, J6, J7`.

---

# Задания 31–60

Пункты 31–60 дословно повторяют уже решённые задания. Для каждого номера применяются те же три выражения и та же таблица-ответ.

| № | Повторяет № | Краткий ответ |
|---:|---:|---|
| 31 | 16 | P6 |
| 32 | 9 | (S4, P6, J7) |
| 33 | 21 | Все поставки, кроме (S4, P6, J7) |
| 34 | 8 | 10 троек с попарно различными городами |
| 35 | 18 | 2 |
| 36 | 4 | 11 поставок с количеством 300–750 |
| 37 | 25 | P1, P2, P3, P4, P5, P6 |
| 38 | 15 | Все 15 неупорядоченных пар P1–P6 |
| 39 | 20 | P1, P3, P5, P6 |
| 40 | 22 | P3, P5, P6 |
| 41 | 6 | S2 |
| 42 | 24 | Red |
| 43 | 26 | S2 |
| 44 | 10 | P1 и P6, полные сведения |
| 45 | 3 | Athens–Athens, London–London, Paris–Paris |
| 46 | 28 | P1, P2, P3, P4, P5, P6 |
| 47 | 12 | P3 |
| 48 | 11 | Пустое множество |
| 49 | 27 | 16 поставок с количеством 200–500 |
| 50 | 23 | 7 |
| 51 | 7 | 4 |
| 52 | 2 | P1, P3, P4, P5 |
| 53 | 5 | P1, P3 |
| 54 | 17 | P1, P2, P3, P4, P5, P6 |
| 55 | 29 | Blue, Red |
| 56 | 14 | Blue, Green, Red |
| 57 | 19 | P3, P4, P5, полные сведения |
| 58 | 1 | P1–P6, полные сведения |
| 59 | 30 | J1–J7 |
| 60 | 13 | Пустое множество |

## Примечание о названиях столбцов

В учебных материалах часто используются имена `S#`, `P#`, `J#`. В PostgreSQL символ `#` потребует двойных кавычек, например `"S#"`. В решениях применены удобные имена `sno`, `pno`, `jno`. Если в вашей базе используются другие имена, их необходимо заменить, не меняя логику запросов.
