"""
Practica 1 - Limpieza de Datos
Dataset: Border Freight Crossings
"""

import pandas as pd
from pathlib import Path

# Carga dataset original
CARPETA = Path(__file__).parent
RUTA_ENTRADA = CARPETA / "Border_Freight_Crossings.csv"

# Salida del dataset limpio (formato ancho, sin redundancias, sin nulos)
RUTA_SALIDA = CARPETA / "dataset_limpio.csv"

df = pd.read_csv(RUTA_ENTRADA)

print(f"Filas originales: {len(df)}")
print(f"Columnas originales: {list(df.columns)}")

# Verificación inicial del dataset
# Se debe verificar explícitamente que no haya nulos ni duplicados en vez de asumirlo
assert df.isnull().sum().sum() == 0, "Se encontraron nulos inesperados"
assert df.duplicated().sum() == 0, "Se encontraron filas duplicadas exactas"

# Corrección de tipos de datos
# la fecha se convierte a datetime real para poder agrupar por mes/año
df["date"] = pd.to_datetime(df["date"])

# Identificación de puertos únicos por nombre y por código
n_puertos_por_nombre = df["port_name"].nunique()
n_puertos_por_codigo = df["port_code"].nunique()
print(f"Puertos únicos por nombre: {n_puertos_por_nombre}")
print(f"Puertos únicos por código: {n_puertos_por_codigo}")

# Eliminación de columnas redundantes
df = df.drop(columns=["point"])

# Valor en 0 en la columna 'value' (se documenta en el dataset original que un valor de 0 es un valor real, no un dato faltante)
ceros = (df["value"] == 0).sum()
print(f"Filas con value=0 (conservadas, evento real - cierre COVID): {ceros}")

# Pivoteo del dataset a formato ancho
df_ancho = df.pivot_table(
    index=["port_code", "port_name", "state", "border", "date",
           "latitude", "longitude"],
    columns="measure",
    values="value",
    aggfunc="sum",
).reset_index()

df_ancho.columns.name = None
df_ancho = df_ancho.rename(columns={"Trucks": "trucks", "Trains": "trains"})

# Nulos generados por el pivoteo
nulos_generados = df_ancho[["trucks", "trains"]].isnull().sum()
print(f"NaN generados por el pivoteo (antes de imputar):\n{nulos_generados}")

df_ancho["trucks"] = df_ancho["trucks"].fillna(0).astype(int)
df_ancho["trains"] = df_ancho["trains"].fillna(0).astype(int)

# Resultado final (dataset limpio)
print(f"\nFilas finales: {len(df_ancho)}")
print(f"Columnas finales: {list(df_ancho.columns)}")
print(f"Duplicados finales (port_code + date): "
      f"{df_ancho.duplicated(subset=['port_code','date']).sum()}")

df_ancho.to_csv(RUTA_SALIDA, index=False)
print(f"\nGuardado en: {RUTA_SALIDA}")