"""
Practica 8 - Pronóstico (Forecasting)
Dataset: dataset_limpio.csv (práctica 1) y pronostico_2025.csv (generado aquí)
"""

# Pronóstico de camiones totales por mes

import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
from pathlib import Path
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.statespace.sarimax import SARIMAX

warnings.filterwarnings("ignore")
CARPETA = Path(__file__).parent

df = pd.read_csv(CARPETA / "dataset_limpio.csv", parse_dates=["date"])
serie = df.groupby("date")["trucks"].sum().asfreq("MS")
print(f"Meses: {len(serie)} ({serie.index.min():%Y-%m} a {serie.index.max():%Y-%m})")


# variables para la regresión
def disenio(indice, covid):
    X = pd.DataFrame(index=indice)
    X["tendencia"] = (indice.year - 2018) * 12 + indice.month
    for m in range(2, 13):
        X[f"mes_{m}"] = (indice.month == m).astype(int)
    if covid:
        # marzo a junio de 2020, los meses con la caída fuerte
        X["covid"] = ((indice >= "2020-03-01") & (indice <= "2020-06-01")).astype(int)
    return sm.add_constant(X, has_constant="add")


# cada modelo recibe train y el indice a pronosticar, y regresa un pronóstico
def naive_estacional(train, idx):
    # mismo mes del ultimo año observado
    return pd.Series(train.iloc[-12:].values, index=idx[:12]).reindex(idx).ffill()


def regresion(covid):
    def f(train, idx):
        m = sm.OLS(np.log(train), disenio(train.index, covid)).fit()
        return np.exp(m.predict(disenio(idx, covid)))
    return f


def holt_winters(train, idx):
    m = ExponentialSmoothing(train, trend="add", damped_trend=True,
                             seasonal="mul", seasonal_periods=12).fit()
    return m.forecast(len(idx))


def sarima(train, idx):
    m = SARIMAX(train, order=(1, 1, 1), seasonal_order=(0, 1, 1, 12)).fit(disp=False)
    return m.forecast(len(idx))


modelos = {
    "Naive estacional (baseline)": naive_estacional,
    "Regresion sin COVID": regresion(False),
    "Regresion con COVID": regresion(True),
    "Holt-Winters": holt_winters,
    "SARIMA(1,1,1)(0,1,1,12)": sarima,
}


def metricas(real, pred):
    e = real - pred
    return {"MAE": e.abs().mean(), "RMSE": np.sqrt((e ** 2).mean()),
            "MAPE %": (e.abs() / real).mean() * 100}


# evaluación: se corta en el tiempo, nunca al azar
cortes = {"Prueba 2024 (train 2018-2023)": "2023-12-01",
          "Prueba 2023 (train 2018-2022)": "2022-12-01"}
predicciones = {}
for nombre_corte, fin in cortes.items():
    train = serie[:fin]
    test = serie[serie.index > fin].iloc[:12]
    filas = {}
    for nombre, f in modelos.items():
        pred = f(train, test.index)
        filas[nombre] = metricas(test, pred)
        predicciones[(nombre_corte, nombre)] = pred
    tabla = pd.DataFrame(filas).T.round(1)
    print(f"\n{nombre_corte}")
    print(tabla.to_string())

# gráfica de la prueba 2024
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(serie["2022":].index, serie["2022":] / 1e6, color="black", lw=2, label="Real")
colores = ["#999999", "#d98c2b", "#a23b72", "#4c9a6a", "#2c5f8a"]
for (corte, nombre), c in zip([k for k in predicciones if k[0].startswith("Prueba 2024")], colores):
    p = predicciones[(corte, nombre)]
    ax.plot(p.index, p / 1e6, color=c, ls="--", label=nombre)
ax.axvline(pd.Timestamp("2023-12-15"), color="gray", lw=1)
ax.set_ylabel("Camiones al mes (millones)")
ax.set_title("Pronóstico contra datos reales de 2024")
ax.legend(fontsize=8)
plt.tight_layout()
plt.savefig(CARPETA / "pronostico_prueba_2024.png", dpi=120)
plt.close()

# residuos del mejor modelo de regresión, para revisar si queda estructura
train = serie[:"2023-12-01"]
m_reg = sm.OLS(np.log(train), disenio(train.index, True)).fit()
print(f"\nRegresion con COVID (train 2018-2023): R2 en log = {m_reg.rsquared:.3f}")
print("Coeficientes con p<0.05:")
print(m_reg.params[m_reg.pvalues < 0.05].round(4).to_string())

# promedio del MAE en las dos pruebas para elegir el modelo final
print("\nMAE promedio de las dos pruebas:")
mae = {n: np.mean([metricas(serie[serie.index > fin].iloc[:12],
                            predicciones[(c, n)])["MAE"] for c, fin in cortes.items()])
       for n in modelos}
print(pd.Series(mae).round(0).sort_values().to_string())

# pronóstico final 2025: regresión con covid reentrenada con toda la serie
futuro = pd.date_range("2025-01-01", periods=12, freq="MS")
final = sm.OLS(np.log(serie), disenio(serie.index, True)).fit()

# intervalo de predicción al 80% en log, se regresa a camiones con exp
pr = final.get_prediction(disenio(futuro, True)).summary_frame(alpha=0.2)
resumen = np.exp(pr[["mean", "obs_ci_lower", "obs_ci_upper"]])
resumen.columns = ["pronostico", "limite_inferior_80", "limite_superior_80"]
print("\nPronóstico 2025 (regresión con COVID, intervalo al 80%)")
print(resumen.round(0).astype(int).to_string())
print(f"Total 2025: {resumen['pronostico'].sum():,.0f} | total 2024 real: {serie['2024'].sum():,.0f}")
print(f"Crecimiento mensual de la tendencia: {np.exp(final.params['tendencia']) - 1:.2%}")
resumen.round(0).astype(int).to_csv(CARPETA / "pronostico_2025.csv")

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(serie.index, serie / 1e6, color="black", label="Histórico")
ax.plot(futuro, resumen["pronostico"] / 1e6, color="#2c5f8a", label="Pronóstico 2025")
ax.fill_between(futuro, resumen["limite_inferior_80"] / 1e6,
                resumen["limite_superior_80"] / 1e6, color="#2c5f8a", alpha=0.25,
                label="Intervalo 80%")
ax.set_ylabel("Camiones al mes (millones)")
ax.set_title("Pronóstico de camiones totales, 2025")
ax.legend()
plt.tight_layout()
plt.savefig(CARPETA / "pronostico_2025.png", dpi=120)
plt.close()