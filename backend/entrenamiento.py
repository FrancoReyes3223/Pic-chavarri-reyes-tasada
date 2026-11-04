import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score
import joblib
from pathlib import Path

#cargamos el dataset historico
df = pd.read_csv('data/pares_historico.csv')
print(f'Dataset cargado: {df.shape[0]} filas, {df.shape[1]} columnas')


# --- EDA ---
FEATURES = [
    'cant_estudiantes_compartidos_historico',
    'mismo_anio', 'misma_carrera',
    'diferencia_anios', 'anio_min',
    'inscriptos_prom_1', 'inscriptos_prom_2',
]
TARGET = 'cant_estudiantes_afectados'
print('\n--- Distribución del target ---')
print(df[TARGET].describe().round(2))
print(f'Pares con 0 afectados: {(df[TARGET] == 0).mean():.1%}')
print('\n--- Correlación de features con el target ---')
corr = df[FEATURES + [TARGET]].corr()[TARGET].drop(TARGET)
print(corr.round(3).to_string())
# Guardar histograma (para el informe)
df[TARGET].hist(bins=30)
plt.title('Distribución de estudiantes afectados')
plt.xlabel('cant_estudiantes_afectados')
plt.savefig('app/histograma_target.png')
plt.close()
print('\nHistograma guardado en app/histograma_target.png')

# --- Partición temporal ---
train = df[df['periodo'] <= 6]
test  = df[df['periodo'] > 6]

X_train, y_train = train[FEATURES], train[TARGET]
X_test,  y_test  = test[FEATURES],  test[TARGET]

print(f'\nTrain: {len(train)} filas (períodos 1-6)')
print(f'Test:  {len(test)} filas (períodos 7-8)')


# --- Entrenamiento y comparación ---
modelos = {
    'Regresion Lineal':    LinearRegression(),
    'Arbol (max_depth=5)': DecisionTreeRegressor(max_depth=5, random_state=42),
    'KNN (k=10)':          KNeighborsRegressor(n_neighbors=10),
}

print('\n--- Comparación de modelos ---')
print(f'{"Modelo":<25} {"MAE train":>10} {"MAE test":>10} {"RMSE test":>10} {"R2 test":>10}')
print('-' * 70)

mejor_mae = float('inf')
mejor_modelo = None
mejor_nombre = ''

for nombre, modelo in modelos.items():
    modelo.fit(X_train, y_train)
    pred_train = modelo.predict(X_train)
    pred_test  = modelo.predict(X_test)

    mae_train = mean_absolute_error(y_train, pred_train)
    mae_test  = mean_absolute_error(y_test,  pred_test)
    rmse_test = root_mean_squared_error(y_test, pred_test)
    r2_test   = r2_score(y_test, pred_test)

    print(f'{nombre:<25} {mae_train:>10.3f} {mae_test:>10.3f} {rmse_test:>10.3f} {r2_test:>10.3f}')

    if mae_test < mejor_mae:
        mejor_mae = mae_test
        mejor_modelo = modelo
        mejor_nombre = nombre

print(f'\nMejor modelo: {mejor_nombre} (MAE test = {mejor_mae:.3f})')


# --- Análisis de overfitting ---
# Entrenamos el árbol con distintas profundidades y comparamos el error en train y en test.
# Si el árbol es muy chico, se equivoca en los dos (underfitting).
# Si es muy profundo, memoriza el train: el error en train baja pero en test sube (overfitting).
profundidades = range(1, 21)
mae_train_por_prof = []
mae_test_por_prof = []

for prof in profundidades:
    arbol = DecisionTreeRegressor(max_depth=prof, random_state=42)
    arbol.fit(X_train, y_train)
    mae_train_por_prof.append(mean_absolute_error(y_train, arbol.predict(X_train)))
    mae_test_por_prof.append(mean_absolute_error(y_test, arbol.predict(X_test)))

plt.plot(profundidades, mae_train_por_prof, marker='o', label='Train')
plt.plot(profundidades, mae_test_por_prof, marker='o', label='Test')
plt.title('Árbol de decisión: error según la profundidad')
plt.xlabel('max_depth')
plt.ylabel('MAE')
plt.legend()
plt.grid(True)
plt.savefig('app/overfitting_arbol.png')
plt.close()

mejor_prof = profundidades[mae_test_por_prof.index(min(mae_test_por_prof))]
print('\n--- Overfitting del árbol ---')
print(f'Profundidad con menor MAE en test: {mejor_prof}')
print(f'max_depth=20 -> MAE train {mae_train_por_prof[-1]:.3f}, MAE test {mae_test_por_prof[-1]:.3f}')
print('Gráfico guardado en app/overfitting_arbol.png')


# --- Guardar el modelo ganador ---
# Guardamos el modelo junto con la lista de features, para que el backend
# le pase las columnas en el mismo orden con el que se entrenó.
joblib.dump(
    {'modelo': mejor_modelo, 'nombre': mejor_nombre, 'features': FEATURES},
    'app/modelo.pkl',
)
print(f'\nModelo guardado en app/modelo.pkl ({mejor_nombre})')