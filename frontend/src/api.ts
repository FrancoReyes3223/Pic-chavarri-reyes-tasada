// Comunicación con el backend (FastAPI).
// Todo lo que el frontend le pide a la API pasa por este archivo.

// Dirección de la API. Se puede cambiar con la variable de entorno VITE_API_URL;
// si no está definida, usamos la dirección local donde corre uvicorn.
export const URL_API = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

// ---------------------------------------------------------------------------
// Tipos: describen la forma del JSON que devuelve cada endpoint.
// Son copia de los modelos Pydantic de backend/app/main.py. Si cambia uno, hay
// que cambiar el otro.
// ---------------------------------------------------------------------------

// GET /
export interface EstadoApi {
  estado: string
  mensaje: string
  version: string
  modo_mock: boolean // true: datos de prueba; false: predicciones del modelo
}

// Una materia dentro de un turno del cronograma.
export interface Materia {
  id: string // por ejemplo "M01"
  nombre: string
  carrera: string
  anio: number
}

// Un turno de examen con las materias que se rinden en él.
export interface Turno {
  turno: number // empieza en 1
  materias: Materia[]
}

// Un nodo del grafo de conflictos: una materia con el turno (color) asignado.
export interface Nodo {
  id: string
  label: string // nombre de la materia
  carrera: string
  anio: number
  turno: number
}

// Una arista del grafo: dos materias en conflicto.
export interface Arista {
  origen: string // id de una materia
  destino: string // id de la otra materia
  peso: number // estudiantes afectados que predice el modelo
}

// GET /cronograma?umbral=X
export interface Cronograma {
  umbral: number
  total_materias: number
  total_turnos: number
  total_conflictos: number // cantidad de aristas
  turnos: Turno[]
  grafo: {
    nodos: Nodo[]
    aristas: Arista[]
  }
}

// ---------------------------------------------------------------------------
// Funciones que llaman a la API.
// ---------------------------------------------------------------------------

// Hace un GET a la ruta indicada y devuelve el JSON de la respuesta.
// Si la API responde con un error (por ejemplo 422 o 500), lanza una excepción.
async function pedir<T>(ruta: string): Promise<T> {
  const respuesta = await fetch(URL_API + ruta)
  if (!respuesta.ok) {
    throw new Error(`La API respondió ${respuesta.status} en ${ruta}`)
  }
  return respuesta.json()
}

export function obtenerEstado(): Promise<EstadoApi> {
  return pedir<EstadoApi>('/')
}

export function obtenerCronograma(umbral: number): Promise<Cronograma> {
  return pedir<Cronograma>(`/cronograma?umbral=${umbral}`)
}
