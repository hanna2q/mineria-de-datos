# Práctica 3 — Visualización de Datos

## Dataset

- dataset_limpio.csv (resultado de la práctica 1).

## Gráficas generadas

Se generaron 5 tipos de gráficas distintas, usando un ciclo for para
automatizar los histogramas (en vez de repetir el mismo bloque de código
para cada variable).

### Histogramas (automatizados con un ciclo)

histograma_trucks.png, histograma_trains.png

Ambas distribuciones confirman el sesgo positivo fuerte detectado en la
práctica 2: la gran mayoría de los registros se concentra en valores bajos,
con una cola larga de puertos que mueven volúmenes mucho más altos.

### Diagrama de caja (trucks por frontera)

boxplot_trucks_por_frontera.png

La frontera con México no solo tiene una mediana más alta que la de Canadá,
sino que también muchos más valores atípicos (outliers) por encima de 150,000
camiones (puertos como Laredo que se disparan muy por encima del resto).

### Dispersión (trucks vs trains)

dispersion_trucks_trains.png

No hay una relación lineal clara entre ambas variables. En cambio, se
observan "nubes" de puntos separadas, que probablemente corresponden a
puertos distintos con comportamientos consistentes en el tiempo.

### Gráfica de pastel (proporción de trucks por frontera)

pastel_trucks_por_frontera.png

México concentra el 55.4% del total de camiones y Canadá el 44.6%. Es una
diferencia más chica de lo que sugería el promedio por puerto (esto lo podemos 
ver en el resultado de la práctica 2), esto es porque la frontera con Canadá tiene
muchos más puertos activos y entre todos suman un volumen total
comparable al de México.

### Gráfica de barras (Top 5 estados por total de trucks)

barras_top5_estados.png

Texas domina (33.7M), duplicando al segundo lugar (Michigan con
16.3M).

## Archivos en esta carpeta

- dataset_limpio.csv — dataset de la práctica 1
- visualizacion.py — script que genera las 5 gráficas
- graficas/ — carpeta con las 6 imágenes de las gráficas generadas
- README.md — este archivo