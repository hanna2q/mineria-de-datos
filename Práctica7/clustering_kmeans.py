"""
Practica 7 - Agrupamiento de datos (clustering) con K-Means
Dataset: dataset_limpio.csv (práctica 1) y puertos_agrupados.csv (generado aquí)
"""

# puertos agrupados por perfil de trafico y por reaccion al covid

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FuncFormatter, NullFormatter
from pathlib import Path
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, silhouette_samples, adjusted_rand_score

CARPETA = Path(__file__).parent
SEMILLA = 42

df = pd.read_csv(CARPETA / "dataset_limpio.csv", parse_dates=["date"])

# en marzo de 2020 el trafico de camiones de el paso, pasó a ysleta (misma ciudad), asi que los tres cruces 
# se tratan como una sola unidad si no, el paso aparecia como un puerto que se hundio cuando solo cambio de ventanilla
df["unidad"] = df["port_code"].replace({2401: 2402, 2404: 2402})
mensual = df.groupby(["unidad", "date"], as_index=False)[["trucks", "trains"]].sum()
mensual["year"] = mensual["date"].dt.year
info = df.groupby("unidad").agg(nombre=("port_name", "first"), border=("border", "first"))
info.loc[2402, "nombre"] = "El Paso (complejo)"

# perfil de cada puerto
g = mensual.groupby("unidad")
puertos = pd.DataFrame({
    "trucks_prom": g["trucks"].mean(),
    "trains_prom": g["trains"].mean(),
    "pct_meses_tren": g["trains"].apply(lambda s: (s > 0).mean()),
    "cv_trucks": g["trucks"].std() / g["trucks"].mean(),
}).join(info)

anual = mensual.pivot_table(index="unidad", columns="year", values="trucks", aggfunc="mean")
puertos["covid"] = anual[2020] / anual[2019]
puertos["recuperacion"] = anual[[2023, 2024]].mean(axis=1) / anual[2019]

# se excluyen los puertos sin datos en 2019, 2020 o 2023-24
# porque sin ellos no se pueden calcular las variables del covid
excluidos = puertos[puertos.isna().any(axis=1)]["nombre"].tolist()
puertos = puertos.dropna()
print(f"Puertos analizados: {len(puertos)}")
print(f"Excluidos por no tener datos en 2019, 2020 o 2023-24: {excluidos}")

# log porque trucks y trains estan muy sesgados (practica 2)
# sin log, laredo y detroit dominarian todas las distancias
puertos["log_trucks"] = np.log1p(puertos["trucks_prom"])
puertos["log_trains"] = np.log1p(puertos["trains_prom"])
puertos["log_covid"] = np.log(puertos["covid"])
puertos["log_recuperacion"] = np.log(puertos["recuperacion"])

# a = perfil de trafico, d = reaccion al covid
# y pruebo con y sin d para ver si aporta algo
VARS_A = ["log_trucks", "log_trains", "pct_meses_tren", "cv_trucks"]
VARS_AD = VARS_A + ["log_covid", "log_recuperacion"]
frontera = (puertos["border"] == "US-Mexico Border").astype(int)

# eleccion de variables y de k
def barrido(cols, ks=range(2, 9)):
    # se escala porque kmeans usa distancias
    X = StandardScaler().fit_transform(puertos[cols])
    filas = []
    for k in ks:
        # n_init=20 para que el resultado no dependa de una mala inicializacion
        km = KMeans(k, n_init=20, random_state=SEMILLA).fit(X)
        filas.append((k, km.inertia_, silhouette_score(X, km.labels_)))
    return pd.DataFrame(filas, columns=["k", "inercia", "silueta"]).set_index("k")

res_a = barrido(VARS_A)
res_ad = barrido(VARS_AD)
print("\nSolo perfil de tráfico (A, 4 variables)")
print(res_a.round(3))
print("\nPerfil de tráfico + COVID (A+D, 6 variables)")
print(res_ad.round(3))

fig, ejes = plt.subplots(1, 2, figsize=(11, 4.5))
for res, nombre, color in [(res_a, "A (4 variables)", "#2c5f8a"),
                           (res_ad, "A+D (6 variables)", "#d98c2b")]:
    ejes[0].plot(res.index, res["inercia"], marker="o", label=nombre, color=color)
    ejes[1].plot(res.index, res["silueta"], marker="o", label=nombre, color=color)
# k=4 empata en silueta con k=5, pero k=5 solo separa a ferry y ambrose
# (dos puertos minusculos), asi que se prefiere el modelo mas sencillo
K = 4
for ax, titulo, ylab in zip(ejes, ["Método del codo", "Índice de silueta"],
                            ["Inercia", "Silueta promedio"]):
    ax.axvline(K, color="gray", linestyle="--", label=f"k elegido = {K}")
    ax.set_title(titulo)
    ax.set_xlabel("k (número de grupos)")
    ax.set_ylabel(ylab)
    ax.legend()
plt.tight_layout()
plt.savefig(CARPETA / "kmeans_codo_silueta.png", dpi=120)
plt.close()

# modelo final (k=4)
X = StandardScaler().fit_transform(puertos[VARS_AD])
modelo = KMeans(K, n_init=20, random_state=SEMILLA).fit(X)
puertos["cluster"] = modelo.labels_

# los clusters salen numerados sin orden, asi que se nombran segun sus medianas
# para que el nombre no dependa del numero que le toque a cada grupo
def nombrar(s):
    if s["pct_meses_tren"].mean() > 0.5:
        return "Grandes con tren"
    if s["recuperacion"].median() < 0.7:
        return "Pequeños que no se recuperaron"
    if s["recuperacion"].median() > 1.2:
        return "Pequeños en crecimiento"
    return "Medianos estables"

nombres = {c: nombrar(s) for c, s in puertos.groupby("cluster")}
puertos["grupo"] = puertos["cluster"].map(nombres)

print(f"\nModelo final: k={K}, silueta={silhouette_score(X, modelo.labels_):.3f}")
resumen = puertos.groupby("grupo").agg(
    puertos=("nombre", "size"),
    trucks_mediana=("trucks_prom", "median"),
    trains_mediana=("trains_prom", "median"),
    pct_tren=("pct_meses_tren", "mean"),
    cv_trucks=("cv_trucks", "median"),
    covid_2020_vs_2019=("covid", "median"),
    recuperacion_vs_2019=("recuperacion", "median"),
    pct_mexico=("border", lambda s: (s == "US-Mexico Border").mean()),
).round(2)
print(resumen.to_string())

sil = silhouette_samples(X, modelo.labels_)
print("\nSilueta por grupo:")
print(pd.Series(sil, index=puertos.index).groupby(puertos["grupo"]).mean().round(3))

# ari cercano a 0 = los grupos no coinciden con la frontera
print("\nConcordancia con la frontera (ARI):",
      round(adjusted_rand_score(frontera, modelo.labels_), 3))

# 30 corridas con una sola inicializacion para ver cuanto cambian los grupos
etiquetas = [KMeans(K, n_init=1, random_state=s).fit_predict(X) for s in range(30)]
ari = [adjusted_rand_score(modelo.labels_, e) for e in etiquetas]
print(f"Estabilidad con 30 inicializaciones sueltas (ARI): media={np.mean(ari):.2f}, mínimo={min(ari):.2f}")

for grupo, s in puertos.groupby("grupo"):
    if len(s) <= 15:
        print(f"\n{grupo}: {', '.join(s['nombre'])}")

puertos.reset_index().rename(columns={"unidad": "port_code"}).to_csv(
    CARPETA / "puertos_agrupados.csv", index=False)

# graficas
colores = dict(zip(sorted(set(nombres.values())), ["#2c5f8a", "#d98c2b", "#4c9a6a", "#a23b72"]))

pca = PCA(2, random_state=SEMILLA).fit(X)
Z = pca.transform(X)
plt.figure(figsize=(8, 6))
for grupo, s in puertos.groupby("grupo"):
    m = (puertos["grupo"] == grupo).values
    plt.scatter(Z[m, 0], Z[m, 1], label=f"{grupo} ({m.sum()})", color=colores[grupo], alpha=0.8, s=40)
plt.xlabel(f"Componente 1 ({pca.explained_variance_ratio_[0]:.0%} de la varianza)")
plt.ylabel(f"Componente 2 ({pca.explained_variance_ratio_[1]:.0%} de la varianza)")
plt.title("Grupos de puertos (K-Means, k=4) proyectados con PCA")
plt.legend(loc="upper left", bbox_to_anchor=(1.01, 1))
plt.tight_layout()
plt.savefig(CARPETA / "kmeans_pca_grupos.png", dpi=120)
plt.close()

plt.figure(figsize=(8, 6))
for grupo, s in puertos.groupby("grupo"):
    plt.scatter(s["covid"], s["recuperacion"], label=grupo, color=colores[grupo], alpha=0.8, s=40)
plt.axvline(1, color="gray", linestyle="--", linewidth=1)
plt.axhline(1, color="gray", linestyle="--", linewidth=1)
plt.xscale("log")
plt.yscale("log")
marcas = [0.2, 0.4, 0.6, 1, 1.5, 2, 3]
for ax_ in (plt.gca().xaxis, plt.gca().yaxis):
    ax_.set_major_locator(FixedLocator(marcas))
    ax_.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
    ax_.set_minor_formatter(NullFormatter())
plt.xlabel("Tráfico 2020 / tráfico 2019 (escala log)")
plt.ylabel("Tráfico 2023-24 / tráfico 2019 (escala log)")
plt.title("Impacto del COVID y recuperación por puerto")
plt.legend()
plt.tight_layout()
plt.savefig(CARPETA / "kmeans_covid_recuperacion.png", dpi=120)
plt.close()