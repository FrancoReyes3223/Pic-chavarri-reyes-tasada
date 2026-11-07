# Planificación de Mesas de Examen Universitario

Sistema inteligente de asignación de turnos de examen sin solapamiento de alumnos, utilizando modelos de Machine Learning para estimar conflictos y algoritmos de coloración de grafos

---

## 1. Requisitos Previos

- **Python 3.10+**
- **Node.js 20+** y **npm** (para el frontend; la librería de rutas `react-router-dom` no funciona con Node 18)

---

## 2. Instalación del Backend

Desde la raíz del proyecto:

```bash
cd backend
```

Crear y activar el entorno virtual:

- **Linux / macOS:**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```
- **Windows** (en Windows el comando es `python`, no `python3`):
  ```bash
  python -m venv .venv
  .venv\Scripts\activate
  ```
  Si PowerShell no permite ejecutar el script de activación, se puede usar el entorno sin activarlo, anteponiendo `.venv\Scripts\python -m` a cada comando. Por ejemplo: `.venv\Scripts\python -m pip install -r requirements.txt`.

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

(Sin activar el entorno, en Windows: `.venv\Scripts\python -m uvicorn app.main:app --reload --port 8000`.)

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

En otra terminal (la API tiene que estar corriendo), desde la raíz del proyecto:

```bash
cd frontend
npm install
npm run dev
```

- **Aplicación Web:** `http://localhost:5173`

El frontend busca la API en `http://localhost:8000`. Si corre en otra dirección, se puede cambiar con la variable de entorno `VITE_API_URL` (por ejemplo, creando `frontend/.env` con `VITE_API_URL=http://localhost:9000`).

Si ya tenían el frontend instalado de antes, vuelvan a correr `npm install` después de bajar los cambios: se agregó la dependencia `react-router-dom`.

### Páginas de la aplicación

| Dirección | Qué muestra |
|---|---|
| `/` | Inicio: los tres pasos del sistema (predecir, armar el grafo, colorear) |
| `/grafo` | Slider de umbral, resumen y grafo de conflictos coloreado por turno, con la leyenda de colores |
| `/cronograma` | Slider de umbral, resumen y grilla con las materias de cada turno |
| `/modelo` | Qué predice el modelo, cómo se evaluó y la tabla comparativa de modelos |

El umbral es uno solo para toda la aplicación: el slider de `/grafo` y el de `/cronograma` muestran y cambian el mismo valor (al recargar la página vuelve a 5).

El grafo se puede ver de tres formas, con las pestañas de `/grafo`:

| Dirección | Vista | Qué muestra |
|---|---|---|
| `/grafo` | Por cercanía | Grupos de conflictos: las materias se acomodan con una simulación de fuerzas. Se pueden arrastrar nodos y hacer zoom con la rueda |
| `/grafo/grilla` | Por carrera y año | Por qué hay conflictos: una fila por carrera y una columna por año, con posiciones fijas |
| `/grafo/turnos` | Por turno | El resultado del coloreo: una columna por turno, y ninguna arista une dos materias de la misma columna |

En las vistas por carrera y año y por turno, al pasar el mouse por una materia se resaltan sus conflictos.

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
│   └── src/
│       ├── App.tsx                     # Rutas, barra de navegación y datos compartidos (umbral)
│       ├── api.ts                      # Tipos del JSON y llamadas a la API
│       ├── colores.ts                  # Color de cada turno
│       ├── index.css                   # Estilos y colores (modo claro y oscuro)
│       ├── paginas/                    # Una página por dirección: Inicio, Grafo, Cronograma, Modelo
│       └── componentes/                # Slider, grafos (fuerzas, grilla, por turno), leyenda, cronograma, métricas
├── prompts_ia.md                       # Registro de prompts e interacción con IA
└── README.md                           # Guía de instalación y ejecución
```
