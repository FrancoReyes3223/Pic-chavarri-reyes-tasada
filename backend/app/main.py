"""
API FastAPI - Planificacion de Mesas de Examen
Rol B: Integracion de API, endpoints y desacople con frontend.

Endpoints expuestos:
- GET /            -> Health check / estado del servicio
- GET /metricas    -> Metricas de evaluacion y comparacion de modelos ML
- GET /cronograma  -> Grafo de conflictos y cronograma de turnos segun umbral

Para ejecutar el servidor localmente:
    cd backend
    uvicorn app.main:app --reload --port 8000

Documentacion interactiva Swagger disponible en:
    http://localhost:8000/docs
"""

import csv
from functools import lru_cache
from pathlib import Path
from typing import List, Dict, Any
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


# Configuracion y rutas de archivos

# Bandera para alternar entre datos simulados (mock) y logica real de grafos
MODO_MOCK: bool = False

BASE_DIR = Path(__file__).resolve().parent.parent
RUTA_MATERIAS = BASE_DIR / "data" / "materias.csv"
RUTA_PARES_PROXIMO = BASE_DIR / "data" / "pares_proximo_periodo.csv"


# Inicializacion de la app y CORS

app = FastAPI(
    title="API de Planificacion de Mesas de Examen",
    description="Sistema inteligente para la organizacion de turnos de examen mediante ML y Teoria de Grafos.",
    version="1.0.0",
)

# Configuracion de CORS para permitir peticiones desde el frontend (Vite/React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "*"  # Permite desarrollo local y pruebas desde cualquier origen
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Modelos Pydantic (esquemas de respuesta)

class HealthResponse(BaseModel):
    estado: str
    mensaje: str
    version: str
    modo_mock: bool


class MetricaModelo(BaseModel):
    modelo: str
    hiperparametro: str
    mae_cv: float
    mae_test: float
    r2_test: float
    es_ganador: bool


class MetricasResponse(BaseModel):
    modelos: List[MetricaModelo]
    modelo_seleccionado: str
    criterio_seleccion: str
    descripcion: str


class MateriaDetalle(BaseModel):
    id: str
    nombre: str
    carrera: str
    anio: int


class TurnoItem(BaseModel):
    turno: int
    materias: List[MateriaDetalle]


class NodoGrafo(BaseModel):
    id: str
    label: str
    carrera: str
    anio: int
    turno: int


class AristaGrafo(BaseModel):
    origen: str
    destino: str
    peso: float


class GrafoData(BaseModel):
    nodos: List[NodoGrafo]
    aristas: List[AristaGrafo]


class CronogramaResponse(BaseModel):
    umbral: float = Field(..., description="Umbral de corte aplicado")
    total_materias: int = Field(..., description="Cantidad total de materias a planificar")
    total_turnos: int = Field(..., description="Numero cromatico / cantidad de turnos requeridos")
    total_conflictos: int = Field(..., description="Cantidad de aristas en el grafo de conflicto")
    turnos: List[TurnoItem] = Field(..., description="Distribucion de materias agrupadas por turno")
    grafo: GrafoData = Field(..., description="Estructura de nodos y aristas para renderizado")


# Armado de la respuesta (lo usan tanto el mock como el flujo real)

def armar_cronograma(
    umbral: float,
    materias: List[Dict[str, Any]],
    aristas: List[Dict[str, Any]],
    asignacion_turnos: Dict[str, int],
) -> CronogramaResponse:
    """Arma la respuesta de /cronograma a partir de las materias, las aristas y el turno de cada materia."""
    total_turnos = max(asignacion_turnos.values()) if asignacion_turnos else 1

    # Estructurar turnos para el response
    turnos_dict: Dict[int, List[MateriaDetalle]] = {}
    for t in range(1, total_turnos + 1):
        turnos_dict[t] = []

    nodos_grafo: List[NodoGrafo] = []

    for m in materias:
        nid = m["id"]
        t = asignacion_turnos[nid]
        detalle = MateriaDetalle(id=nid, nombre=m["nombre"], carrera=m["carrera"], anio=m["anio"])
        turnos_dict[t].append(detalle)
        nodos_grafo.append(NodoGrafo(
            id=nid,
            label=m["nombre"],
            carrera=m["carrera"],
            anio=m["anio"],
            turno=t
        ))

    lista_turnos = []
    for t in sorted(turnos_dict.keys()):
        lista_turnos.append(TurnoItem(turno=t, materias=turnos_dict[t]))

    aristas_grafo = []
    for a in aristas:
        aristas_grafo.append(AristaGrafo(origen=a["origen"], destino=a["destino"], peso=a["peso"]))

    return CronogramaResponse(
        umbral=umbral,
        total_materias=len(materias),
        total_turnos=total_turnos,
        total_conflictos=len(aristas_grafo),
        turnos=lista_turnos,
        grafo=GrafoData(nodos=nodos_grafo, aristas=aristas_grafo)
    )


# Funciones auxiliares para datos mock

def cargar_materias_csv() -> List[Dict[str, Any]]:
    """Carga la lista completa de las 45 materias desde el archivo CSV."""
    if not RUTA_MATERIAS.exists():
        raise FileNotFoundError(f"No se encontro el archivo de materias en {RUTA_MATERIAS}")

    materias = []
    with open(RUTA_MATERIAS, mode="r", encoding="utf-8") as f:
        lector = csv.DictReader(f)
        for fila in lector:
            materias.append({
                "id": fila["materia_id"],
                "nombre": fila["nombre"],
                "carrera": fila["carrera"],
                "anio": int(fila["anio"]),
            })
    return materias


def generar_cronograma_mock(umbral: float) -> CronogramaResponse:
    """
    Genera un cronograma y grafo de prueba basado en materias reales y pares historicos.
    Aplica una asignacion voraz (greedy) simple para garantizar que dos materias con conflicto
    no compartan el mismo turno.
    """
    materias = cargar_materias_csv()

    aristas = []
    adyacencias: Dict[str, set] = {}
    for m in materias:
        adyacencias[m["id"]] = set()

    # Si existe el archivo de pares del periodo proximo, usamos los historicos como peso representativo
    if RUTA_PARES_PROXIMO.exists():
        with open(RUTA_PARES_PROXIMO, mode="r", encoding="utf-8") as f:
            lector = csv.DictReader(f)
            for fila in lector:
                peso = float(fila["cant_estudiantes_compartidos_historico"])
                if peso >= umbral:
                    m1 = fila["materia_id_1"]
                    m2 = fila["materia_id_2"]
                    aristas.append({
                        "origen": m1,
                        "destino": m2,
                        "peso": round(peso, 1)
                    })
                    adyacencias[m1].add(m2)
                    adyacencias[m2].add(m1)
    else:
        # Fallback de seguridad en caso de que no este el CSV de pares
        for i in range(len(materias)):
            for j in range(i + 1, len(materias)):
                m1, m2 = materias[i], materias[j]
                if m1["carrera"] == m2["carrera"] and m1["anio"] == m2["anio"]:
                    peso_estimado = 25.0
                    if peso_estimado >= umbral:
                        aristas.append({"origen": m1["id"], "destino": m2["id"], "peso": peso_estimado})
                        adyacencias[m1["id"]].add(m2["id"])
                        adyacencias[m2["id"]].add(m1["id"])

    # Algoritmo de coloreo Greedy basico para el mock
    # Ordenamos nodos por grado descendente (heuristica de Welch-Powell)
    nodos_ordenados = sorted(materias, key=lambda m: len(adyacencias[m["id"]]), reverse=True)
    asignacion_turnos: Dict[str, int] = {}

    for nodo in nodos_ordenados:
        nid = nodo["id"]
        # Buscar turnos usados por los vecinos
        turnos_vecinos = set()
        for vecino in adyacencias[nid]:
            if vecino in asignacion_turnos:
                turnos_vecinos.add(asignacion_turnos[vecino])

        # Asignar el menor turno disponible (empezando en 1)
        turno_candidato = 1
        while turno_candidato in turnos_vecinos:
            turno_candidato += 1
        asignacion_turnos[nid] = turno_candidato

    return armar_cronograma(umbral, materias, aristas, asignacion_turnos)


# Conexion con los modulos reales de grafos

@lru_cache(maxsize=1)
def cargar_predicciones():
    """Carga las materias y predice los afectados una sola vez: al mover el slider solo cambia el umbral."""
    from app.grafo import cargar_materias, predecir_afectados_por_par

    return cargar_materias(), predecir_afectados_por_par()


def generar_cronograma_real(umbral: float) -> CronogramaResponse:
    """Arma el cronograma con las predicciones del modelo, grafo.py y coloreo.py."""
    from app.coloreo import colorear_grafo
    from app.grafo import construir_grafo

    materias_df, afectados_por_par = cargar_predicciones()
    grafo_conflictos = construir_grafo(materias_df, afectados_por_par, umbral)

    # colorear_grafo devuelve {materia_id: turno} con turnos desde 0; la API los muestra desde 1.
    turno_por_materia = colorear_grafo(grafo_conflictos)
    asignacion_turnos = {}
    for materia_id, turno in turno_por_materia.items():
        asignacion_turnos[materia_id] = turno + 1

    materias = []
    for materia_id, datos in grafo_conflictos.nodes(data=True):
        materias.append({
            "id": materia_id,
            "nombre": datos["nombre"],
            "carrera": datos["carrera"],
            "anio": int(datos["anio"]),
        })

    aristas = []
    for origen, destino, datos in grafo_conflictos.edges(data=True):
        aristas.append({"origen": origen, "destino": destino, "peso": round(datos["weight"], 1)})

    return armar_cronograma(umbral, materias, aristas, asignacion_turnos)


# Endpoints

@app.get("/", response_model=HealthResponse, tags=["Sistema"])
def health_check():
    """Verifica que el servicio este operativo y expone el modo actual de ejecucion."""
    return HealthResponse(
        estado="ok",
        mensaje="API de Planificacion de Examenes operativa",
        version="1.0.0",
        modo_mock=MODO_MOCK
    )


@app.get("/metricas", response_model=MetricasResponse, tags=["Machine Learning"])
def obtener_metricas():
    """
    Retorna la comparativa oficial de modelos de regresion evaluados en el proyecto.
    Permite al frontend mostrar la justificacion teorica y empirica del modelo ganador.
    """
    modelos = [
        MetricaModelo(
            modelo="Regresion Lineal",
            hiperparametro="N/A",
            mae_cv=1.042,
            mae_test=1.069,
            r2_test=0.876,
            es_ganador=False
        ),
        MetricaModelo(
            modelo="Arbol de Decision",
            hiperparametro="max_depth=5",
            mae_cv=0.989,
            mae_test=1.038,
            r2_test=0.869,
            es_ganador=False
        ),
        MetricaModelo(
            modelo="KNN Regressor",
            hiperparametro="k=15 (con StandardScaler)",
            mae_cv=0.946,
            mae_test=1.021,
            r2_test=0.886,
            es_ganador=True
        )
    ]

    return MetricasResponse(
        modelos=modelos,
        modelo_seleccionado="KNN Regressor (k=15)",
        criterio_seleccion="Menor MAE en validacion cruzada y mejor generalizacion en conjunto de test sin sobreajuste.",
        descripcion="El modelo predice la cantidad de estudiantes simultaneos para cada par de asignaturas."
    )


@app.get("/cronograma", response_model=CronogramaResponse, tags=["Cronograma y Grafos"])
def obtener_cronograma(
    umbral: float = Query(
        5.0,
        gt=0.0,
        description="Cantidad minima de estudiantes afectados predichos para generar una arista de conflicto"
    )
):
    """
    Construye el grafo de conflictos segun el umbral y devuelve la distribucion de turnos de examen.
    - Si MODO_MOCK=True: utiliza datos simulados pero basados en materias reales y logica greedy.
    - Si MODO_MOCK=False: conecta con los modulos reales grafo.py y coloreo.py.
    """
    if MODO_MOCK:
        return generar_cronograma_mock(umbral=umbral)

    # Conexion real (para cuando el Integrante A complete coloreo.py)
    try:
        return generar_cronograma_real(umbral)
    except ImportError as e:
        raise HTTPException(
            status_code=501,
            detail=f"Los modulos reales aun no estan listos ({e}). Cambie MODO_MOCK = True en app/main.py."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error durante el procesamiento del grafo real: {str(e)}"
        )
