# Práctica 9 — Análisis de texto: nube de palabras y análisis exploratorio

## Dataset y texto que analicé

Mi dataset es casi todo numérico, así que el texto que tengo es el nombre del puerto y su estado (como por ejemplo, "Laredo, Texas" o "Sweetgrass, Montana"). Con eso armé un texto por puerto, las palabras de su nombre más su estado. Trabajé con los 102 puertos de dataset_limpio.csv (práctica 1) y para uno de los análisis, con los grupos de puertos de la práctica 7 (puertos_agrupados.csv).

## Por qué elegí este enfoque

Elegí hacer las nubes de palabras ponderadas por tráfico y no solo por frecuencia. Es un texto muy corto ya que hay 138 palabras distintas (contando los estados) y solo 20 aparecen en más de un puerto. Una nube por frecuencia casi solo mostraría los estados con más puertos. Al ponderar por camiones puedo preguntarme algo concreto ¿las palabras que más aparecen en el texto son las que más tráfico mueven? Además así conecto esta práctica con las anteriores (frontera de la práctica 6 y grupos de la práctica 7). Descarté usar texto externo (noticias o comunicados) para no depender de una fuente que no sale de mi dataset.

## Cómo preparé el texto

| Decisión | Qué hice | Por qué |
|---|---|---|
| Palabras | Separé los nombres en palabras y las pasé a minúsculas | Para que "Falls" y "falls" cuenten igual |
| Estados | Los dejé como una sola palabra (north dakota, new york, new mexico) | Si los separo, "new" mezcla New York con New Mexico y "north" no significa nada |
| Palabras quitadas | del, van, st y g | Son partes sueltas de nombres como "Del Rio", "Van Buren", "St John" y "Kenneth G Ward" que no dicen nada solas |
| Qué se quedó | Las demás palabras de los nombres, aunque sean nombres propios | Es lo que hay; no hay "palabras vacías" reales en un nombre de puerto |
| Peso por tráfico | Cada palabra pesa los camiones totales (2018-2024) de los puertos donde aparece | Es una definición sencilla; una palabra cuenta una vez por puerto |

Una limitación de ese peso: como un puerto aporta su tráfico a todas sus palabras, la suma de los porcentajes pasa de 100%. Por ejemplo, Laredo aporta sus camiones a "laredo" y a "texas". No es un error pero hay que leerlo como "camiones de los puertos donde aparece la palabra" y no como "camiones de la palabra".

Para cada palabra calculé también un índice como porcentaje de camiones entre porcentaje de puertos. Mayor a 1 significa que la palabra pesa más en tráfico que en cantidad de puertos.

## Resultados

### 1. Frecuencia contra tráfico (nube_frecuencia_vs_trafico.png)

Con frecuencia domina north dakota (18 puertos, 17.6%), seguido de texas, washington y montana (12 cada uno). Con tráfico la nube cambia completamente: dominan texas, laredo, michigan, california y detroit.

| Palabra | Puertos | % de camiones | Índice |
|---|---|---|---|
| texas | 12 | 38.6 | 3.3 |
| laredo | 1 | 21.0 | 21.4 |
| michigan | 3 | 18.7 | 6.4 |
| california | 3 | 11.9 | 4.0 |
| detroit | 1 | 11.8 | 12.0 |
| new york | 6 | 11.6 | 2.0 |
| falls | 4 | 7.4 | 1.9 |

La tabla completa está en palabras_tabla.csv. Un caso para leer con cuidado es "falls": aparece en 4 puertos, pero casi todo su tráfico (6.26 de 6.47 millones de camiones) viene de uno solo, Buffalo Niagara Falls. La palabra pesa mucho por un puerto, no porque los puertos con "falls" sean grandes en general. Algo parecido pasa con "port" (Port Huron).

### 2. Estados: cuántos puertos tienen y cuánto tráfico mueven (estados_puertos_vs_trafico.png)

| Estado | % de los puertos | % de los camiones |
|---|---|---|
| Texas | 11.8 | 38.6 |
| Michigan | 2.9 | 18.7 |
| California | 2.9 | 11.9 |
| New York | 5.9 | 11.6 |
| North Dakota | 17.6 | 3.1 |
| Montana | 11.8 | 1.4 |
| Minnesota | 6.9 | 0.4 |
| Alaska | 3.9 | 0.1 |

Cuatro estados (Texas, Michigan, California y New York) tienen 24 de los 102 puertos y mueven 80.8% de los camiones. En sentido contrario, North Dakota, Montana, Minnesota y Alaska tienen 41 puertos (40%) y mueven 5% del tráfico. Es decir, la cantidad de puertos de un estado casi no dice nada de cuánto tráfico mueve.

### 3. Frontera con México contra Canadá (nubes_mexico_canada.png)

- México: texas, laredo, california y otay mesa. El tráfico se concentra en pocos puertos grandes.
- Canadá: michigan, detroit, new york, falls y buffalo (este último, Buffalo Niagara Falls). Michigan y Nueva York concentran el tráfico canadiense.
- En ambas la nube tiene pocas palabras grandes y muchas pequeñas, y eso refleja que el tráfico está muy concentrado, como ya vi en la Práctica 2 con el sesgo.

### 4. Nubes por grupo de la Práctica 7 (nubes_por_grupo.png)

Aquí pesé por número de puertos, porque dentro de cada grupo los puertos son parecidos en tamaño.

| Grupo | Palabras más frecuentes |
|---|---|
| Grandes con tren (30) | maine (4), texas (4), washington (4), vermont (3) |
| Medianos estables (45) | maine (6), north dakota (6), texas (5), washington (5) |
| Pequeños en crecimiento (8) | montana (3), north dakota (2) |
| Pequeños que no se recuperaron (14) | north dakota (7), washington (3), montana (3) |

Lo que más llama la atención es el grupo de pequeños que no se recuperaron: 13 de sus 14 puertos están en North Dakota (7), Washington (3) o Montana (3), y el otro es de Minnesota. Los 14 son de la frontera con Canadá, como ya vi en la Práctica 7.

## Limitaciones

- El texto son nombres propios de lugares, no lenguaje natural. No hay significado que analizar (sentimiento, temas), solo qué palabras aparecen y cuánto tráfico las acompaña. Es un análisis exploratorio y descriptivo, no un modelo.
- Solo hay 102 textos, y casi todas las palabras aparecen una vez. Que una palabra tenga peso grande suele deberse a un solo puerto (laredo, detroit, buffalo).
- Los estados son la parte del texto que más se repite y ya traen su información geográfica. Parte de lo que veo es, en realidad, un análisis por estado con otra visualización.
- Dos puertos se llaman Eastport (Maine e Idaho). Los traté como puertos distintos, pero la palabra "eastport" los junta.
- El peso por tráfico se traslapa entre palabras (ver sección de preparación), así que los porcentajes no se pueden sumar.
- Las nubes sirven para ver, no para medir: el tamaño de una palabra se aprecia mejor en palabras_tabla.csv y en la gráfica de estados.

## Conclusión

Las palabras que más aparecen en los nombres de los puertos no son las que más tráfico mueven. North Dakota tiene más puertos que cualquier otro estado (17.6%) y mueve 3.1% de los camiones, mientras que Texas con 11.8% de los puertos, mueve 38.6%. Al ponderar por tráfico, la nube cambia de estados con muchos puertos pequeños a puertos concretos (Laredo, Detroit, Buffalo Niagara Falls) y a los estados donde están. Esto coincide con lo que encontré antes que es que el tráfico está muy concentrado en pocos puertos y la frontera con México o Canadá no explica por sí sola el tamaño. Los puertos pequeños que perdieron tráfico después del COVID están casi todos en North Dakota, Washington y Montana.

## Archivos en esta carpeta

- dataset_limpio.csv: dataset de la práctica 1
- puertos_agrupados.csv: grupos de puertos de la práctica 7
- analisis_texto.py: script con todo el proceso
- palabras_tabla.csv: puertos, camiones e índice por palabra
- nube_frecuencia_vs_trafico.png: nube por número de puertos y por camiones
- estados_puertos_vs_trafico.png: porcentaje de puertos contra porcentaje de camiones por estado
- nubes_mexico_canada.png: nubes por frontera, ponderadas por camiones
- nubes_por_grupo.png: nubes por grupo de la práctica 7
- README.md: este archivo