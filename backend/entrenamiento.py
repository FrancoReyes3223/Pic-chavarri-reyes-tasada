import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score
from sklearn.model_selection import GridSearchCV, GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
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


# --- Selección de modelos con cross-validation (solo sobre train) ---
# El test NO se usa para elegir nada: queda guardado para la evaluación final.

cv = GroupKFold(n_splits=train['periodo'].nunique())
grupos = train['periodo']

# Para cada modelo, los hiperparámetros que vamos a probar.
# KNN usa distancias, así que escalamos las features 
busquedas = {
    'Regresion Lineal': (LinearRegression(), {}),
    'Arbol': (
        DecisionTreeRegressor(random_state=42),
        {'max_depth': list(range(1, 21))},
    ),
    'KNN': (
        make_pipeline(StandardScaler(), KNeighborsRegressor()),
        {'kneighborsregressor__n_neighbors': [3, 5, 10, 15, 20, 30, 50]},
    ),
}

print('\n--- Cross-validation sobre train (elige hiperparámetros y modelo) ---')
resultados = {}
for nombre, (modelo, grilla) in busquedas.items():
    busqueda = GridSearchCV(
        modelo, grilla, cv=cv,
        scoring='neg_mean_absolute_error',   # sklearn maximiza, por eso el MAE va negativo
        return_train_score=True,
    )
    busqueda.fit(X_train, y_train, groups=grupos)   # al final reentrena con todo el train
    resultados[nombre] = busqueda
    print(f'{nombre:<18} mejores parámetros: {busqueda.best_params_}  MAE CV = {-busqueda.best_score_:.3f}')

mejor_nombre = min(resultados, key=lambda n: -resultados[n].best_score_)
mejor_modelo = resultados[mejor_nombre].best_estimator_
print(f'\nMejor modelo según CV: {mejor_nombre}')


# --- Evaluación final en test (se usa una sola vez, con los modelos ya elegidos) ---
print('\n--- Evaluación en test (períodos 7-8) ---')
print(f'{"Modelo":<18} {"MAE CV":>8} {"MAE train":>10} {"MAE test":>10} {"RMSE test":>10} {"R2 test":>10}')
print('-' * 70)
for nombre, busqueda in resultados.items():
    modelo = busqueda.best_estimator_
    pred_test = modelo.predict(X_test)
    mae_train = mean_absolute_error(y_train, modelo.predict(X_train))
    mae_test = mean_absolute_error(y_test, pred_test)
    rmse_test = root_mean_squared_error(y_test, pred_test)
    r2_test = r2_score(y_test, pred_test)
    print(f'{nombre:<18} {-busqueda.best_score_:>8.3f} {mae_train:>10.3f} {mae_test:>10.3f} {rmse_test:>10.3f} {r2_test:>10.3f}')


# --- Análisis de overfitting del árbol ---
# Usamos los resultados de la cross-validation: error en train contra error en validación.

cv_arbol = resultados['Arbol'].cv_results_
profundidades = cv_arbol['param_max_depth'].tolist()
mae_train_por_prof = -cv_arbol['mean_train_score']
mae_val_por_prof = -cv_arbol['mean_test_score']   # en sklearn "test" acá es el fold de validación

plt.plot(profundidades, mae_train_por_prof, marker='o', label='Train')
plt.plot(profundidades, mae_val_por_prof, marker='o', label='Validación (CV)')
plt.title('Árbol de decisión: error según la profundidad')
plt.xlabel('max_depth')
plt.ylabel('MAE')
plt.legend()
plt.grid(True)
plt.savefig('app/overfitting_arbol.png')
plt.close()

print('\n--- Overfitting del árbol ---')
print(f'Profundidad con menor MAE en validación: {resultados["Arbol"].best_params_["max_depth"]}')
print(f'max_depth=20 -> MAE train {mae_train_por_prof[-1]:.3f}, MAE validación {mae_val_por_prof[-1]:.3f}')
print('Gráfico guardado en app/overfitting_arbol.png')


# --- Guardar el modelo ganador ---
# Guardamos el modelo junto con la lista de features, para que el backend
# le pase las columnas en el mismo orden con el que se entrenó.
joblib.dump(
    {'modelo': mejor_modelo, 'nombre': mejor_nombre, 'features': FEATURES},
    'app/modelo.pkl',
)
print(f'\nModelo guardado en app/modelo.pkl ({mejor_nombre})')