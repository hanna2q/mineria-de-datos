"""
Práctica 2 - Estadística Descriptiva
Dataset: dataset_limpio.csv (Práctica 1)
"""

import pandas as pd
from pathlib import Path

CARPETA = Path(__file__).parent
RUTA_ENTRADA = CARPETA / "dataset_limpio.csv"

df = pd.read_csv(RUTA_ENTRADA)
df["date"] = pd.to_datetime(df["date"])

# Estadística descriptiva de las variables numéricas (trucks, trains)
print("=" * 50)
print("ESTADÍSTICA DESCRIPTIVA (trucks, trains)")
print("=" * 50)

# Imprime una tabla con cuantos datos hay (count), el promedio (mean), qué tan dispersos están
# los datos (std), el valor mínimo, el máximo, y los cuartiles 25%/50%/75% (el 50% es la mediana)
descriptivos = df[["trucks", "trains"]].describe().round(2)
print(descriptivos)

# Imprime el valor que más se repite en cada columna
print("\nModa:")
print(f"  trucks: {df['trucks'].mode()[0]}")
print(f"  trains: {df['trains'].mode()[0]}")

# Imprime qué tan "inclinados" están los datos hacia un lado (skew) y qué tan concentrados son alrededor del promedio (kurtosis)
# números altos y positivos = pocos valores extremos jalan el promedio
print("\nAsimetria (skew) y curtosis:")
print(df[["trucks", "trains"]].skew().round(2))
print(df[["trucks", "trains"]].kurt().round(2))
# Ambas variables tienen asimetria positiva fuerte (cola larga a la derecha):
# pocos puertos muy grandes y elevan la media por encima de la mediana. 
# Por eso la mediana y la media son tan distintas en trucks (844.5 y 10,774.4)

# Métricas agrupadas por frontera, estado y puerto
print("\n" + "=" * 50)
print("MÉTRICAS AGRUPADAS")
print("=" * 50)

# Imprime el promedio de camiones y trenes, calculado por frontera
print("\nPromedio de trucks/trains por frontera:")
print(df.groupby("border")[["trucks", "trains"]].mean().round(1))

# Imprime los 5 estados que en total movieron más camiones, ordenados de mayor a menor
print("\nTop 5 estados por total de trucks:")
print(df.groupby("state")["trucks"].sum().sort_values(ascending=False).head(5))

# Crea una columna nueva (trucks + trains) e imprime los 5 puertos con más tráfico en total en todo el periodo 2018-2024
df["total"] = df["trucks"] + df["trains"]
print("\nTop 5 puertos por tráfico total (trucks + trains):")
print(df.groupby("port_name")["total"].sum().sort_values(ascending=False).head(5))

# Extrae el año de cada fecha, e imprime el promedio mensual de camiones por año (así se identifica la caída de 2020 por COVID)
df["year"] = df["date"].dt.year
print("\nPromedio mensual de trucks por año (tendencia temporal):")
print(df.groupby("year")["trucks"].mean().round(1))
print("")