// Vista "por carrera y año": cada materia va en una grilla fija, una fila por carrera
// y una columna por año. Muestra por qué hay conflictos (mismo año, años cercanos).
// Las posiciones no dependen del umbral.
import type { Arista, Nodo } from '../api'
import GrafoSvg from './GrafoSvg'
import type { Encabezado, Posicion } from './GrafoSvg'

const ANCHO = 1000
const MARGEN_IZQUIERDO = 100 // lugar para el nombre de la carrera
const MARGEN_SUPERIOR = 40 // lugar para "1.º año", "2.º año", ...
const SEPARACION_VERTICAL = 34 // entre las materias de una misma celda
const ALTO_CELDA = 140

interface Props {
  nodos: Nodo[]
  aristas: Arista[]
}

function GrafoGrilla({ nodos, aristas }: Props) {
  // Carreras en el orden en que aparecen, y el año más alto.
  const carreras: string[] = []
  let anioMaximo = 1
  for (const nodo of nodos) {
    if (!carreras.includes(nodo.carrera)) carreras.push(nodo.carrera)
    anioMaximo = Math.max(anioMaximo, nodo.anio)
  }

  const anchoCelda = (ANCHO - MARGEN_IZQUIERDO) / anioMaximo
  const alto = MARGEN_SUPERIOR + carreras.length * ALTO_CELDA

  // Ubicamos cada materia en su celda, una debajo de la otra (ordenadas por id).
  const ordenados = [...nodos].sort((a, b) => a.id.localeCompare(b.id))
  const ocupadosPorCelda = new Map<string, number>()
  const posiciones = new Map<string, Posicion>()
  for (const nodo of ordenados) {
    const celda = nodo.carrera + '-' + nodo.anio
    const lugar = ocupadosPorCelda.get(celda) ?? 0
    ocupadosPorCelda.set(celda, lugar + 1)
    posiciones.set(nodo.id, {
      x: MARGEN_IZQUIERDO + (nodo.anio - 1) * anchoCelda + 14,
      y: MARGEN_SUPERIOR + carreras.indexOf(nodo.carrera) * ALTO_CELDA + 28 + lugar * SEPARACION_VERTICAL,
    })
  }

  const encabezados: Encabezado[] = []
  for (let anio = 1; anio <= anioMaximo; anio++) {
    encabezados.push({ x: MARGEN_IZQUIERDO + (anio - 1) * anchoCelda + 7, y: 18, texto: `${anio}.º año`, ancla: 'start' })
  }
  for (let fila = 0; fila < carreras.length; fila++) {
    encabezados.push({
      x: 0,
      y: MARGEN_SUPERIOR + fila * ALTO_CELDA + 28 + SEPARACION_VERTICAL + 4,
      texto: carreras[fila],
      ancla: 'start',
    })
  }

  return (
    <GrafoSvg
      nodos={nodos}
      aristas={aristas}
      posiciones={posiciones}
      ancho={ANCHO}
      alto={alto}
      encabezados={encabezados}
      maxLetrasEtiqueta={Math.floor((anchoCelda - 40) / 6.6)}
    />
  )
}

export default GrafoGrilla
