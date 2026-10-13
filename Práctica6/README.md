# Práctica 6 — Clasificación de Datos con KNN

## Dataset

- dataset_limpio.csv (resultado de la práctica 1).

El objetivo es: ¿podemos saber si un registro pertenece a la frontera con
México o con Canadá usando solo el volumen de trucks y trains?

- Variable objetivo: border (1 = México, 0 = Canadá).
- Algoritmo: K Vecinos Más Cercanos (KNN).

## Baseline

Las clases están desbalanceadas, ya que contamos con 6,337 registros de Canadá 
(78.3%) y 1,753 de México (21.7%). Un modelo que siempre responda "Canadá" ya 
tendría un accuracy de aproximadamente 0.783, así que el accuracy no basta para evaluar. 
Se reportan también la precisión, recall y F1 de la clase minoritaria (en este 
caso corrersponde a México).

## Decisiones del modelo

| Decisión | Evidencia | Qué se decidió |
|---|---|---|
| Variables | Con latitude y longitude el accuracy es 1.000 (los puertos de México están al sur) | Descartarlas: no aportan un hallazgo, solo repiten la geografía |
| Escalado | Sin escalar: acc 0.841 / F1 0.590. Con StandardScaler: acc 0.886 / F1 0.716 | Escalar. KNN usa distancias y trucks (cientos de miles) dominaba a trains (cientos) |
| Transformación log | Con split aleatorio es casi igual (0.885 vs 0.886). Con puertos nuevos mejora (acc 0.751 a 0.812) | Aplicamos log1p, consistente con el sesgo detectado en las prácticas anteriores (2 y 5) |
| Valor de k | Validación cruzada de 5 folds (ver la imagen generada k vs f1) | k = 7 |

Sobre k: con k=1 el modelo memoriza el ruido (F1 = 0.625) y con k muy
grande se suaviza de más. k=7 está en la zona estable, empata con el mejor
valor en la validación aleatoria (0.738) y es el mejor en la validación por
puerto (0.377).

## Resultados del modelo final

| Métrica | Valor |
|---|---|
| Accuracy | 0.888 (baseline: 0.783) |
| Precision (México) | 0.801 |
| Recall (México) | 0.641 |
| F1 (México) | 0.712 |

Matriz de confusión:

| | Predicho Canadá | Predicho México |
|---|---|---|
| Real Canadá | 1211 | 56 |
| Real México | 126 | 225 |

El modelo es conservador con México: cuando dice "México" acierta el 80% de
las veces (precision), pero solo detecta el 64% de los registros que
realmente son de México (recall); 126 registros de México se clasificaron
como Canadá.

## Prueba de estrés (los puertos que el modelo no llegó a considerar)

Cada puerto aparece aproximadamente 79 veces (un registro por mes). Con un split 
aleatorio, meses del mismo puerto quedan en entrenamiento y en prueba, y el modelo
puede "reconocer" un puerto por su volumen típico. Para medir qué tanto
generaliza, se separó por puerto (GroupShuffleSplit y GroupKFold), de
modo que el test contiene puertos totalmente nuevos:

| Evaluación | Accuracy | F1 (México) |
|---|---|---|
| Split aleatorio 80/20 | 0.888 (baseline 0.783) | 0.712 |
| Split por puerto (21 puertos nuevos) | 0.816 (baseline 0.747) | 0.576 |
| Validación cruzada por puerto (5 folds) | — | 0.377 |

La diferencia entre 0.576 y 0.377 se debe a que el resultado depende mucho de
qué puertos caen en el test; la validación cruzada promedia 5 combinaciones
y es la medida más estable.

## Conclusión

- Con puertos ya conocidos, el volumen de camiones y trenes permite predecir
  la frontera con un accuracy de 0.888 (más 10.5 puntos sobre el baseline) y un
  F1 de 0.712 para México.
- Con puertos nuevos el desempeño cae a un F1 cercano a 0.38. El volumen de
  carga por sí solo no distingue bien una frontera de la otra; lo que el
  modelo aprende es sobre todo el perfil de volumen de cada puerto.
- Esto es coherente con lo visto anteriormente en la práctica 3, donde la gráfica de
  dispersión mostraba algunas "nubes" separadas que correspondían a puertos
  individuales, y anticipa que un agrupamiento debería encontrar grupos
  de puertos por perfil de tráfico más que por frontera.

## Archivos en esta carpeta

- dataset_limpio.csv — dataset de la práctica 1
- clasificacion_knn.py — script con todo el proceso
- knn_k_vs_f1.png — elección de k con validación cruzada
- knn_matriz_confusion.png — matriz de confusión del modelo final
- README.md — este archivo