# Planificación de Mesas de Examen Universitario

Sistema inteligente de asignación de turnos de examen sin solapamiento de alumnos, utilizando modelos de Machine Learning para estimar conflictos y algoritmos de coloración de grafos

---

## 1. Requisitos Previos

- **Python 3.10+**
- **Node.js 18+** y **npm** (para el frontend)

---

## 2. Instalación del Backend

Desde la raíz del proyecto:

```bash
cd backend
python3 -m venv .venv
```

Activar el entorno virtual:

- **Linux / macOS:**
  ```bash
  source .venv/bin/activate
  ```
- **Windows:**
  ```bash
  .venv\Scripts\activate
  ```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

---

## 3. Datos y Entrenamiento de Modelos

Los comandos deben ejecutarse dentro de la carpeta `backend/` con el entorno virtual activo:

### Regenerar Dataset Sintético (Opcional)
Genera el catálogo de 45 materias y las series temporales de pares de materias:
```bash
python data/generar_dataset.py
```

### Entrenar y Evaluar Modelos
Compara Regresión Lineal, Árbol de Decisión y KNN con validación cruzada temporal (`GroupKFold`), grafica sobreajuste y guarda el modelo ganador en `app/modelo.pkl`:
```bash
python entrenamiento.py
```

---

## 4. Ejecución de la API (Backend)

Con el entorno virtual activo en `backend/`:

```bash
uvicorn app.main:app --reload --port 8000
```

- **API Base:** `http://localhost:8000`
- **Documentación Interactiva (Swagger UI):** `http://localhost:8000/docs`

### Endpoints Principales

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/` | Health check y estado del servicio |
| `GET` | `/metricas` | Tabla comparativa de modelos (MAE, R²) y ganador |
| `GET` | `/cronograma?umbral=5.0` | Grafo de conflictos y asignación de materias por turno |

---

## 5. Ejecución del Frontend

- **Aplicación Web:** `http://localhost:5173`

---

## 6. Estructura del Repositorio

```text
├── backend/
│   ├── app/
│   │   ├── main.py                     # API FastAPI y endpoints
│   │   ├── modelo.pkl                  # Modelo KNN serializado
│   │   ├── grafo.py                    # Construcción del grafo con NetworkX
│   │   └── coloreo.py                  # Algoritmo de coloreo voraz
│   ├── data/
│   │   ├── generar_dataset.py          # Script generador sintético
│   │   ├── materias.csv                # Catálogo de 45 asignaturas
│   │   ├── pares_historico.csv         # Datos históricos para entrenamiento
│   │   └── pares_proximo_periodo.csv   # Pares del periodo a planificar
│   ├── entrenamiento.py                # EDA, entrenamiento y selección de modelo
│   └── requirements.txt                # Dependencias de Python
├── frontend/                           # Aplicación React + Vite + TypeScript
├── prompts_ia.md                       # Registro de prompts e interacción con IA
└── README.md                           # Guía de instalación y ejecución
```
