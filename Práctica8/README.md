# Práctica 8 — Pronóstico (Forecasting)

## Dataset y objetivo

Parto de dataset_limpio.csv de la Práctica 1. Sumo los camiones de todos los puertos para tener una serie mensual, el cual me da el valor de 84 meses, de enero de 2018 a diciembre de 2024. 
El objetivo es pronosticar los camiones totales de cada mes de 2025.


Elegí comparar un modelo de regresión (el tipo de modelo de la Práctica 5) contra modelos de series de tiempo, y no usar solo uno. Con 84 puntos y un hueco por COVID no podía saber cuál podía funcionar mejor y comparar me permite defender la elección con números y no solo con una idea. Trabajé con el total y no con un puerto o un grupo porque suma el ruido de los 102 puertos y la serie queda más estable.

Lo que vi en la serie antes de modelar:

- Tendencia al alza desde 2021 (promedio mensual de 1.043 millones en 2021 a 1.097 millones en 2024).
- Estacionalidad suave: diciembre es el mes más bajo y mayo y octubre los más altos.
- Una caída fuerte en abril de 2020 (718 mil camiones, el mínimo de toda la serie).

## Modelos comparados

| Modelo | Qué hace | Para qué lo incluí |
|---|---|---|
| Naive estacional | Predice cada mes igual que el mismo mes del último año | Baseline: es el piso que cualquier modelo debe superar |
| Regresión sin COVID | log(camiones) aprox tendencia + mes del año | Primera versión, la más sencilla |
| Regresión con COVID | Lo anterior + una variable que vale 1 en marzo-junio de 2020 | Variación: ver si tratar el COVID mejora el modelo |
| Holt-Winters | Suavizamiento exponencial con tendencia amortiguada y estacionalidad multiplicativa | Modelo clásico de series de tiempo |
| SARIMA(1,1,1)(0,1,1,12) | Modelo que usa los errores y valores pasados | Modelo clásico más flexible |

Decisiones:

- Log en la regresión: igual que en la Práctica 5, para que el efecto de cada mes sea un porcentaje y no una cantidad fija.
- Meses del COVID: usé de marzo a junio de 2020 porque son los meses con la caída más fuerte. No probé otras ventanas así que esa elección es mía y no está validada opr alguna otra fuente o prueba.
- Órdenes de SARIMA: usé un modelo estándar de uso común y no hice una búsqueda de órdenes y puede ser posible que otros órdenes lo hagan mejor.

## Cómo evalué

- División por tiempo, nunca al azar: en una serie, entrenar con el futuro y probar con el pasado sería hacer trampa.
- Dos pruebas: entrenar con 2018-2023 y probar con 2024, y entrenar con 2018-2022 y probar con 2023. Con una sola prueba de 12 meses el resultado depende demasiado de ese año.
- Métricas: MAE (error promedio en camiones), RMSE (castiga más los errores grandes) y MAPE (el error como porcentaje), elegí el MAE para decidir porque se entiende directo: cuántos camiones se equivoca el modelo en promedio.

## Resultados

Prueba 2024 (entrenando con 2018-2023):

| Modelo | MAE | RMSE | MAPE % |
|---|---|---|---|
| Naive estacional (baseline) | 47,890 | 60,058 | 4.3 |
| Regresión sin COVID | 36,935 | 52,181 | 3.3 |
| Regresión con COVID | 39,134 | 52,086 | 3.5 |
| Holt-Winters | 49,131 | 62,404 | 4.4 |
| SARIMA | 55,811 | 67,622 | 5.0 |

Prueba 2023 (entrenando con 2018-2022):

| Modelo | MAE | RMSE | MAPE % |
|---|---|---|---|
| Naive estacional (baseline) | 27,350 | 30,143 | 2.6 |
| Regresión sin COVID | 27,966 | 40,492 | 2.5 |
| Regresión con COVID | 19,124 | 26,078 | 1.8 |
| Holt-Winters | 26,629 | 39,317 | 2.4 |
| SARIMA | 60,057 | 66,954 | 5.5 |

MAE promedio de las dos pruebas:

| Modelo | MAE promedio |
|---|---|
| Regresión con COVID | 29,129 |
| Regresión sin COVID | 32,451 |
| Naive estacional (baseline) | 37,620 |
| Holt-Winters | 37,880 |
| SARIMA | 57,934 |

Gráfica: pronostico_prueba_2024.png (cada modelo contra lo que pasó en 2024).

Lo que veo:

- La regresión con COVID tiene el menor MAE promedio y es la elegida. Supera al baseline por unos 8,500 camiones (23%) en promedio.
- Holt-Winters casi empata con el baseline (37,880 contra 37,620), un modelo más complejo no aportó nada sobre simplemente repetir el año anterior.
- SARIMA es el peor y pierde contra el baseline en las dos pruebas, con solo 72 meses de entrenamiento y un golpe como el COVID, un modelo con muchos parámetros se ajusta mal.
- La variable de COVID no gana en las dos pruebas: en 2024 es un poco peor que la regresión sin COVID (39,134 contra 36,935) pero en 2023 es mucho mejor (19,124 contra 27,966). Tiene sentido ya que al entrenar con 2018-2022, el hueco de 2020 distorsiona la tendencia si no se marca. Al entrenar con 2018-2023 el efecto se diluye. La diferencia en 2024 es chica (2,200 camiones) y con 12 puntos no puedo asegurar que sea real.
- Ajuste de la regresión con COVID (entrenada hasta 2023): R2 = 0.785 en log, contra 0.476 que tenía sin la variable de COVID y sobre toda la serie. Coeficientes significativos (p < 0.05): tendencia (+0.11% mensual), diciembre (-8.2%), febrero (-5.4%), marzo (+11.3%) y covid (-21.9%). Los coeficientes de mes son relativos a enero.

## Pronóstico 2025

Reentrené la regresión con COVID con los 84 meses y pronostiqué los 12 meses de 2025 (pronostico_2025.png y pronostico_2025.csv, con intervalo de predicción al 80%).

| Mes | Pronóstico | Intervalo 80% |
|---|---|---|
| Enero | 1,078,380 | 1,016,687 – 1,143,817 |
| Febrero | 1,029,829 | 970,914 – 1,092,319 |
| Marzo | 1,193,463 | 1,125,131 – 1,265,946 |
| Abril | 1,086,376 | 1,024,175 – 1,152,354 |
| Mayo | 1,148,363 | 1,082,613 – 1,218,106 |
| Junio | 1,158,854 | 1,092,503 – 1,229,235 |
| Julio | 1,097,650 | 1,034,854 – 1,164,255 |
| Agosto | 1,141,290 | 1,075,998 – 1,210,544 |
| Septiembre | 1,096,177 | 1,033,466 – 1,162,693 |
| Octubre | 1,167,715 | 1,100,911 – 1,238,572 |
| Noviembre | 1,086,325 | 1,024,178 – 1,152,244 |
| Diciembre | 1,003,346 | 945,946 – 1,064,229 |

El total de 2025 es de 13.29 millones de camiones, un 0.9% más que los 13.17 millones reales de 2024.

## Limitaciones

- Solo hay 84 puntos y dos pruebas de 12 meses, así que las diferencias pequeñas entre modelos (por ejemplo, con y sin COVID en 2024) no son concluyentes.
- El intervalo de 2025 solo cubre el ruido normal de los meses. La regresión supone que la tendencia sigue igual y que el error tiene el mismo tamaño siempre, si algo cambia (aranceles, un cierre de frontera, otra crisis), el pronóstico no lo ve y como referencia, el error real en 2024 fue de unos 39,000 camiones por mes y el intervalo de 80% es de aprox 60,000.
- La variable de COVID fue una decisión mía (marzo a junio de 2020), y no probé con otras ventanas.
- Pronostico solo el total, los puertos pequeños (Práctica 7) son demasiado ruidosos para pronosticarse con tan pocos datos.
- Es una extrapolación de lo que pasó entre 2018 y 2024: describe la tendencia y la estacionalidad, no las causas.

## Conclusión

Una regresión sencilla (tendencia, mes del año y una variable para el COVID) pronostica mejor los camiones totales que modelos de series de tiempo más complejos, el cual se equivoca en promedio unos 29 mil camiones al mes (alrededor de 2.7% de error) contra 38 mil del baseline. Holt-Winters no mejora el baseline y SARIMA es peor. Para esta serie, corta y con una ruptura, ganó el modelo más simple y más fácil de explicar. Para 2025 pronostico unos 13.29 millones de camiones, un crecimiento leve de 0.9%, con la estacionalidad de siempre (diciembre el más bajo, marzo y octubre los más altos).

## Archivos en esta carpeta

- dataset_limpio.csv: dataset de la práctica 1
- pronostico.py: script con todo el proceso del forecasting
- pronostico_2025.csv: pronóstico mensual de 2025 con intervalo
- pronostico_prueba_2024.png: modelos contra los datos reales de 2024
- pronostico_2025.png: histórico y pronóstico de 2025
- README.md: este archivo