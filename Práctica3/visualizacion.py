"""
Práctica 3 - Visualización de Datos
Dataset: dataset_limpio.csv (práctica 1)
"""

#En este códigos se generan 5 tipos de gráficas distintas: 
# histogramas, boxplot, dispersión, pastel y barras.

import pandas as pd
import matplotlib.pyplot as plt

from pathlib import Path

CARPETA = Path(__file__).parent
RUTA_ENTRADA = CARPETA / "dataset_limpio.csv"
CARPETA_GRAFICAS = CARPETA / "graficas"
CARPETA_GRAFICAS.mkdir(exist_ok=True)

df = pd.read_csv(RUTA_ENTRADA)
df["date"] = pd.to_datetime(df["date"])

# HISTOGRAMAS
columnas_numericas = ["trucks", "trains"]
for columna in columnas_numericas:
    plt.figure(figsize=(8, 5))
    plt.hist(df[columna], bins=40, color="#2c5f8a", edgecolor="white")
    plt.title(f"Histograma de {columna}")
    plt.xlabel(columna)
    plt.ylabel("Frecuencia")
    plt.tight_layout()
    plt.savefig(CARPETA_GRAFICAS / f"histograma_{columna}.png", dpi=120)
    plt.close()
print("Histogramas generados para:", columnas_numericas)

# DIAGRAMA DE CAJA (boxplot)
# Compara la distribución de 'trucks' entre las dos fronteras y muestra
# los valores atípicos como puntos fuera de la caja
fig, ax = plt.subplots(figsize=(8, 5))
data_por_frontera = [
    df[df["border"] == b]["trucks"] for b in df["border"].unique()
]
ax.boxplot(data_por_frontera, labels=df["border"].unique())
ax.set_title("Diagrama de caja: trucks por frontera")
ax.set_ylabel("trucks")
plt.tight_layout()
plt.savefig(CARPETA_GRAFICAS / "boxplot_trucks_por_frontera.png", dpi=120)
plt.close()

# DIAGRAMA DE DISPERSIÓN (scatter)
# Explora si existe relación entre el volumen de camiones y de trenes por puerto y mes
plt.figure(figsize=(8, 5))
plt.scatter(df["trucks"], df["trains"], alpha=0.4, color="#8a4a2c", s=15)
plt.title("Dispersion: trucks vs trains")
plt.xlabel("trucks")
plt.ylabel("trains")
plt.tight_layout()
plt.savefig(CARPETA_GRAFICAS / "dispersion_trucks_trains.png", dpi=120)
plt.close()

# GRÁFICA DE PASTEL
# Muestra que porcentaje del total de camiones se mueve por cada frontera (México y Canada)
total_por_frontera = df.groupby("border")["trucks"].sum()
plt.figure(figsize=(6, 6))
plt.pie(
    total_por_frontera,
    labels=total_por_frontera.index,
    autopct="%1.1f%%",
    colors=["#2c5f8a", "#8a4a2c"],
)
plt.title("Proporcion de trucks por frontera")
plt.tight_layout()
plt.savefig(CARPETA_GRAFICAS / "pastel_trucks_por_frontera.png", dpi=120)
plt.close()

# GRÁFICA DE BARRAS
# Top 5 estados por total de trucks
top5_estados = (
    df.groupby("state")["trucks"].sum().sort_values(ascending=False).head(5)
)
plt.figure(figsize=(8, 5))
plt.bar(top5_estados.index, top5_estados.values, color="#2c5f8a")
plt.title("Top 5 estados por total de trucks (2018-2024)")
plt.ylabel("Total de trucks")
plt.xticks(rotation=20)
plt.tight_layout()
plt.savefig(CARPETA_GRAFICAS / "barras_top5_estados.png", dpi=120)
plt.close()

print("Las gráficas se guardaron en la carpeta 'graficas/'")