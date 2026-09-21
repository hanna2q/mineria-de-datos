# Práctica 4 — Pruebas Estadísticas

## Dataset

- dataset_limpio.csv (resultado de la práctica 1).

## 1. Test de normalidad

ANOVA y la prueba t clásica asumen que los datos siguen una distribución
normal. Ya en la Práctica 2 detectamos mediante las pruebas un sesgo fuerte
en trucks (skew = 4.91) y aquí se confirma formalmente con un test de normalidad
D'Agostino-Pearson:

- p-value es aproximadamente 0: rechazamos la normalidad

**Decisión:** en lugar de usar la prueba ANOVA y la prueba t clásicas, usaremos
sus equivalentes no paramétricos (Mann-Whitney U y Kruskal-Wallis), los cuales
no asumen normalidad y son más confiables para datos tan sesgados como estos

## 2. Mann-Whitney U: (trucks entre fronteras)

Compara si el volumen de camiones difiere entre las dos fronteras
(2 grupos independientes)

- p-value es aproximadamente 0: es una diferencia estadísticamente significativa

**Interpretación:** hay evidencia estadística sólida de que el volumen
de camiones por puerto es distinto entre la frontera con México y la
frontera con Canadá (no es una diferencia que se pueda atribuir al azar),
esto respalda el hallazgo de la Práctica 2 (México con 4.5x más camiones
en promedio por puerto)

## 3. Kruskal-Wallis: (trucks entre años)

Compara si el volumen de camiones difiere entre los 7 años (2018-2024) del dataset
(con más de 2 grupos independientes)

- p-value = 0.92: no hay diferencia estadísticamente significativa

**Interpretación:** aunque en la Práctica 2 se observó una caída en el
promedio de 2020 (posiblemente por COVID-19), esta prueba muestra que
esa diferencia no es estadísticamente significativa una vez que se
considera la enorme variabilidad entre los puertos. Es decir, la variación 
entre puertos es tan grande que "esconde" cualquier efecto real del año.

Estos resultados son un buen ejemplo de por qué una prueba
estadística formal puede contradecir lo que parece obvio en una
gráfica de promedios, pero eso no basta para decir que la diferencia
es real y no producto de la variabilidad natural de los datos.

## Archivos en esta carpeta

- dataset_limpio.csv — dataset de la práctica 1
- pruebas_estadisticas.py — script con las 3 pruebas
- README.md — este archivo