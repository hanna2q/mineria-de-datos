# Práctica 1 — Limpieza de Datos

## Dataset elegido:
Border Freight Crossings — cruces fronterizos de carga (camiones y trenes) hacia
Estados Unidos, por puerto de entrada y mes.
- Fuente: Bureau of Transportation Statistics
- Filtro aplicado: "measure" en (Trucks, Trains), fechas de enero 2018 a diciembre 2024
- Archivo original: "Border_Freight_Crossings.csv" (10,605 filas, dataset crudo)

## Por qué elegí este dataset:
Hace unos meses comencé a trabajar en una empresa de logística de embarques, al estar en constante
contacto con este tema me empezó a interesar cada vez más. Al principio pensé en pedir permiso para
usar un dataset real con datos de ahí, pero al no cumplir con la longitud requerida, opté por buscar 
uno del mismo tema en internet para no comprometer información.
Este  fue el dataset elegido ya que al revisarlo, sí cumplía con todos los requisitos de la rúbrica.

## Proceso de limpieza (limpieza.py)
1. Verificación inicial: no se encontraron nulos ni filas duplicadas exactas en el archivo original.
2. Tipos de datos: la columna `date` venía como texto; se convirtió a tipo fecha real para poder 
   agrupar por mes/año en prácticas posteriores.
3. Identificador de puerto: encontré dos puertos distintos llamados "Eastport" (uno en Idaho, otro 
   en Maine). Usar `port_name` como identificador generaba colisiones falsas, así que usé `port_code` 
   como identificador real.
4. Columna redundante: eliminé `point`, que solo repetía en texto la información ya presente en 
   `latitude` y `longitude`.
5. Valor en cero: se conservó una fila con `value = 0` (puerto Ambrose, ND, abril 2020) porque coincide
   con el cierre de fronteras por COVID-19 — es un dato real, no un valor faltante.
6. Pivoteo a formato ancho: el dataset original tenía una sola columna numérica de negocio (`value`), 
   con la categoría de camión/tren en `measure`. Se transformó a formato ancho para que cada fila sea un
   puerto+fecha único, con `trucks` y `trains` como columnas numéricas separadas.
7. Nulos generados por el pivoteo: no todos los puertos reportan ambas medidas cada mes. Los NaN 
   resultantes se imputaron con 0, ya que representan "no hubo cruces de ese tipo ese mes en ese puerto",
   no un dato perdido.

## Resultado:
- Filas finales: 8,090
- Columnas finales: `port_code`, `port_name`, `state`, `border`, `date`, `latitude`, `longitude`, `trains`, `trucks`
- Duplicados finales (`port_code` + `date`): 0
- Archivo de salida: dataset_limpio.csv

## Archivos en esta carpeta:
- Border_Freight_Crossings.csv — dataset original
- limpieza.py — script de limpieza de los datos
- dataset_limpio.csv — resultado final de los datos limpios
- README.md — este archivo
