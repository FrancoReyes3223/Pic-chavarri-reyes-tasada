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

from functools import lru_cache
from typing import Dict, List

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.coloreo import colorear_grafo
from app.grafo import cargar_materias, construir_grafo, predecir_afectados_por_par


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
    modo_mock: bool  # siempre False: se mantiene porque el frontend lo muestra


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


# Armado del cronograma: predicciones -> grafo -> coloreo -> respuesta

@lru_cache(maxsize=1)
def cargar_predicciones():
    """Carga las materias y predice los afectados una sola vez: al mover el slider solo cambia el umbral."""
    return cargar_materias(), predecir_afectados_por_par()


def turnos_desde_uno(turno_por_materia: Dict[str, int]) -> Dict[str, int]:
    """colorear_grafo numera los turnos desde 0; la API los muestra desde 1."""
    turnos = {}
    for materia_id, turno in turno_por_materia.items():
        turnos[materia_id] = turno + 1
    return turnos


def armar_turnos(grafo_conflictos, turno_por_materia: Dict[str, int], total_turnos: int) -> List[TurnoItem]:
    """Agrupa las materias por turno, del turno 1 al último."""
    materias_por_turno: Dict[int, List[MateriaDetalle]] = {}
    for turno in range(1, total_turnos + 1):
        materias_por_turno[turno] = []

    for materia_id, datos in grafo_conflictos.nodes(data=True):
        materias_por_turno[turno_por_materia[materia_id]].append(MateriaDetalle(
            id=materia_id,
            nombre=datos["nombre"],
            carrera=datos["carrera"],
            anio=int(datos["anio"]),
        ))

    turnos = []
    for turno in sorted(materias_por_turno.keys()):
        turnos.append(TurnoItem(turno=turno, materias=materias_por_turno[turno]))
    return turnos


def armar_nodos(grafo_conflictos, turno_por_materia: Dict[str, int]) -> List[NodoGrafo]:
    """Un nodo por materia, con el turno que le tocó, para que el frontend lo dibuje."""
    nodos = []
    for materia_id, datos in grafo_conflictos.nodes(data=True):
        nodos.append(NodoGrafo(
            id=materia_id,
            label=datos["nombre"],
            carrera=datos["carrera"],
            anio=int(datos["anio"]),
            turno=turno_por_materia[materia_id],
        ))
    return nodos


def armar_aristas(grafo_conflictos) -> List[AristaGrafo]:
    """Una arista por par en conflicto, con los afectados predichos redondeados a un decimal."""
    aristas = []
    for origen, destino, datos in grafo_conflictos.edges(data=True):
        aristas.append(AristaGrafo(origen=origen, destino=destino, peso=round(datos["weight"], 1)))
    return aristas


def generar_cronograma(umbral: float) -> CronogramaResponse:
    """Arma el grafo con el umbral pedido, lo colorea y devuelve la respuesta de /cronograma."""
    materias, afectados_por_par = cargar_predicciones()
    grafo_conflictos = construir_grafo(materias, afectados_por_par, umbral)
    turno_por_materia = turnos_desde_uno(colorear_grafo(grafo_conflictos))

    total_turnos = max(turno_por_materia.values()) if turno_por_materia else 1
    aristas = armar_aristas(grafo_conflictos)

    return CronogramaResponse(
        umbral=umbral,
        total_materias=grafo_conflictos.number_of_nodes(),
        total_turnos=total_turnos,
        total_conflictos=len(aristas),
        turnos=armar_turnos(grafo_conflictos, turno_por_materia, total_turnos),
        grafo=GrafoData(nodos=armar_nodos(grafo_conflictos, turno_por_materia), aristas=aristas),
    )


# Endpoints

@app.get("/", response_model=HealthResponse, tags=["Sistema"])
def health_check():
    """Verifica que el servicio este operativo."""
    return HealthResponse(
        estado="ok",
        mensaje="API de Planificacion de Examenes operativa",
        version="1.0.0",
        modo_mock=False
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
    """Construye el grafo de conflictos segun el umbral y devuelve la distribucion de turnos de examen."""
    try:
        return generar_cronograma(umbral)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error durante el procesamiento del grafo: {str(e)}"
        )
