# Práctica 7 — Agrupamiento de Datos con K-Means

## Dataset

- dataset_limpio.csv (resultado de la práctica 1)

## Qué decidí agrupar y por qué

Elegí agrupar puertos y no registros puerto-mes. En la Práctica 6 vi que el modelo KNN no aprendía a distinguir una frontera de otra, sino el "perfil" de cada puerto, con puertos que nunca había visto, el F1 bajó de 0.71 a unos 0.38. Si el puerto es la unidad que importa, tiene más sentido agruparlos directamente. Agrupar los 8090 registros solo me habría separado puertos grandes de chicos, porque cada puerto aparece unas 79 veces

Combiné dos preguntas:

- A, perfil de tráfico: ¿qué tipos de puerto hay según su volumen, si mueven trenes y qué tan variable es su tráfico?
- D, reacción al COVID: ¿hay puertos que reaccionaron distinto a 2020 y a la recuperación posterior?

Elegí D porque en la Práctica 4 el año no resultó significativo para el conjunto de puertos (Kruskal-Wallis con p = 0.92), pero ese resultado mezcla todos los puertos juntos, que son muy distintos entre sí. Quise ver si, por grupos, el COVID sí dejó huella.

## Construcción de las variables (una fila por puerto)

| Variable | Qué mide | Pregunta |
|---|---|---|
| log_trucks | Camiones promedio al mes (con log) | A |
| log_trains | Trenes promedio al mes (con log) | A |
| pct_meses_tren | % de meses con cruces de tren | A |
| cv_trucks | Variabilidad: desviación estándar / media de camiones | A |
| log_covid | log(tráfico 2020 / tráfico 2019) | D |
| log_recuperacion | log(tráfico 2023-24 / tráfico 2019) | D |

Decisiones:

- Log: trucks y trains están muy sesgados (Práctica 2), así sin log, Laredo o Detroit dominarían todas las distancias.
- Escalar: K-Means usa distancias, así que estandarizo las variables para que ninguna pese más solo por su unidad.
- Latitud y longitud fuera: repetirían la geografía y no aportarían un hallazgo (el mismo razonamiento de la Práctica 6).

### El caso de El Paso

Al calcular el impacto del COVID, El Paso salía con una caída enorme (2020 / 2019 = 0.34, y 0.14 en la recuperación). Al revisar vi que en marzo de 2020 el tráfico de camiones de El Paso pasó al cruce de Ysleta, en la misma ciudad (El Paso: 792 mil camiones en 2019 y 273 mil en 2020; Ysleta empieza en marzo de 2020 con 484 mil). Esto es una reubicación, no una caída real. Por eso traté El Paso, Ysleta y Tornillo como una sola unidad ("El Paso (complejo)"). Ya combinado, su tráfico de 2020 fue 0.96 del de 2019 y el de 2023-24 fue 0.99, es decir, no hubo caída real; de otro modo habría aparecido como un puerto que se hundió cuando solo cambió de ventanilla.

### Puertos excluidos

Quité 3 puertos por no tener datos en 2019, 2020 o 2023 y 2024, que necesito para calcular las variables de D: Ketchikan (1 mes de datos), Willow Creek (4 meses) y Whitlash (25 meses). Quedan 97 puertos.

## Elección de k

Probé k de 2 a 8 con las dos configuraciones (kmeans_codo_silueta.png), usando n_init=20 para que el resultado no dependa de una inicialización con mala suerte:

| k | Silueta A (4 variables) | Silueta A+D (6 variables) |
|---|---|---|
| 2 | 0.582 | 0.424 |
| 3 | 0.528 | 0.448 |
| 4 | 0.530 | 0.461 |
| 5 | 0.514 | 0.461 |
| 6 | 0.473 | 0.448 |
| 7 | 0.436 | 0.391 |

- A+D, no solo A: con solo A la silueta es mayor, pero esos grupos únicamente separan por tamaño y por si hay tren, y no responden mi pregunta sobre el COVID. Las siluetas de conjuntos de variables distintos no son del todo comparables, así que elegí por la pregunta y no por el número más alto.
- k = 4 y no 5: empatan en silueta (0.461). Con k = 5 el modelo solo separa dos puertos más (Ferry y Ambrose), de volumen minúsculo y muy variables, que en k = 4 caben en un grupo existente. Prefiero el modelo más sencillo.
- El codo no marca un quiebre muy claro: la inercia baja de forma gradual. Por eso me apoyé más en la silueta y en la interpretabilidad de los grupos.

## Resultados (k = 4, A+D)

| Grupo | Puertos | Camiones/mes (mediana) | Trenes/mes (mediana) | 2020 vs 2019 | 2023-24 vs 2019 | % frontera México |
|---|---|---|---|---|---|---|
| Grandes con tren | 30 | 10,083 | 41 | 0.96 | 0.97 | 23% |
| Medianos estables | 45 | 839 | 0 | 0.95 | 0.93 | 24% |
| Pequeños que no se recuperaron | 14 | 51 | 0 | 0.57 | 0.41 | 0% |
| Pequeños en crecimiento | 8 | 54 | 0 | 1.51 | 1.77 | 25% |

Gráficas: kmeans_pca_grupos.png (los grupos proyectados en 2 dimensiones con PCA) y kmeans_covid_recuperacion.png (cada puerto según su caída en 2020 y su recuperación).

Lo que veo:

- El tren separa a los puertos grandes. pct_meses_tren es casi binaria: los puertos con tren lo tienen prácticamente todos los meses (99%) y los demás nunca. Los 30 puertos "grandes con tren" mueven una mediana de 10 mil camiones al mes, unas 12 veces más que los medianos.
- Los puertos grandes y medianos casi no se movieron con el COVID: su tráfico de 2020 fue ~95% del de 2019 y en 2023-24 volvieron a ~93-97%.
- El efecto del COVID se concentra en puertos pequeños: 14 puertos perdieron en mediana 43% de su tráfico en 2020 (0.57) y en 2023-24 estaban en 41% de su nivel de 2019. Los 14 están en la frontera con Canadá (0% México). En sentido contrario, 8 puertos pequeños crecieron (1.77 veces su nivel de 2019); entre ellos están Roma y Lukeville, de la frontera con México.
- Los grupos no siguen la frontera. La concordancia entre los grupos y la frontera México/Canadá es prácticamente nula (ARI = -0.03), y cada grupo tiene entre 0% y 25% de puertos de México. Esto es consistente con la Práctica 6: el volumen y el comportamiento de un puerto no dependen de la frontera en la que está.

## Evaluación del modelo

- Silueta global: 0.461.
- Silueta por grupo: 0.52 (grandes con tren), 0.55 (medianos estables), 0.19 (pequeños en crecimiento) y 0.20 (pequeños que no se recuperaron). Los dos primeros grupos están bien definidos y los dos pequeños están poco definidos.
- Estabilidad: repetí el modelo 30 veces con una sola inicialización cada vez y lo comparé con el modelo final (ARI): media de 0.82 y mínimo de 0.58. La estructura general se mantiene, pero los límites de los grupos pequeños cambian según la inicialización.

## Limitaciones

- Solo hay 97 puertos, así que los grupos de 8 y 14 puertos son frágiles.
- Los puertos pequeños (unos 50 camiones al mes) tienen cocientes muy ruidosos: con tan pocos cruces, unos cuantos camiones cambian mucho la proporción 2020 / 2019. Por eso estos dos grupos tienen siluetas bajas y sus conclusiones son menos firmes que las de los grupos grandes.
- Lo que encontré describe qué pasó con el tráfico, no por qué. No puedo afirmar con estos datos que el COVID sea la causa de la caída de los 14 puertos.

## Conclusión

Agrupar los puertos por su perfil muestra una estructura clara: los puertos grandes (con tren) y los medianos son estables y, en conjunto, apenas cambiaron con el COVID. La diferencia aparece en un grupo pequeño de puertos que perdió mucho tráfico y no se ha recuperado. La frontera (México o Canadá) no explica ninguno de los grupos.

## Archivos en esta carpeta

- dataset_limpio.csv: dataset de la Práctica 1
- clustering_kmeans.py: script con todo el proceso
- puertos_agrupados.csv: perfil y grupo asignado a cada puerto
- kmeans_codo_silueta.png: método del codo y silueta para elegir k
- kmeans_pca_grupos.png: grupos proyectados con PCA
- kmeans_covid_recuperacion.png: impacto del COVID y recuperación por puerto
- README.md: este archivo