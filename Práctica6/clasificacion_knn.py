"""
Practica 6 - Clasificacion de Datos con KNN
Dataset: dataset_limpio.csv (práctica 1)
"""


# El objetivo de esta práctica es clasificar si un registro (puerto + mes) pertenece a 
# la frontera con Mexico o con Canada, usando solo el volumen de trucks y trains mediante KNN

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

from sklearn.model_selection import (
    train_test_split, StratifiedKFold, GroupKFold, GroupShuffleSplit,
    cross_val_score,
)
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, ConfusionMatrixDisplay,
)

CARPETA = Path(__file__).parent
RUTA_ENTRADA = CARPETA / "dataset_limpio.csv"
SEMILLA = 42  # número aleatorio para que los resultados sean reproducibles

df = pd.read_csv(RUTA_ENTRADA)

# Variable objetivo y baseline
# Se clasifica border con 1 = Mexico y 0 = Canada.
y = (df["border"] == "US-Mexico Border").astype(int)

print("")
print("VARIABLE OBJETIVO Y BASELINE")
print("=" * 60)
print(y.map({0: "Canada", 1: "Mexico"}).value_counts())
baseline = 1 - y.mean()
print(f"Baseline (predecir siempre 'Canada'): accuracy = {baseline:.3f}")

# Elección de variables predictoras
def evaluar(columnas, k=5, escalar=True):
    # Entrena KNN con un split 80/20 y regresa (accuracy, F1)
    X = df[columnas]
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=SEMILLA
    )
    modelo = (make_pipeline(StandardScaler(), KNeighborsClassifier(k))
              if escalar else KNeighborsClassifier(k))
    modelo.fit(X_tr, y_tr)
    pred = modelo.predict(X_te)
    return accuracy_score(y_te, pred), f1_score(y_te, pred)

print("\n")
print("COMPARACIÓN DE VARIABLES PREDICTORAS (k=5)")
print("=" * 60)
acc, f1 = evaluar(["trucks", "trains", "latitude", "longitude"])
print(f"trucks + trains + latitude + longitude da acc={acc:.3f}  F1={f1:.3f}")
print("Accuracy perfecto: es trivial, los puertos de México estan al sur.")
acc, f1 = evaluar(["trucks", "trains"])
print(f"trucks + trains: acc={acc:.3f}  F1={f1:.3f}")

# Escalado y transformación logarítmica
# KNN clasifica por distancia trucks llega a cientos de miles y trains
# a cientos, asi que trucks domina toda la distancia
print("\n")
print("ESCALADO Y LOG (k=5)")
print("=" * 60)
acc, f1 = evaluar(["trucks", "trains"], escalar=False)
print(f"Sin escalar           acc={acc:.3f}  F1={f1:.3f}")
acc, f1 = evaluar(["trucks", "trains"], escalar=True)
print(f"Con StandardScaler    acc={acc:.3f}  F1={f1:.3f}")

# Ambas variables estan muy sesgadas (práctica 2,con skew 4.91 y 3.28) 
# se prueba log1p antes de escalar
df["log_trucks"] = np.log1p(df["trucks"])
df["log_trains"] = np.log1p(df["trains"])
COLS = ["log_trucks", "log_trains"]
acc, f1 = evaluar(COLS, escalar=True)
print(f"log1p + Scaler     -> acc={acc:.3f}  F1={f1:.3f}")
print("Escalar mejora claramente. El log es casi igual con split aleatorio.")

# para decidir sobre el log se compara también con un split, pero ahora por puerto
# el test contiene puertos que el modelo nunca vio (sección 6)
def evaluar_por_puerto(columnas, k=5):
    X_ = df[columnas]
    i_tr, i_te = next(GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=SEMILLA)
                      .split(X_, y, groups=df["port_code"]))
    m = make_pipeline(StandardScaler(), KNeighborsClassifier(k))
    m.fit(X_.iloc[i_tr], y.iloc[i_tr])
    return accuracy_score(y.iloc[i_te], m.predict(X_.iloc[i_te]))

print(f"Split por puerto, sin log: acc={evaluar_por_puerto(['trucks', 'trains']):.3f}")
print(f"Split por puerto, con log: acc={evaluar_por_puerto(COLS):.3f}")
print("Con puertos nuevos el log si ayuda, por eso se conserva")

# Búsqueda de k
# se compara con validación cruzada de 5 folds
# se mide F1 de la clase Mexico, no accuracy (por el desbalance)
X = df[COLS]
ks = [1, 3, 5, 7, 9, 11, 15, 21, 31, 51]
f1_cv = []        # validación cruzada aleatoria
f1_cv_grupo = []  # validación cruzada por puerto
for k in ks:
    modelo = make_pipeline(StandardScaler(), KNeighborsClassifier(k))
    cv = StratifiedKFold(5, shuffle=True, random_state=SEMILLA)
    f1_cv.append(cross_val_score(modelo, X, y, cv=cv, scoring="f1").mean())
    f1_cv_grupo.append(cross_val_score(
        modelo, X, y, cv=GroupKFold(5), groups=df["port_code"], scoring="f1"
    ).mean())

print("\n")
print("BÚSQUEDA DE k (validación cruzada, F1 de Mexico)")
print("=" * 60)
for k, f, fg in zip(ks, f1_cv, f1_cv_grupo):
    print(f"k={k:2d}  F1 aleatoria = {f:.3f}  |  F1 por puerto = {fg:.3f}")

K_FINAL = 7
plt.figure(figsize=(8, 5))
plt.plot(ks, f1_cv, marker="o", color="#2c5f8a")
plt.axvline(K_FINAL, color="red", linestyle="--", label=f"k elegido = {K_FINAL}")
plt.xlabel("k (numero de vecinos)")
plt.ylabel("F1 (clase Mexico), validacion cruzada")
plt.title("Elección de k para KNN")
plt.legend()
plt.tight_layout()
plt.savefig(CARPETA / "knn_k_vs_f1.png", dpi=120)
plt.close()

# Evaluación del modelo final con un split 80/20
X_tr, X_te, y_tr, y_te = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=SEMILLA
)
modelo_final = make_pipeline(StandardScaler(), KNeighborsClassifier(K_FINAL))
modelo_final.fit(X_tr, y_tr)
pred = modelo_final.predict(X_te)

print("\n")
print(f"MODELO FINAL (k={K_FINAL}, log1p + escalado, split 80/20)")
print("=" * 60)
print(f"Accuracy : {accuracy_score(y_te, pred):.3f}   (baseline: {baseline:.3f})")
print(f"Precision: {precision_score(y_te, pred):.3f}")
print(f"Recall   : {recall_score(y_te, pred):.3f}")
print(f"F1       : {f1_score(y_te, pred):.3f}")
cm = confusion_matrix(y_te, pred)
print("Matriz de confusión (filas = real, columnas = predicho):")
print(cm)

ConfusionMatrixDisplay(cm, display_labels=["Canada", "Mexico"]).plot(cmap="Blues")
plt.title(f"Matriz de confusión - KNN (k={K_FINAL})")
plt.tight_layout()
plt.savefig(CARPETA / "knn_matriz_confusion.png", dpi=120)
plt.close()

# Prueba de estrés (por puerto)
print("\n")
print("PRUEBA DE ESTRÉS (puertos nuevos en el test)")
print("=" * 60)
gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=SEMILLA)
idx_tr, idx_te = next(gss.split(X, y, groups=df["port_code"]))
modelo_g = make_pipeline(StandardScaler(), KNeighborsClassifier(K_FINAL))
modelo_g.fit(X.iloc[idx_tr], y.iloc[idx_tr])
pred_g = modelo_g.predict(X.iloc[idx_te])
y_g = y.iloc[idx_te]
print(f"Baseline en este test: {1 - y_g.mean():.3f}")
print(f"Accuracy : {accuracy_score(y_g, pred_g):.3f}")
print(f"F1       : {f1_score(y_g, pred_g):.3f}")

f1_grupo = cross_val_score(
    make_pipeline(StandardScaler(), KNeighborsClassifier(K_FINAL)),
    X, y, cv=GroupKFold(5), groups=df["port_code"], scoring="f1",
).mean()
print(f"F1 promedio con validacion cruzada por puerto: {f1_grupo:.3f}\n")