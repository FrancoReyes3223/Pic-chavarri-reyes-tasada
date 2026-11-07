// Dibuja el grafo de conflictos en SVG con posiciones fijas que calcula otro componente
// (GrafoGrilla o GrafoPorTurno). No hay simulación: los nodos no se mueven solos,
// y al cambiar el umbral solo aparecen o desaparecen aristas.
import { useMemo, useState } from 'react'
import type { Arista, Nodo } from '../api'
import { colorDelTurno, turnoRayado } from '../colores'

export interface Posicion {
  x: number
  y: number
}

// Textos fijos del dibujo: nombres de filas y columnas.
export interface Encabezado {
  x: number
  y: number
  texto: string
  ancla: 'start' | 'middle' | 'end'
  color?: string // por ejemplo, el color del turno en la vista por turnos
}

interface Props {
  nodos: Nodo[]
  aristas: Arista[]
  posiciones: Map<string, Posicion>
  ancho: number // tamaño del dibujo en unidades del SVG; después se escala al ancho de la pantalla
  alto: number
  encabezados: Encabezado[]
  maxLetrasEtiqueta: number // 0 = sin nombres al lado de los nodos
}

const RADIO_NODO = 7

function GrafoSvg({ nodos, aristas, posiciones, ancho, alto, encabezados, maxLetrasEtiqueta }: Props) {
  // La materia que está bajo el mouse (o con el foco del teclado). null = ninguna.
  const [resaltada, setResaltada] = useState<string | null>(null)

  // Para cada materia, el conjunto de materias con las que está en conflicto.
  const vecinas = useMemo(() => {
    const resultado = new Map<string, Set<string>>()
    for (const nodo of nodos) {
      resultado.set(nodo.id, new Set())
    }
    for (const arista of aristas) {
      resultado.get(arista.origen)?.add(arista.destino)
      resultado.get(arista.destino)?.add(arista.origen)
    }
    return resultado
  }, [nodos, aristas])

  let pesoMaximo = 0
  for (const arista of aristas) {
    pesoMaximo = Math.max(pesoMaximo, arista.peso)
  }

  // Un nodo se ve "apagado" si hay una materia resaltada y no es ella ni una vecina.
  function estaApagado(id: string): boolean {
    if (resaltada === null) return false
    return id !== resaltada && !vecinas.get(resaltada)?.has(id)
  }

  const nodoResaltado = nodos.find((nodo) => nodo.id === resaltada)

  return (
    <div className="grafo-svg">
      <div className="grafo-svg-desplazable">
        <svg viewBox={`0 0 ${ancho} ${alto}`} role="img" aria-label="Grafo de conflictos entre materias">
          <defs>
            {/* Rayas del color de fondo para los turnos 9 en adelante. */}
            <pattern id="rayas" width="4" height="4" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
              <rect width="1.6" height="4" className="rayas-trazo" />
            </pattern>
          </defs>

          {encabezados.map((encabezado) => (
            <text
              key={encabezado.texto}
              x={encabezado.x}
              y={encabezado.y}
              textAnchor={encabezado.ancla}
              className="grafo-encabezado"
              style={encabezado.color ? { fill: encabezado.color } : undefined}
            >
              {encabezado.texto}
            </text>
          ))}

          {/* Aristas: curvas, así dos aristas entre nodos alineados no se tapan. */}
          <g>
            {aristas.map((arista) => {
              const a = posiciones.get(arista.origen)
              const b = posiciones.get(arista.destino)
              if (!a || !b) return null
              const intensidad = pesoMaximo === 0 ? 1 : arista.peso / pesoMaximo
              const tocaResaltada = resaltada === arista.origen || resaltada === arista.destino
              let clase = 'grafo-arista'
              if (resaltada !== null) {
                clase = tocaResaltada ? 'grafo-arista resaltada' : 'grafo-arista apagada'
              }
              return (
                <path
                  key={arista.origen + '-' + arista.destino}
                  d={curva(a, b)}
                  className={clase}
                  style={{ strokeWidth: 0.75 + 2.5 * intensidad, strokeOpacity: tocaResaltada ? 0.9 : 0.15 + 0.5 * intensidad }}
                />
              )
            })}
          </g>

          {/* Nodos y nombres. */}
          <g>
            {nodos.map((nodo) => {
              const p = posiciones.get(nodo.id)
              if (!p) return null
              return (
                <g
                  key={nodo.id}
                  className={estaApagado(nodo.id) ? 'grafo-nodo apagado' : 'grafo-nodo'}
                  tabIndex={0}
                  onMouseEnter={() => setResaltada(nodo.id)}
                  onMouseLeave={() => setResaltada(null)}
                  onFocus={() => setResaltada(nodo.id)}
                  onBlur={() => setResaltada(null)}
                >
                  <title>{`${nodo.label}: turno ${nodo.turno}`}</title>
                  {/* Círculo invisible más grande: facilita apuntar con el mouse. */}
                  <circle cx={p.x} cy={p.y} r={RADIO_NODO + 6} fill="transparent" />
                  <circle cx={p.x} cy={p.y} r={RADIO_NODO} style={{ fill: colorDelTurno(nodo.turno) }} className="grafo-circulo" />
                  {turnoRayado(nodo.turno) && <circle cx={p.x} cy={p.y} r={RADIO_NODO} fill="url(#rayas)" />}
                  {maxLetrasEtiqueta > 0 && (
                    <text x={p.x + RADIO_NODO + 5} y={p.y + 4} className="grafo-etiqueta">
                      {recortar(nodo.label, maxLetrasEtiqueta)}
                    </text>
                  )}
                </g>
              )
            })}
          </g>
        </svg>
      </div>

      {/* Detalle de la materia resaltada, debajo del dibujo. */}
      <p className="grafo-detalle" aria-live="polite">
        {nodoResaltado ? (
          <>
            <strong>{nodoResaltado.label}</strong> · Turno {nodoResaltado.turno} ·{' '}
            {nodoResaltado.carrera}, {nodoResaltado.anio}.º año ·{' '}
            {vecinas.get(nodoResaltado.id)?.size ?? 0} conflictos
          </>
        ) : (
          'Pasá el mouse por una materia para resaltar sus conflictos.'
        )}
      </p>
    </div>
  )
}

// Curva entre dos puntos: se arquea hacia un costado desde el punto medio, a una
// distancia proporcional al largo de la arista. De los dos costados posibles elegimos
// el de abajo, así las curvas no tapan los títulos de arriba; si las dos opciones
// quedan a la misma altura (arista vertical), elegimos la de la izquierda.
function curva(a: Posicion, b: Posicion): string {
  const medioX = (a.x + b.x) / 2
  const medioY = (a.y + b.y) / 2
  const curvatura = 0.18
  const desvioX = -(b.y - a.y) * curvatura
  const desvioY = (b.x - a.x) * curvatura

  let controlX = medioX + desvioX
  let controlY = medioY + desvioY
  if (desvioY < 0 || (desvioY === 0 && desvioX > 0)) {
    controlX = medioX - desvioX
    controlY = medioY - desvioY
  }
  return `M ${a.x} ${a.y} Q ${controlX} ${controlY} ${b.x} ${b.y}`
}

// Acorta un nombre largo y le agrega "…" al final.
function recortar(texto: string, maxLetras: number): string {
  if (texto.length <= maxLetras) return texto
  return texto.slice(0, maxLetras - 1).trimEnd() + '…'
}

export default GrafoSvg
