"""
Práctica 4 - Pruebas Estadísticas
Dataset: dataset_limpio.csv (práctica 1)
"""

# Se comprueban diferencias entre grupos etiquetados (frontera, anio) usando pruebas no
# paramétricas (Mann-Whitney U y Kruskal-Wallis) justificadas por un test de normalidad previo

import pandas as pd
from scipy import stats
from pathlib import Path

CARPETA = Path(__file__).parent
RUTA_ENTRADA = CARPETA / "dataset_limpio.csv"

df = pd.read_csv(RUTA_ENTRADA)
df["date"] = pd.to_datetime(df["date"])
df["year"] = df["date"].dt.year

# Test de normalidad (para decidir que prueba usar después)

# ANOVA y la prueba t clásica asumen que los datos siguen una distribución normal,
# y sabemos por los resultados de la práctica 2 (skew=4.91) que "trucks" esta muy sesgado
# así que aquí lo confirmamos con una prueba formal antes de decidir

print("=" * 50)
print("TEST DE NORMALIDAD (D'Agostino-Pearson) (trucks)")
print("=" * 50)
stat_norm, p_norm = stats.normaltest(df["trucks"])
print(f"Estadístico: {stat_norm:.2f}  |  p-value: {p_norm:.8f}")

if p_norm < 0.05:
    print("   Se rechaza normalidad (p < 0.05)")
    print("   Decisión: usar pruebas NO parametricas (Mann-Whitney U y")
    print("   Kruskal-Wallis) en vez de la prueba t y ANOVA clásicas,")
    print("   porque estas últimas pierden confiabilidad con datos muy")
    print("   sesgados (como los nuestros en este caso)")
else:
    print("   No se rechaza normalidad. Se puede usar ANOVA/t clásicos")

# ya teniendo los resultados del test de normalidad (probados en terminal)
# se procede a las pruebas no paramétricas:

# Mann-Whitney U: trucks entre 2 grupos (fronteras)
# equivalente no paramétrico de la prueba t para 2 grupos independientes
print("\n" + "=" * 50)
print("Mann-Whitney U: trucks entre fronteras (Mexico vs Canada)")
print("=" * 50)

mexico = df[df["border"] == "US-Mexico Border"]["trucks"]
canada = df[df["border"] == "US-Canada Border"]["trucks"]

stat_mw, p_mw = stats.mannwhitneyu(mexico, canada, alternative="two-sided")
print(f"Estadístico U: {stat_mw:.0f}  |  p-value: {p_mw:.6f}")
print("Diferencia significativa (p<0.05)?", "SI" if p_mw < 0.05 else "NO")


# Kruskal-Wallis: trucks entre mas de 2 grupos (años)
# equivalente no paramétrico de ANOVA para más de 2 grupos independientes
print("\n" + "=" * 50)
print("Kruskal-Wallis: trucks entre los años (2018-2024)")
print("=" * 50)

grupos_por_anio = [df[df["year"] == y]["trucks"] for y in sorted(df["year"].unique())]
stat_kw, p_kw = stats.kruskal(*grupos_por_anio)
print(f"Estadístico H: {stat_kw:.2f}  |  p-value: {p_kw:.6f}")
print("Diferencia significativa (p<0.05)?", "SI" if p_kw < 0.05 else "NO")
print("")