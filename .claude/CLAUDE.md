# TP Integrador — Planificación de mesas de examen

Trabajo práctico final de "Lógica y Teoría de Grafos", hecho en grupo de 2 personas. **Fecha de entrega: 08/11/2026.**
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
- El análisis de over/underfitting va en el notebook de entrenamiento, no en el generador.

## Estructura

```
backend/
  data/generar_dataset.py         genera los 3 CSV de abajo
  data/materias.csv               45 materias (3 carreras × 5 años × 3 materias) = nodos
  data/pares_historico.csv        990 pares × 8 períodos = 7920 filas (entrenamiento)
  data/pares_proximo_periodo.csv  features del período a planificar, sin target
  requirements.txt
  notebooks/                      (pendiente) entrenamiento.ipynb
  app/                            (pendiente) modelo.py, grafo.py, coloreo.py, main.py (FastAPI)
frontend/                         (pendiente) React + TypeScript (Vite)
prompts_ia.md                     registro de prompts para la sección "Uso de IA" del informe
```

## Features y target

- Features: `cant_estudiantes_compartidos_historico`, `mismo_anio`, `misma_carrera`, `diferencia_anios`, `anio_min`, `inscriptos_prom_1`, `inscriptos_prom_2`.
- Target: `cant_estudiantes_afectados`.
- `periodo`, `materia_id_1` y `materia_id_2` **no son features**.

## Cómo correr

Entorno de desarrollo: Windows, Python 3.13 y un entorno virtual en `backend/.venv`.

```
cd backend
.venv\Scripts\activate
python data/generar_dataset.py
```

Si se corre desde Git Bash, usar `PYTHONIOENCODING=utf-8 .venv/Scripts/python ...`, porque la salida tiene acentos.

## Convenciones

- Código, variables y comentarios en **español**, sin tildes en los identificadores.
- Código simple y explicable: en la defensa oral nos pueden preguntar cualquier línea.
- **No hacer commits** salvo que se pida. El repo tiene que mostrar commits incrementales de los dos integrantes.
- Después de cada pedido relevante, registrar el prompt con la skill `registrar-prompt`. **Siempre que se toque `prompts_ia.md`, avisarlo con el bloque grande "⚠️ SE ACTUALIZÓ prompts_ia.md"** definido en esa skill, para que el grupo lo revise.
