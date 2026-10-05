# Práctica 5 — Modelos Lineales y Correlación

## Dataset

- dataset_limpio.csv (resultado de la práctica 1).

## 1. Correlación (antes de modelar)

Antes de construir cualquier modelo, se revisó la correlación entre todas
las variables numéricas para decidir con evidencia, cuáles usar como
predictores:

| | trucks | trains | latitude |
|---|---|---|---|
| trucks | 1.000 | 0.626 | -0.369 |

**Decisión:** trains tiene la correlación más fuerte con trucks
(0.626), así que se usa como predictor principal. por otra parte, latitude también
muestra una correlación moderada (-0.369, lo cual tiene sentido porque los puertos más
al sur, cerca de México, mueven más camiones), así que se incorpora
después en un segundo modelo.

## 2. Modelo A: regresión simple (trucks / trains)

**R2 = 0.392** — trains explica el 39.2% de la variación en trucks,
relación estadísticamente significativa (p ≈ 0).

**Diagnóstico de residuos** (diagnostico_residuos_modelo_a.png): al
graficar los residuos, se observa un patrón claro y un "abanico" que
crece: heterocedasticidad, un supuesto violado de la regresión
lineal clásica. Esto es consistente con el sesgo fuerte de trucks
detectado desde la práctica 2 (skew = 4.91).

## 3. Iteración: transformación logarítmica

**Decisión:** dado el problema de heterocedasticidad, se aplicó log1p()
(logaritmo de x+1, para poder incluir los valores en 0) a trucks y trains. 
Es una técnica estándar para estabilizar la varianza en datos muy sesgados a la derecha.

**Resultado:** el R2 bajó de 0.392 a 0.307, pero la asimetría de los
residuos mejoró drásticamente (de 1.95 a -0.28, casi simétrica, lo cual lo podemos
ver en diagnostico_residuos_modelo_a_log.png). Se prioriza la confiabilidad
del modelo sobre un R2 más alto pero engañoso.

## 4. Modelo B: regresión múltiple

Se agregan dos variables al modelo logarítmico:
- latitude (correlación moderada con trucks)
- es_mexico (variable dummy: 1 si el puerto está en la frontera con
  México, 0 si es Canadá), esto lo usamos porque en la práctica 4 
  confirmamos con Mann-Whitney U que la diferencia entre fronteras es
  estadísticamente significativa.

R2 = 0.478: las tres variables son significativas (p < 0.05). Mejora
real de 0.307 a 0.478 sin perder la estabilidad de los residuos ganada
con la transformación log.

Ver modelo_b_real_vs_predicho.png: los puntos se agrupan alrededor de
la línea de predicción perfecta, con dispersión considerable (el modelo
capta una tendencia real pero está lejos de ser perfecto).

## Conclusión

| Modelo | R2 | Observación |
|---|---|---|
| A: trucks / trains (original) | 0.392 | Residuos heterocedásticos, no confiable |
| A: log_trucks / log_trains | 0.307 | R2 más bajo, residuos mucho más sanos |
| B: log_trucks / log_trains + latitude + es_mexico | 0.478 | Mejor modelo: más variables, residuos estables |

Elegimos el Modelo B como el final: explica el 48% de la variación en
log(trucks), con supuestos estadísticos más razonables que el modelo
original sin transformar. El R2 no es altísimo porque, como se vimos desde
la práctica 3, el tráfico de camiones depende de muchos factores propios
de cada puerto (infraestructura, tamaño de la ciudad, tipo de industria)
que no están capturados en estas variables (lo cual es una limitación real y
esperada, no un error del proceso).

## Archivos en esta carpeta

- dataset_limpio.csv — dataset de la práctica 1
- modelo_lineal.py — script con correlación, Modelo A, iteración log y Modelo B
- diagnostico_residuos_modelo_a.png — residuos del Modelo A (escala original)
- diagnostico_residuos_modelo_a_log.png — residuos del Modelo A (con log)
- modelo_b_real_vs_predicho.png — valores reales vs. predichos del Modelo B
- README.md — este archivo