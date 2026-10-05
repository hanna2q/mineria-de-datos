"""
Practica 5 - Modelos Lineales y Correlación
Dataset: dataset_limpio.csv (práctica 1)
"""

# Flujo: 
# correlación -> modelo A (simple) -> diagnóstico de residuos -> iteración con transformación log -> modelo B (Múltiple)

import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
from pathlib import Path

CARPETA = Path(__file__).parent
RUTA_ENTRADA = CARPETA / "dataset_limpio.csv"

df = pd.read_csv(RUTA_ENTRADA)
df["date"] = pd.to_datetime(df["date"])
df["year"] = df["date"].dt.year

# Correlación
# primero que nada, se revisa la correlacion entre todas las variables numéricas para decidir (con evidencia) cual usar como predictor principal
print("")
print("MATRIZ DE CORRELACIÓN")
numericas = df[["trucks", "trains", "latitude", "longitude", "year"]]
print(numericas.corr().round(3))

# decisión tomada: al ver que "trains" tiene la correlación mas fuerte con "trucks" (0.626)
# y "latitude" tiene una correlación moderada (-0.369), usamos ambas

# Modelo A (regresión simple, trucks/trains)
print("")
print("MODELO A: trucks/trains (escala original)")
X_a = sm.add_constant(df["trains"])
y_a = df["trucks"]
modelo_a = sm.OLS(y_a, X_a).fit()
print(f"R2: {modelo_a.rsquared:.3f}")
print(f"Coeficiente trains: {modelo_a.params['trains']:.2f}  (p-value: {modelo_a.pvalues['trains']:.4f})")

# graficamos los residuos para verificar si el modelo cumple los supuestos de la regresión lineal
# (residuos aleatorios, sin patrón, varianza constante)
residuos_a = modelo_a.resid
predichos_a = modelo_a.predict(X_a)
plt.figure(figsize=(8, 5))
plt.scatter(predichos_a, residuos_a, alpha=0.3, s=15)
plt.axhline(0, color="red", linestyle="--")
plt.xlabel("Valores predichos")
plt.ylabel("Residuos")
plt.title("Residuos vs predichos - Modelo A (trucks ~ trains)")
plt.tight_layout()
plt.savefig(CARPETA / "diagnostico_residuos_modelo_a.png", dpi=120)
plt.close()
print("   Diagnóstico: los residuos muestran un patrón claro y un")
print("   abanico que crece (heterocedasticidad). Esto viola un supuesto")
print("   de la regresión lineal clásica, consistente con el sesgo fuerte")
print("   de trucks que fue detectado en la práctica 2 (skew=4.91).")

# Iteración (transformación logarítmica)
# Decisión: ya que el problema de heterocedasticidad, se aplica log1p() (log(x+1), para poder incluir los valores en 0 a ambas variables
# Es una técnica estándar para estabilizar la varianza en datos muy sesgados a la derecha (como los nuestros)
print("")
print("ITERACIÓN: Modelo A con transformación log")
df["log_trucks"] = np.log1p(df["trucks"])
df["log_trains"] = np.log1p(df["trains"])

X_log = sm.add_constant(df["log_trains"])
y_log = df["log_trucks"]
modelo_a_log = sm.OLS(y_log, X_log).fit()
print(f"R2: {modelo_a_log.rsquared:.3f}")
print(f"Skew de residuos antes: {residuos_a.skew():.2f}  ||  después: {modelo_a_log.resid.skew():.2f}")
print("   El R2 baja un poco (0.392 -> 0.307), pero la asimetría de los residuos mejora muchísimo")
print("   (1.95 -> -0.28), es decir, el modelo log es mas confiable aunque explique un poco menos varianza.")

# guardamos el diagnóstico de residuos del modelo log, para comparar visualmente contra el de la sección 2
residuos_a_log = modelo_a_log.resid
predichos_a_log = modelo_a_log.predict(X_log)
plt.figure(figsize=(8, 5))
plt.scatter(predichos_a_log, residuos_a_log, alpha=0.3, s=15)
plt.axhline(0, color="red", linestyle="--")
plt.xlabel("Valores predichos (log)")
plt.ylabel("Residuos")
plt.title("Residuos vs predichos - Modelo A con log (log_trucks ~ log_trains)")
plt.tight_layout()
plt.savefig(CARPETA / "diagnostico_residuos_modelo_a_log.png", dpi=120)
plt.close()

# Modelo B (regresión múltiple)
# Se agregan "latitude" (correlación moderada con trucks) y una variable dummy "es_mexico", 1 si el puerto esta en la frontera 
# con México y 0 si es Canadá (en la práctica 4 confirmamos que la frontera tiene una diferencia estadisticamente significativa en trucks
print("")
print("MODELO B: log_trucks y log_trains + latitude + es_mexico")
df["es_mexico"] = (df["border"] == "US-Mexico Border").astype(int)

X_b = sm.add_constant(df[["log_trains", "latitude", "es_mexico"]])
y_b = df["log_trucks"]
modelo_b = sm.OLS(y_b, X_b).fit()
print(modelo_b.summary())

# Gráfica final (valores reales vs predichos)
predichos_b = modelo_b.predict(X_b)
plt.figure(figsize=(7, 7))
plt.scatter(y_b, predichos_b, alpha=0.3, s=15, color="#2c5f8a")
lims = [y_b.min(), y_b.max()]
plt.plot(lims, lims, "r--", label="Predicción perfecta")
plt.xlabel("log(trucks) real")
plt.ylabel("log(trucks) predicho")
plt.title(f"Modelo B: valores reales vs predichos (R2 = {modelo_b.rsquared:.3f})")
plt.legend()
plt.tight_layout()
plt.savefig(CARPETA / "modelo_b_real_vs_predicho.png", dpi=120)
plt.close()

# Conclusión
print("")
print("CONCLUSIÓN")
print(f"""
- Modelo A (trucks/trains, escala original): R2 = {modelo_a.rsquared:.3f}
  Buen ajuste aparente, pero con residuos heterocedasticos (no confiable).

- Modelo A con log (log_trucks/log_trains): R2 = {modelo_a_log.rsquared:.3f}
  R2 mas bajo, con residuos mucho mas sanos (menos sesgo).

- Modelo B (log_trucks/log_trains + latitude + es_mexico): R2 = {modelo_b.rsquared:.3f}
  Mejor modelo: agregar la latitud y la frontera mejora el ajuste de forma
  significativa (vemos todas las variables con p<0.05) sin perder la
  estabilidad de los residuos que ganó la transformación log.

- Elegí el MODELO B como el modelo final: explica que el 48% de la variación en
  log(trucks), con supuestos estadísticos mas razonables que el modelo original sin transformar.
""")