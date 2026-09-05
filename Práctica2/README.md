## Estadística descriptiva
| Métrica | trucks | trains |
|---|---|---|
| Media | 10,774.4 | 27.9 |
| Mediana | 844.5 | 0 |
| Desv. estándar | 29,296.1 | 68.9 |
| Mínimo | 0 | 0 |
| Máximo | 267,884 | 447 |
| Moda | 1 | 0 |
| Asimetría (skew) | 4.91 | 3.28 |

Interpretación: 

Ambas variables tienen una asimetría positiva muy fuerte, la media está muy por encima de la mediana en ambos casos. Esto indica que la
mayoría de los puertos manejan volúmenes bajos de cruces, mientras que un grupo pequeño de puertos (Laredo, Detroit) concentra volúmenes muy altos y eleva el promedio general.
La mediana de trains en 0 confirma que más de la mitad de los registros no tienen cruce de tren ese mes, muchos puertos solo manejan tráfico de camiones.

## Entidades y relaciones
El dataset combina dos entidades:
- PUERTO (estática): port_code (PK), port_name, state, border, latitude, longitude.
- CRUCE MENSUAL (transaccional): date, trucks, trains, con port_code como llave foránea hacia PUERTO.

Relación: un Puerto tiene muchos Cruces Mensuales (1:N).

## Métricas de datos agrupados
Por frontera: la frontera con México mueve en promedio 4.5x más camiones que la de Canadá (27,552 vs. 6,133 camiones/mes por puerto).

Por estado: Texas concentra por mucho el mayor volumen de camiones (33.7M en total 2018-2024), seguido de Michigan y California.

Por puerto: Laredo es el puerto con más tráfico combinado (18.4M), seguido de Detroit y Otay Mesa.

Por año: se observa una caída clara en 2020 (10,035 promedio mensual, coincide con el cierre de fronteras por COVID-19) y una recuperación sostenida hasta 2024 (11,226).

## Archivos en esta carpeta:
- estadistica_descriptiva.py — script cumpliendo los puntos de esta práctica
- diagrama_ER.pdf — diagrama entidad relación
- dataset_limpio.csv — datos limpios (resultado de la práctica 1)
- README.md — este archivo
