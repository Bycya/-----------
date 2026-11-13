# Контрольная работа №1 — оформление по образцу

Используются отношения:

```text
S(S#, SNAME, STATUS, CITY)
P(P#, PNAME, COLOR, WEIGHT, CITY)
J(J#, JNAME, CITY)
SPJ(S#, P#, J#, QTY)
```

Формат каждого решения:

```text
1) реляционная алгебра;
2) реляционное исчисление;
3) SQL;
4) таблица-ответ.
```

`SX`, `PX`, `JX`, `SPJX` — переменные-кортежи. В формулах `JOIN(условие)` означает соединение по явно указанному условию. Это позволяет не соединять ошибочно одноимённые столбцы `CITY`.

---

## 1. Получить полные сведения о деталях, поставляемых поставщиком из Афин

```text
1) (((S WHERE CITY='Athens') JOIN(S.S#=SPJ.S#) SPJ)
     JOIN(SPJ.P#=P.P#) P)[P#, PNAME, COLOR, WEIGHT, P.CITY]

2) PX WHERE EXISTS SX EXISTS SPJX
   (SX.CITY='Athens' AND SX.S#=SPJX.S# AND SPJX.P#=PX.P#)

3) SELECT DISTINCT P.*
   FROM P JOIN SPJ ON SPJ.P#=P.P# JOIN S ON S.S#=SPJ.S#
   WHERE S.CITY='Athens';
```

4) Ответ:

| P# | PNAME | COLOR | WEIGHT | CITY |
|---|---|---|---:|---|
| P1 | Nut | Red | 12 | London |
| P2 | Bolt | Green | 17 | Paris |
| P3 | Screw | Blue | 17 | Rome |
| P4 | Screw | Red | 14 | London |
| P5 | Cam | Blue | 12 | Paris |
| P6 | Cog | Red | 19 | London |

## 2. Номера деталей от парижского поставщика или для парижского проекта

```text
1) (((S WHERE CITY='Paris') JOIN(S.S#=SPJ.S#) SPJ)[P#]) UNION
   ((SPJ JOIN(SPJ.J#=J.J#) (J WHERE CITY='Paris'))[P#])

2) SPJX.P# WHERE
   EXISTS SX (SX.S#=SPJX.S# AND SX.CITY='Paris')
   OR EXISTS JX (JX.J#=SPJX.J# AND JX.CITY='Paris')

3) SELECT DISTINCT SPJ.P#
   FROM SPJ JOIN S ON S.S#=SPJ.S# JOIN J ON J.J#=SPJ.J#
   WHERE S.CITY='Paris' OR J.CITY='Paris';
```

4) Ответ: `P1, P3, P4, P5`.

## 3. Пары городов, где город поставщика равен городу проекта

```text
1) (((S RENAME CITY AS SCITY) JOIN(S.S#=SPJ.S#) SPJ
     JOIN(SPJ.J#=J.J#) (J RENAME CITY AS JCITY))
     WHERE SCITY=JCITY)[SCITY, JCITY]

2) {SX.CITY AS SCITY, JX.CITY AS JCITY} WHERE EXISTS SPJX
   (SX.S#=SPJX.S# AND JX.J#=SPJX.J# AND SX.CITY=JX.CITY)

3) SELECT DISTINCT S.CITY AS SCITY, J.CITY AS JCITY
   FROM SPJ JOIN S ON S.S#=SPJ.S# JOIN J ON J.J#=SPJ.J#
   WHERE S.CITY=J.CITY;
```

4) Ответ:

| SCITY | JCITY |
|---|---|
| Athens | Athens |
| London | London |
| Paris | Paris |

## 4. Поставки количеством от 300 до 750 включительно

```text
1) SPJ WHERE QTY>=300 AND QTY<=750

2) SPJX WHERE SPJX.QTY>=300 AND SPJX.QTY<=750

3) SELECT * FROM SPJ WHERE QTY BETWEEN 300 AND 750;
```

4) Ответ:

| S# | P# | J# | QTY |
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

```text
1) (SPJ JOIN(SPJ.J#=J.J#) (J WHERE CITY='Paris'))[P#]

2) SPJX.P# WHERE EXISTS JX
   (JX.J#=SPJX.J# AND JX.CITY='Paris')

3) SELECT DISTINCT SPJ.P#
   FROM SPJ JOIN J ON J.J#=SPJ.J#
   WHERE J.CITY='Paris';
```

4) Ответ: `P1, P3`.

## 6. Поставщики, поставляющие детали для всех проектов J1–J7

```text
1) SPJ[S#, J#] DIVIDEBY J[J#]

2) SX.S# WHERE FORALL JX
   (EXISTS SPJX (SPJX.S#=SX.S# AND SPJX.J#=JX.J#))

2') SX.S# WHERE NOT EXISTS JX
    (NOT EXISTS SPJX (SPJX.S#=SX.S# AND SPJX.J#=JX.J#))

3) SELECT S.S# FROM S
   WHERE NOT EXISTS (
       SELECT * FROM J
       WHERE NOT EXISTS (
           SELECT * FROM SPJ
           WHERE SPJ.S#=S.S# AND SPJ.J#=J.J#));
```

4) Ответ: `S2`.

## 7. Количество разных проектов поставщика S5

```text
1) COUNT((SPJ WHERE S#='S5')[J#])

2) COUNT DISTINCT SPJX.J# WHERE SPJX.S#='S5'

3) SELECT COUNT(DISTINCT J#) AS PROJECT_COUNT
   FROM SPJ WHERE S#='S5';
```

4) Ответ:

| PROJECT_COUNT |
|---:|
| 4 |

## 8. Тройки, в которых все три города попарно различны

```text
1) ((SPJ JOIN(SPJ.S#=S.S#) (S RENAME CITY AS SCITY)
      JOIN(SPJ.P#=P.P#) (P RENAME CITY AS PCITY)
      JOIN(SPJ.J#=J.J#) (J RENAME CITY AS JCITY))
      WHERE SCITY<>PCITY AND SCITY<>JCITY AND PCITY<>JCITY)[S#, P#, J#]

2) {SPJX.S#, SPJX.P#, SPJX.J#} WHERE EXISTS SX EXISTS PX EXISTS JX
   (SX.S#=SPJX.S# AND PX.P#=SPJX.P# AND JX.J#=SPJX.J#
    AND SX.CITY<>PX.CITY AND SX.CITY<>JX.CITY AND PX.CITY<>JX.CITY)

3) SELECT DISTINCT SPJ.S#, SPJ.P#, SPJ.J#
   FROM SPJ JOIN S ON S.S#=SPJ.S#
   JOIN P ON P.P#=SPJ.P# JOIN J ON J.J#=SPJ.J#
   WHERE S.CITY<>P.CITY AND S.CITY<>J.CITY AND P.CITY<>J.CITY;
```

4) Ответ:

| S# | P# | J# |
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

## 9. Тройки, в которых поставщик, деталь и проект находятся в одном городе

```text
1) ((SPJ JOIN(SPJ.S#=S.S#) (S RENAME CITY AS SCITY)
      JOIN(SPJ.P#=P.P#) (P RENAME CITY AS PCITY)
      JOIN(SPJ.J#=J.J#) (J RENAME CITY AS JCITY))
      WHERE SCITY=PCITY AND PCITY=JCITY)[S#, P#, J#]

2) {SPJX.S#, SPJX.P#, SPJX.J#} WHERE EXISTS SX EXISTS PX EXISTS JX
   (SX.S#=SPJX.S# AND PX.P#=SPJX.P# AND JX.J#=SPJX.J#
    AND SX.CITY=PX.CITY AND PX.CITY=JX.CITY)

3) SELECT DISTINCT SPJ.S#, SPJ.P#, SPJ.J#
   FROM SPJ JOIN S ON S.S#=SPJ.S#
   JOIN P ON P.P#=SPJ.P# JOIN J ON J.J#=SPJ.J#
   WHERE S.CITY=P.CITY AND P.CITY=J.CITY;
```

4) Ответ: `(S4, P6, J7)`.

## 10. Полные сведения о деталях от лондонского поставщика

```text
1) (((S WHERE CITY='London') JOIN(S.S#=SPJ.S#) SPJ)
     JOIN(SPJ.P#=P.P#) P)[P#, PNAME, COLOR, WEIGHT, P.CITY]

2) PX WHERE EXISTS SX EXISTS SPJX
   (SX.CITY='London' AND SX.S#=SPJX.S# AND SPJX.P#=PX.P#)

3) SELECT DISTINCT P.*
   FROM P JOIN SPJ ON SPJ.P#=P.P# JOIN S ON S.S#=SPJ.S#
   WHERE S.CITY='London';
```

4) Ответ:

| P# | PNAME | COLOR | WEIGHT | CITY |
|---|---|---|---:|---|
| P1 | Nut | Red | 12 | London |
| P6 | Cog | Red | 19 | London |

## 11. Детали от афинского поставщика для проекта в Осло

```text
1) ((S WHERE CITY='Athens') JOIN(S.S#=SPJ.S#) SPJ
    JOIN(SPJ.J#=J.J#) (J WHERE CITY='Oslo'))[P#]

2) SPJX.P# WHERE EXISTS SX EXISTS JX
   (SX.S#=SPJX.S# AND JX.J#=SPJX.J#
    AND SX.CITY='Athens' AND JX.CITY='Oslo')

3) SELECT DISTINCT SPJ.P#
   FROM SPJ JOIN S ON S.S#=SPJ.S# JOIN J ON J.J#=SPJ.J#
   WHERE S.CITY='Athens' AND J.CITY='Oslo';
```

4) Ответ: пустое множество.

## 12. Детали от парижского поставщика для проекта в Париже

```text
1) ((S WHERE CITY='Paris') JOIN(S.S#=SPJ.S#) SPJ
    JOIN(SPJ.J#=J.J#) (J WHERE CITY='Paris'))[P#]

2) SPJX.P# WHERE EXISTS SX EXISTS JX
   (SX.S#=SPJX.S# AND JX.J#=SPJX.J#
    AND SX.CITY='Paris' AND JX.CITY='Paris')

3) SELECT DISTINCT SPJ.P#
   FROM SPJ JOIN S ON S.S#=SPJ.S# JOIN J ON J.J#=SPJ.J#
   WHERE S.CITY='Paris' AND J.CITY='Paris';
```

4) Ответ: `P3`.

## 13. Названия проектов для деталей из Осло

```text
1) ((P WHERE CITY='Oslo') JOIN(P.P#=SPJ.P#) SPJ
    JOIN(SPJ.J#=J.J#) J)[JNAME]

2) JX.JNAME WHERE EXISTS PX EXISTS SPJX
   (PX.CITY='Oslo' AND PX.P#=SPJX.P# AND SPJX.J#=JX.J#)

3) SELECT DISTINCT J.JNAME
   FROM J JOIN SPJ ON SPJ.J#=J.J# JOIN P ON P.P#=SPJ.P#
   WHERE P.CITY='Oslo';
```

4) Ответ: пустое множество.

## 14. Цвета деталей поставщика S5

```text
1) ((SPJ WHERE S#='S5') JOIN(SPJ.P#=P.P#) P)[COLOR]

2) PX.COLOR WHERE EXISTS SPJX
   (SPJX.S#='S5' AND SPJX.P#=PX.P#)

3) SELECT DISTINCT P.COLOR
   FROM P JOIN SPJ ON SPJ.P#=P.P#
   WHERE SPJ.S#='S5';
```

4) Ответ: `Blue, Green, Red`.

## 15. Пары деталей, поставляемых одним поставщиком

```text
1) ((SPJ RENAME P# AS PA, S# AS SA)
    JOIN(SA=SB AND PA<PB)
    (SPJ RENAME P# AS PB, S# AS SB))[PA, PB]

2) {SPJX.P# AS PA, SPJY.P# AS PB} WHERE
   SPJX.S#=SPJY.S# AND SPJX.P#<SPJY.P#

3) SELECT DISTINCT X.P# AS PA, Y.P# AS PB
   FROM SPJ AS X JOIN SPJ AS Y
   ON X.S#=Y.S# AND X.P#<Y.P#;
```

4) Ответ: все 15 неупорядоченных пар деталей `P1–P6`.

## 16. Детали от лондонского поставщика для проекта в Лондоне

```text
1) ((S WHERE CITY='London') JOIN(S.S#=SPJ.S#) SPJ
    JOIN(SPJ.J#=J.J#) (J WHERE CITY='London'))[P#]

2) SPJX.P# WHERE EXISTS SX EXISTS JX
   (SX.S#=SPJX.S# AND JX.J#=SPJX.J#
    AND SX.CITY='London' AND JX.CITY='London')

3) SELECT DISTINCT SPJ.P#
   FROM SPJ JOIN S ON S.S#=SPJ.S# JOIN J ON J.J#=SPJ.J#
   WHERE S.CITY='London' AND J.CITY='London';
```

4) Ответ: `P6`.

## 17. Детали для афинских проектов

```text
1) (SPJ JOIN(SPJ.J#=J.J#) (J WHERE CITY='Athens'))[P#]

2) SPJX.P# WHERE EXISTS JX
   (JX.J#=SPJX.J# AND JX.CITY='Athens')

3) SELECT DISTINCT SPJ.P#
   FROM SPJ JOIN J ON J.J#=SPJ.J#
   WHERE J.CITY='Athens';
```

4) Ответ: `P1, P2, P3, P4, P5, P6`.

## 18. Количество разных проектов поставщика S1

```text
1) COUNT((SPJ WHERE S#='S1')[J#])
2) COUNT DISTINCT SPJX.J# WHERE SPJX.S#='S1'
3) SELECT COUNT(DISTINCT J#) FROM SPJ WHERE S#='S1';
```

4) Ответ: `2`.

## 19. Полные сведения о деталях от парижского поставщика

```text
1) (((S WHERE CITY='Paris') JOIN(S.S#=SPJ.S#) SPJ)
     JOIN(SPJ.P#=P.P#) P)[P#, PNAME, COLOR, WEIGHT, P.CITY]

2) PX WHERE EXISTS SX EXISTS SPJX
   (SX.CITY='Paris' AND SX.S#=SPJX.S# AND SPJX.P#=PX.P#)

3) SELECT DISTINCT P.*
   FROM P JOIN SPJ ON SPJ.P#=P.P# JOIN S ON S.S#=SPJ.S#
   WHERE S.CITY='Paris';
```

4) Ответ: `P3, P4, P5` с полными сведениями из `P`.

## 20. Детали от лондонского поставщика или для лондонского проекта

```text
1) (((S WHERE CITY='London') JOIN(S.S#=SPJ.S#) SPJ)[P#]) UNION
   ((SPJ JOIN(SPJ.J#=J.J#) (J WHERE CITY='London'))[P#])

2) SPJX.P# WHERE
   EXISTS SX (SX.S#=SPJX.S# AND SX.CITY='London')
   OR EXISTS JX (JX.J#=SPJX.J# AND JX.CITY='London')

3) SELECT DISTINCT SPJ.P#
   FROM SPJ JOIN S ON S.S#=SPJ.S# JOIN J ON J.J#=SPJ.J#
   WHERE S.CITY='London' OR J.CITY='London';
```

4) Ответ: `P1, P3, P5, P6`.

## 21. Тройки, в которых поставщик, деталь и проект не все из одного города

```text
1) ((SPJ JOIN(SPJ.S#=S.S#) (S RENAME CITY AS SCITY)
      JOIN(SPJ.P#=P.P#) (P RENAME CITY AS PCITY)
      JOIN(SPJ.J#=J.J#) (J RENAME CITY AS JCITY))
      WHERE NOT(SCITY=PCITY AND PCITY=JCITY))[S#, P#, J#]

2) {SPJX.S#, SPJX.P#, SPJX.J#} WHERE EXISTS SX EXISTS PX EXISTS JX
   (SX.S#=SPJX.S# AND PX.P#=SPJX.P# AND JX.J#=SPJX.J#
    AND NOT(SX.CITY=PX.CITY AND PX.CITY=JX.CITY))

3) SELECT DISTINCT SPJ.S#, SPJ.P#, SPJ.J#
   FROM SPJ JOIN S ON S.S#=SPJ.S#
   JOIN P ON P.P#=SPJ.P# JOIN J ON J.J#=SPJ.J#
   WHERE NOT(S.CITY=P.CITY AND P.CITY=J.CITY);
```

4) Ответ: все 24 поставки, кроме `(S4, P6, J7)`, то есть 23 строки.

## 22. Детали для лондонских проектов

```text
1) (SPJ JOIN(SPJ.J#=J.J#) (J WHERE CITY='London'))[P#]
2) SPJX.P# WHERE EXISTS JX (JX.J#=SPJX.J# AND JX.CITY='London')
3) SELECT DISTINCT SPJ.P# FROM SPJ JOIN J ON J.J#=SPJ.J#
   WHERE J.CITY='London';
```

4) Ответ: `P3, P5, P6`.

## 23. Количество разных проектов поставщика S2

```text
1) COUNT((SPJ WHERE S#='S2')[J#])
2) COUNT DISTINCT SPJX.J# WHERE SPJX.S#='S2'
3) SELECT COUNT(DISTINCT J#) FROM SPJ WHERE S#='S2';
```

4) Ответ: `7`.

## 24. Цвета деталей поставщика S1

```text
1) ((SPJ WHERE S#='S1') JOIN(SPJ.P#=P.P#) P)[COLOR]
2) PX.COLOR WHERE EXISTS SPJX (SPJX.S#='S1' AND SPJX.P#=PX.P#)
3) SELECT DISTINCT P.COLOR FROM P JOIN SPJ ON SPJ.P#=P.P#
   WHERE SPJ.S#='S1';
```

4) Ответ: `Red`.

## 25. Детали для проектов от поставщика из города проекта

```text
1) ((S RENAME CITY AS SCITY) JOIN(S.S#=SPJ.S#) SPJ
    JOIN(SPJ.J#=J.J#) (J RENAME CITY AS JCITY)
    WHERE SCITY=JCITY)[P#]

2) SPJX.P# WHERE EXISTS SX EXISTS JX
   (SX.S#=SPJX.S# AND JX.J#=SPJX.J# AND SX.CITY=JX.CITY)

3) SELECT DISTINCT SPJ.P#
   FROM SPJ JOIN S ON S.S#=SPJ.S# JOIN J ON J.J#=SPJ.J#
   WHERE S.CITY=J.CITY;
```

4) Ответ: `P1, P2, P3, P4, P5, P6`.

## 26. Поставщики со статусом меньше статуса S1

```text
1) ((S RENAME S# AS SX, STATUS AS STATUSX)
    TIMES (S WHERE S#='S1' RENAME STATUS AS STATUS1)
    WHERE STATUSX<STATUS1)[SX]

2) SX.S# WHERE EXISTS SY
   (SY.S#='S1' AND SX.STATUS<SY.STATUS)

3) SELECT S# FROM S
   WHERE STATUS < (SELECT STATUS FROM S WHERE S#='S1');
```

4) Ответ: `S2`.

## 27. Поставки количеством от 200 до 500 включительно

```text
1) SPJ WHERE QTY>=200 AND QTY<=500
2) SPJX WHERE SPJX.QTY>=200 AND SPJX.QTY<=500
3) SELECT * FROM SPJ WHERE QTY BETWEEN 200 AND 500;
```

4) Ответ:

| S# | P# | J# | QTY |
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

```text
1) ((S WHERE CITY='Athens') JOIN(S.S#=SPJ.S#) SPJ
    JOIN(SPJ.J#=J.J#) (J WHERE CITY='Athens'))[P#]
2) SPJX.P# WHERE EXISTS SX EXISTS JX
   (SX.S#=SPJX.S# AND JX.J#=SPJX.J#
    AND SX.CITY='Athens' AND JX.CITY='Athens')
3) SELECT DISTINCT SPJ.P# FROM SPJ
   JOIN S ON S.S#=SPJ.S# JOIN J ON J.J#=SPJ.J#
   WHERE S.CITY='Athens' AND J.CITY='Athens';
```

4) Ответ: `P1, P2, P3, P4, P5, P6`.

## 29. Цвета деталей поставщика S3

```text
1) ((SPJ WHERE S#='S3') JOIN(SPJ.P#=P.P#) P)[COLOR]
2) PX.COLOR WHERE EXISTS SPJX (SPJX.S#='S3' AND SPJX.P#=PX.P#)
3) SELECT DISTINCT P.COLOR FROM P JOIN SPJ ON SPJ.P#=P.P#
   WHERE SPJ.S#='S3';
```

4) Ответ: `Blue, Red`.

## 30. Проекты для поставщиков из Парижа

```text
1) ((S WHERE CITY='Paris') JOIN(S.S#=SPJ.S#) SPJ)[J#]
2) SPJX.J# WHERE EXISTS SX (SX.S#=SPJX.S# AND SX.CITY='Paris')
3) SELECT DISTINCT SPJ.J# FROM SPJ JOIN S ON S.S#=SPJ.S#
   WHERE S.CITY='Paris';
```

4) Ответ: `J1, J2, J3, J4, J5, J6, J7`.

---

# Повторяющиеся задания 31–60

В PDF задания 31–60 дословно повторяют предыдущие. Их решения в том же формате находятся по следующим номерам:

| Задание | Использовать решение |
|---:|---:|
| 31 | 16 |
| 32 | 9 |
| 33 | 21 |
| 34 | 8 |
| 35 | 18 |
| 36 | 4 |
| 37 | 25 |
| 38 | 15 |
| 39 | 20 |
| 40 | 22 |
| 41 | 6 |
| 42 | 24 |
| 43 | 26 |
| 44 | 10 |
| 45 | 3 |
| 46 | 28 |
| 47 | 12 |
| 48 | 11 |
| 49 | 27 |
| 50 | 23 |
| 51 | 7 |
| 52 | 2 |
| 53 | 5 |
| 54 | 17 |
| 55 | 29 |
| 56 | 14 |
| 57 | 19 |
| 58 | 1 |
| 59 | 30 |
| 60 | 13 |

## Примечание для PostgreSQL

Записи `S#`, `P#`, `J#` повторяют учебный образец. В PostgreSQL такие имена нужно заключать в двойные кавычки (`"S#"`) либо заменить на `sno`, `pno`, `jno`, как в предыдущем подробном файле.
