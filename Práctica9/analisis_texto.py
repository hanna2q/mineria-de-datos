"""
Practica 9 - Analisis de texto
Dataset: dataset_limpio.csv (práctica 1) y puertos_agrupados.csv (práctica 7)
"""

import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
from pathlib import Path
from wordcloud import WordCloud

CARPETA = Path(__file__).parent
SEMILLA = 42

df = pd.read_csv(CARPETA / "dataset_limpio.csv")
grupos = pd.read_csv(CARPETA / "puertos_agrupados.csv")[["port_code", "grupo"]]

# un registro por puerto con su trafico total de camiones
puertos = df.groupby(["port_code", "port_name", "state", "border"], as_index=False)["trucks"].sum()

# el texto de cada puerto es su nombre mas su estado los estados se 
# dejan como una sola palabra (north_dakota) para que new york y new mexico no se mezclen en "new"
SIN_VALOR = {"del", "van", "st", "g"}


def palabras(fila):
    nombre = [w for w in re.findall(r"[a-z]+", fila["port_name"].lower()) if w not in SIN_VALOR]
    return nombre + [fila["state"].lower().replace(" ", "_")]


puertos["palabras"] = puertos.apply(palabras, axis=1)
total_camiones = puertos["trucks"].sum()

# tabla por palabra: puertos donde aparece y camiones de esos puertos
# cada puerto cuenta una vez por palabra, pero la suma entre palabras no es el total
filas = []
for w in sorted({w for lista in puertos["palabras"] for w in lista}):
    s = puertos[puertos["palabras"].apply(lambda l: w in l)]
    filas.append({"palabra": w, "n_puertos": len(s), "camiones": s["trucks"].sum()})
tabla = pd.DataFrame(filas)
tabla["pct_puertos"] = tabla["n_puertos"] / len(puertos) * 100
tabla["pct_camiones"] = tabla["camiones"] / total_camiones * 100

# indice > 1: la palabra pesa mas en tráfico que en cantidad de puertos
tabla["indice"] = tabla["pct_camiones"] / tabla["pct_puertos"]
tabla = tabla.sort_values("camiones", ascending=False)
tabla.round(2).to_csv(CARPETA / "palabras_tabla.csv", index=False)

print(f"Puertos: {len(puertos)} | palabras distintas: {len(tabla)}")
print(f"Palabras que aparecen en más de un puerto: {(tabla['n_puertos'] > 1).sum()}")

print("\nTop 10 por número de puertos")
print(tabla.sort_values(["n_puertos", "camiones"], ascending=False).head(10)
      [["palabra", "n_puertos", "pct_puertos"]].round(1).to_string(index=False))
print("\nTop 10 por camiones")
print(tabla.head(10)[["palabra", "n_puertos", "pct_camiones", "indice"]].round(1).to_string(index=False))

def nube(ax, pesos, titulo, color):
    pesos = {w.replace("_", " "): v for w, v in pesos.items()}
    wc = WordCloud(width=800, height=500, background_color="white",
                   color_func=lambda *a, **k: color, random_state=SEMILLA,
                   prefer_horizontal=1).generate_from_frequencies(pesos)
    ax.imshow(wc, interpolation="bilinear")
    ax.set_title(titulo)
    ax.axis("off")


# nube 1: frecuencia contra tráfico
fig, ejes = plt.subplots(1, 2, figsize=(14, 5.5))
nube(ejes[0], dict(zip(tabla["palabra"], tabla["n_puertos"])),
     "Por número de puertos", "#2c5f8a")
nube(ejes[1], dict(zip(tabla["palabra"], tabla["camiones"])),
     "Por camiones (tráfico 2018-2024)", "#c0601a")
plt.tight_layout()
plt.savefig(CARPETA / "nube_frecuencia_vs_trafico.png", dpi=120)
plt.close()

# estados: cuántos puertos tienen contra cuanto trafico mueven
estados = puertos.groupby("state").agg(puertos=("port_code", "size"), camiones=("trucks", "sum"))
estados["pct_puertos"] = estados["puertos"] / len(puertos) * 100
estados["pct_camiones"] = estados["camiones"] / total_camiones * 100
estados = estados.sort_values("pct_camiones")
print("\nEstados: % de puertos vs % de camiones")
print(estados[["puertos", "pct_puertos", "pct_camiones"]].round(1).iloc[::-1].to_string())

y = np.arange(len(estados))
plt.figure(figsize=(8, 6))
plt.barh(y + 0.2, estados["pct_puertos"], height=0.4, color="#2c5f8a", label="% de los puertos")
plt.barh(y - 0.2, estados["pct_camiones"], height=0.4, color="#d98c2b", label="% de los camiones")
plt.yticks(y, estados.index)
plt.xlabel("Porcentaje")
plt.title("Estados: cuántos puertos tienen y cuánto tráfico mueven")
plt.legend()
plt.tight_layout()
plt.savefig(CARPETA / "estados_puertos_vs_trafico.png", dpi=120)
plt.close()

# nubes por frontera, pesadas por camiones
fig, ejes = plt.subplots(1, 2, figsize=(14, 5.5))
for ax, (borde, titulo, color) in zip(ejes, [("US-Mexico Border", "Frontera con México", "#2e7d4f"),
                                           ("US-Canada Border", "Frontera con Canadá", "#6a4c93")]):
    pesos = Counter()
    for _, f in puertos[puertos["border"] == borde].iterrows():
        for w in f["palabras"]:
            pesos[w] += f["trucks"]
    nube(ax, dict(pesos), titulo + " (por camiones)", color)
    top = [w for w, _ in pesos.most_common(5)]
    print(f"\n{titulo}: palabras con más camiones -> {', '.join(top)}")
plt.tight_layout()
plt.savefig(CARPETA / "nubes_mexico_canada.png", dpi=120)
plt.close()

# nubes por grupo de la practica 7 por numero de puertos
# se juntan el paso, ysleta y tornillo como en la práctica 7
puertos["port_code_p7"] = puertos["port_code"].replace({2401: 2402, 2404: 2402})
g = puertos.merge(grupos, left_on="port_code_p7", right_on="port_code", suffixes=("", "_g"))
g = g.drop_duplicates("port_code_p7")
print(f"\nPuertos con grupo de la Práctica 7: {len(g)}")
fig, ejes = plt.subplots(2, 2, figsize=(14, 9))
for ax, (nombre, s), color in zip(ejes.ravel(), g.groupby("grupo"), ["#2c5f8a", "#c0601a", "#2e7d4f", "#6a4c93"]):
    cuenta = Counter(w for lista in s["palabras"] for w in lista)
    nube(ax, dict(cuenta), f"{nombre} ({len(s)} puertos)", color)
    print(f"{nombre}: {', '.join(f'{w} ({n})' for w, n in cuenta.most_common(4))}")
plt.tight_layout()
plt.savefig(CARPETA / "nubes_por_grupo.png", dpi=120)
plt.close()