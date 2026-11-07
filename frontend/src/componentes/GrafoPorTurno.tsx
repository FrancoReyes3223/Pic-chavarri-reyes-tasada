// Vista "por turno": una columna por turno. Muestra el resultado del coloreo: como es
// válido, ninguna arista une dos materias de la misma columna, todas van de una a otra.
import type { Arista, Nodo } from '../api'
import { colorDelTurno } from '../colores'
import GrafoSvg from './GrafoSvg'
import type { Encabezado, Posicion } from './GrafoSvg'

const ANCHO = 1000
const MARGEN_SUPERIOR = 44 // lugar para "Turno 1", "Turno 2", ...
const SEPARACION_VERTICAL = 30
const ANCHO_MINIMO_PARA_NOMBRES = 150 // con columnas más angostas, los nombres no entran

interface Props {
  nodos: Nodo[]
  aristas: Arista[]
}

function GrafoPorTurno({ nodos, aristas }: Props) {
  let cantidadDeTurnos = 1
  for (const nodo of nodos) {
    cantidadDeTurnos = Math.max(cantidadDeTurnos, nodo.turno)
  }
  const anchoColumna = ANCHO / cantidadDeTurnos
  const conNombres = anchoColumna >= ANCHO_MINIMO_PARA_NOMBRES

  // Dentro de cada columna, ordenamos por carrera y año para que sea fácil de leer.
  const ordenados = [...nodos].sort(
    (a, b) => a.turno - b.turno || a.carrera.localeCompare(b.carrera) || a.anio - b.anio || a.id.localeCompare(b.id),
  )
  const ocupadosPorTurno = new Map<number, number>()
  const posiciones = new Map<string, Posicion>()
  let filasMaximas = 0
  for (const nodo of ordenados) {
    const lugar = ocupadosPorTurno.get(nodo.turno) ?? 0
    ocupadosPorTurno.set(nodo.turno, lugar + 1)
    filasMaximas = Math.max(filasMaximas, lugar + 1)
    const inicioColumna = (nodo.turno - 1) * anchoColumna
    posiciones.set(nodo.id, {
      x: conNombres ? inicioColumna + 14 : inicioColumna + anchoColumna / 2,
      y: MARGEN_SUPERIOR + 14 + lugar * SEPARACION_VERTICAL,
    })
  }

  const encabezados: Encabezado[] = []
  for (let turno = 1; turno <= cantidadDeTurnos; turno++) {
    const inicioColumna = (turno - 1) * anchoColumna
    encabezados.push({
      x: conNombres ? inicioColumna + 7 : inicioColumna + anchoColumna / 2,
      y: 20,
      texto: conNombres ? `Turno ${turno}` : `T${turno}`,
      ancla: conNombres ? 'start' : 'middle',
      color: colorDelTurno(turno),
    })
  }

  return (
    <GrafoSvg
      nodos={nodos}
      aristas={aristas}
      posiciones={posiciones}
      ancho={ANCHO}
      alto={MARGEN_SUPERIOR + filasMaximas * SEPARACION_VERTICAL + 10}
      encabezados={encabezados}
      maxLetrasEtiqueta={conNombres ? Math.floor((anchoColumna - 40) / 6.6) : 0}
    />
  )
}

export default GrafoPorTurno
