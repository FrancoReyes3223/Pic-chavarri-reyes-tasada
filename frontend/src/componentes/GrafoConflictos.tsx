// Grafo de conflictos: cada nodo es una materia pintada con el color de su turno,
// y cada arista une dos materias en conflicto. Lo dibuja la librería
// react-force-graph-2d, que ubica los nodos con una simulación de fuerzas:
// las aristas los atraen como resortes y los nodos se repelen entre sí,
// así las materias con muchos conflictos en común quedan cerca.
import { useEffect, useMemo, useRef, useState } from 'react'
import ForceGraph2D from 'react-force-graph-2d'
import type { ForceGraphMethods } from 'react-force-graph-2d'
import type { Arista, Nodo } from '../api'
import { turnoRayado } from '../colores'

// Los datos en el formato que pide la librería: "nodes" con id, y "links" con source y target.
interface NodoGrafico {
  id: string
  nombre: string
  carrera: string
  anio: number
  turno: number
  conflictos: number // grado del nodo: con cuántas materias choca
  x?: number // posición, la completa la librería
  y?: number
}

interface EnlaceGrafico {
  source: string
  target: string
  peso: number
}

const RADIO_NODO = 6
const ALTO_GRAFO = 520

// Posición de cada materia en el dibujo anterior. Al mover el slider las materias
// arrancan desde donde estaban, así el grafo no se desarma por completo.
let nodosAnteriores = new Map<string, NodoGrafico>()

interface Props {
  nodos: Nodo[]
  aristas: Arista[]
}

function GrafoConflictos({ nodos, aristas }: Props) {
  const grafoRef = useRef<ForceGraphMethods<NodoGrafico, EnlaceGrafico> | undefined>(undefined)

  // La librería necesita un ancho en píxeles: medimos el contenedor y lo
  // volvemos a medir si cambia el tamaño de la ventana.
  const contenedorRef = useRef<HTMLDivElement>(null)
  const [ancho, setAncho] = useState(0) // 0 = todavía no lo medimos
  useEffect(() => {
    const contenedor = contenedorRef.current
    if (!contenedor) return
    const observador = new ResizeObserver(() => setAncho(contenedor.clientWidth))
    observador.observe(contenedor)
    return () => observador.disconnect()
  }, [])

  // Pasamos los datos de la API al formato de la librería.
  // useMemo: solo se recalcula cuando llegan nodos o aristas nuevos.
  const datos = useMemo(() => {
    const conflictosPorMateria = new Map<string, number>()
    for (const arista of aristas) {
      conflictosPorMateria.set(arista.origen, (conflictosPorMateria.get(arista.origen) ?? 0) + 1)
      conflictosPorMateria.set(arista.destino, (conflictosPorMateria.get(arista.destino) ?? 0) + 1)
    }

    const nodosNuevos = new Map<string, NodoGrafico>()
    for (const nodo of nodos) {
      const anterior = nodosAnteriores.get(nodo.id)
      nodosNuevos.set(nodo.id, {
        id: nodo.id,
        nombre: nodo.label,
        carrera: nodo.carrera,
        anio: nodo.anio,
        turno: nodo.turno,
        conflictos: conflictosPorMateria.get(nodo.id) ?? 0,
        x: anterior?.x,
        y: anterior?.y,
      })
    }
    nodosAnteriores = nodosNuevos

    const enlaces: EnlaceGrafico[] = []
    for (const arista of aristas) {
      enlaces.push({ source: arista.origen, target: arista.destino, peso: arista.peso })
    }

    return { nodes: Array.from(nodosNuevos.values()), links: enlaces }
  }, [nodos, aristas])

  // El peso más alto, para que el grosor de cada arista sea relativo a él.
  const pesoMaximo = useMemo(() => {
    let maximo = 0
    for (const arista of aristas) {
      maximo = Math.max(maximo, arista.peso)
    }
    return maximo
  }, [aristas])

  // El canvas no entiende variables CSS: leemos los colores reales una vez, al abrir la página.
  const [colores] = useState(leerColores)

  // Cada nodo es un círculo con el color de su turno, con un borde del color de fondo
  // para que se distingan cuando se superponen. Los turnos 9 en adelante llevan rayas.
  function dibujarNodo(nodo: NodoGrafico, ctx: CanvasRenderingContext2D, escala: number) {
    const x = nodo.x ?? 0
    const y = nodo.y ?? 0
    ctx.beginPath()
    ctx.arc(x, y, RADIO_NODO, 0, 2 * Math.PI)
    ctx.fillStyle = colores.turnos[(nodo.turno - 1) % colores.turnos.length]
    ctx.fill()

    if (turnoRayado(nodo.turno)) {
      ctx.save()
      ctx.clip()
      ctx.strokeStyle = colores.fondo
      ctx.lineWidth = 1.5
      for (let desplazamiento = -2 * RADIO_NODO; desplazamiento <= 2 * RADIO_NODO; desplazamiento += 4) {
        ctx.beginPath()
        ctx.moveTo(x + desplazamiento - RADIO_NODO, y + RADIO_NODO)
        ctx.lineTo(x + desplazamiento + RADIO_NODO, y - RADIO_NODO)
        ctx.stroke()
      }
      ctx.restore()
    }

    ctx.beginPath()
    ctx.arc(x, y, RADIO_NODO, 0, 2 * Math.PI)
    ctx.strokeStyle = colores.fondo
    ctx.lineWidth = 2 / escala
    ctx.stroke()
  }

  // Zona donde el mouse "toca" el nodo (para el tooltip): el mismo círculo.
  function dibujarZonaDelMouse(nodo: NodoGrafico, color: string, ctx: CanvasRenderingContext2D) {
    ctx.beginPath()
    ctx.arc(nodo.x ?? 0, nodo.y ?? 0, RADIO_NODO + 2, 0, 2 * Math.PI)
    ctx.fillStyle = color
    ctx.fill()
  }

  // Texto que aparece al pasar el mouse por un nodo.
  function textoDelNodo(nodo: NodoGrafico): string {
    const conflictos = nodo.conflictos === 1 ? '1 conflicto' : `${nodo.conflictos} conflictos`
    return `<strong>${nodo.nombre}</strong><br>Turno ${nodo.turno}<br>${nodo.carrera}, ${nodo.anio}.º año, ${conflictos}`
  }

  // Grosor de la arista: entre 0.5 y 4 píxeles según cuántos estudiantes afectados predice el modelo.
  function grosorDeArista(enlace: EnlaceGrafico): number {
    if (pesoMaximo === 0) return 1
    return 0.5 + 3.5 * (enlace.peso / pesoMaximo)
  }

  return (
    <div ref={contenedorRef} className="grafo">
      {/* Dibujamos recién cuando sabemos el ancho, así el primer encuadre ya es el correcto. */}
      {ancho > 0 && (
        <ForceGraph2D<NodoGrafico, EnlaceGrafico>
          ref={grafoRef}
          graphData={datos}
          width={ancho}
          height={Math.min(ALTO_GRAFO, ancho)} /* en celular queda cuadrado, sin espacio vacío */
          backgroundColor="rgba(0, 0, 0, 0)"
          nodeCanvasObject={dibujarNodo}
          nodePointerAreaPaint={dibujarZonaDelMouse}
          nodeLabel={textoDelNodo}
          linkColor={() => colores.arista}
          linkWidth={grosorDeArista}
          cooldownTicks={120}
          onEngineStop={() => grafoRef.current?.zoomToFit(400, 30)}
        />
      )}
    </div>
  )
}

// Lee de index.css los colores de los turnos, del fondo y de las aristas.
function leerColores() {
  const estilos = getComputedStyle(document.documentElement)
  const turnos: string[] = []
  for (let numero = 1; numero <= 8; numero++) {
    turnos.push(estilos.getPropertyValue(`--turno-${numero}`).trim())
  }
  return {
    turnos,
    fondo: estilos.getPropertyValue('--fondo').trim(),
    arista: estilos.getPropertyValue('--arista').trim(),
  }
}

export default GrafoConflictos
