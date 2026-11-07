# TP Integrador — Planificación de mesas de examen

Trabajo práctico final de "Lógica y Teoría de Grafos", hecho en grupo de **3 personas** (excepción del curso: el enunciado pide grupos de 2). **Fecha de entrega: 08/11/2026.**
El enunciado completo está en `enunciado.pdf`; nuestro TP es "Planificación de mesas de examen" (páginas 11 y 12).
Lo que se vio en clase de Machine Learning está en https://github.com/AgustinGurvich/Intro-A-ML.

## Pipeline

pares de materias → **modelo de regresión** predice estudiantes afectados → **grafo de conflictos** (arista si la predicción ≥ umbral, peso = predicción) → **coloreo greedy** (color = turno) → **API** → **frontend**

## Decisiones ya tomadas (no volver a discutirlas)

- **Regresión** sobre `cant_estudiantes_afectados`. No hacemos clasificación: se sacó a propósito.
- **Dataset sintético** generado por `backend/data/generar_dataset.py`. Sus reglas (R1 a R6) están en el docstring del script.
- Evaluación con **partición temporal**: entrenar con los primeros períodos y testear con los últimos.
- El **umbral de conflicto** se aplica en el backend al armar el grafo, no en el dataset. Es el slider del frontend.
- El coloreo greedy **lo implementamos nosotros**. `nx.greedy_color` solo se usa para validar el resultado.
- Modelos permitidos por el enunciado: regresión lineal, regresión logística, KNN, SVM y árboles de decisión.
- El análisis de over/underfitting va en el script de entrenamiento (`backend/entrenamiento.py`), no en el generador.
- Usamos **scripts `.py`, no notebooks de Jupyter**.
- **El test no se usa para elegir nada.** Los hiperparámetros y el modelo ganador se eligen con `GridSearchCV` sobre train, con `GroupKFold` por período (cada fold deja afuera un período entero). El test (períodos 7 y 8) se mira una sola vez, al final.
- **KNN va con `StandardScaler`** dentro de un pipeline, porque usa distancias. La regresión lineal y el árbol van sin escalar.

## Resultados actuales del modelo (seed 42)

| Modelo | Hiperparámetro elegido | MAE CV | MAE test | R² test |
|---|---|---|---|---|
| Regresión lineal | — | 1.042 | 1.069 | 0.876 |
| Árbol | `max_depth=5` | 0.989 | 1.038 | 0.869 |
| **KNN (ganador)** | `k=15` | **0.946** | **1.021** | **0.886** |

Árbol con `max_depth=20`: MAE train 0.076 contra MAE validación 1.225, un overfitting claro. El gráfico está en `app/overfitting_arbol.png`.

`app/modelo.pkl` es un dict `{'modelo', 'nombre', 'features'}`. `modelo` es un **Pipeline** (scaler + KNN): se usa directo con `modelo.predict(df[features])`, que escala solo. Las columnas tienen que ir en el orden de `features`.

## Estructura

```
backend/
  data/generar_dataset.py         genera los 3 CSV de abajo
  data/materias.csv               45 materias (3 carreras × 5 años × 3 materias) = nodos
  data/pares_historico.csv        990 pares × 8 períodos = 7920 filas (entrenamiento)
  data/pares_proximo_periodo.csv  features del período a planificar, sin target
  entrenamiento.py                EDA, CV, evaluación en test, gráfico de overfitting y guardado del modelo
  requirements.txt                numpy, pandas, scikit-learn, networkx, fastapi, uvicorn, matplotlib
  app/modelo.pkl                  modelo ganador (lo genera entrenamiento.py)
  app/histograma_target.png       gráfico para el informe
  app/overfitting_arbol.png       gráfico para el informe
  app/main.py                     API FastAPI (/metricas, /cronograma) con CORS y mock
  app/grafo.py                    predice el próximo período y arma el grafo según el umbral
  app/coloreo.py                  coloreo greedy (`colorear_grafo`) y su verificación
frontend/                         (pendiente) React + TypeScript (Vite)
prompts_ia.md                     registro de prompts para la sección "Uso de IA" del informe
```

Los scripts usan rutas relativas (`data/...`, `app/...`), así que **hay que correrlos parados en `backend/`**.

## Estado y próximos pasos

- [x] Dataset sintético
- [x] Entrenamiento y selección de modelo
- [x] `app/grafo.py`: predecir sobre `pares_proximo_periodo.csv` y armar el grafo con networkx (arista si la predicción ≥ umbral, `weight` = predicción)
- [x] `app/coloreo.py`: greedy implementado a mano, ordenando las materias por grado ponderado; validar contra `nx.greedy_color`
- [x] `app/main.py`: API FastAPI (`/metricas`, `/cronograma?umbral=`) con CORS y modo mock desacoplado
- [ ] `frontend/`: grafo coloreado, grilla de cronograma y slider de umbral
- [x] `README.md`: guía de instalación y ejecución completa
- [ ] Informe y capturas

## Formato de la API (acordado por el grupo)

`GET /cronograma?umbral=5` responde con estos campos y nombres. Si hay que cambiarlos, avisar al grupo: backend y frontend dependen de ellos.

```json
{
  "umbral": 5,
  "cant_turnos": 9,
  "nodos": [
    {"id": "M01", "nombre": "Análisis Matemático I", "carrera": "Sistemas", "anio": 1, "turno": 0}
  ],
  "aristas": [
    {"source": "M01", "target": "M02", "peso": 23.4}
  ],
  "cronograma": {
    "0": ["M01", "M07"],
    "1": ["M02"]
  }
}
```

`coloreo.py` tiene que exponer `colorear_grafo(grafo_conflictos)` y devolver un diccionario `{materia_id: turno}` con turnos desde 0. `main.py` arma la respuesta a partir de él y del grafo, y muestra los turnos desde 1. `MODO_MOCK` ya está en `False`.

**Pendiente de resolver:** la respuesta actual de `main.py` no usa exactamente estos nombres (ver `CronogramaResponse`: `total_turnos`, `turnos`, `grafo.nodos`, `origen`/`destino`, `label`).

## Features y target

- Features: `cant_estudiantes_compartidos_historico`, `mismo_anio`, `misma_carrera`, `diferencia_anios`, `anio_min`, `inscriptos_prom_1`, `inscriptos_prom_2`.
- Target: `cant_estudiantes_afectados`.
- `periodo`, `materia_id_1` y `materia_id_2` **no son features**.

## Cómo correr

Entorno virtual en `backend/.venv`:

- **Linux / Git Bash:** `source .venv/bin/activate`
- **Windows:** `.venv\Scripts\activate`

Una vez activo el entorno (parado en `backend/`):
- **Para correr el entrenamiento:** `python entrenamiento.py`
- **Para levantar la API (FastAPI):** `uvicorn app.main:app --reload --port 8000` (documentación Swagger interactiva en `http://localhost:8000/docs`)

Si se corre desde Git Bash, usar `PYTHONIOENCODING=utf-8 .venv/Scripts/python ...`, porque la salida tiene acentos.

## Convenciones

- Código, variables y comentarios en **español**, sin tildes en los identificadores.
- Código simple y explicable: en la defensa oral nos pueden preguntar cualquier línea.
- **No usar comprensiones** de listas, conjuntos o diccionarios ni expresiones generadoras (`all(x for ...)`, `max(x for ...)`): no las vimos en clase. Usar bucles `for` comunes.
- **No hacer commits** salvo que se pida. El repo tiene que mostrar commits incrementales de los tres integrantes.
- Después de cada pedido relevante, registrar el prompt con la skill `registrar-prompt`. **Siempre que se toque `prompts_ia.md`, avisarlo con el bloque grande "⚠️ SE ACTUALIZÓ prompts_ia.md"** definido en esa skill, para que el grupo lo revise.
