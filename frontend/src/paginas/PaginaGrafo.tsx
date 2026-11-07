// Página /grafo: el slider de umbral y el grafo de conflictos coloreado por turno.
// El mismo grafo se puede ver de tres formas, y cada una muestra algo distinto:
//   /grafo          por cercanía: qué materias forman grupos de conflictos (simulación de fuerzas)
//   /grafo/grilla   por carrera y año: por qué hay conflictos
//   /grafo/turnos   por turno: el resultado del coloreo
import { NavLink } from 'react-router-dom'
import type { Cronograma } from '../api'
import ControlUmbral from '../componentes/ControlUmbral'
import GrafoConflictos from '../componentes/GrafoConflictos'
import GrafoGrilla from '../componentes/GrafoGrilla'
import GrafoPorTurno from '../componentes/GrafoPorTurno'
import LeyendaTurnos from '../componentes/LeyendaTurnos'
import Resumen from '../componentes/Resumen'

export type VistaGrafo = 'fuerzas' | 'grilla' | 'turnos'

// Qué muestra cada vista y cómo se usa.
const AYUDA_POR_VISTA: Record<VistaGrafo, string> = {
  fuerzas:
    'Muestra qué materias forman grupos de conflictos: se acomodan solas y las que chocan entre sí quedan cerca. Arrastrá un punto para moverlo y usá la rueda para hacer zoom.',
  grilla:
    'Muestra por qué hay conflictos: cada fila es una carrera y cada columna un año, así se ve que chocan las materias del mismo año y de años cercanos. Al cambiar el umbral las materias no se mueven, solo aparecen o desaparecen conflictos.',
  turnos:
    'Muestra el resultado del coloreo: cada columna es un turno, y ninguna línea une dos materias de la misma columna. Por eso se pueden rendir el mismo día.',
}

interface Props {
  vista: VistaGrafo
  cronograma: Cronograma | null
  umbral: number
  alCambiarUmbral: (nuevoUmbral: number) => void
  cargando: boolean
}

function PaginaGrafo({ vista, cronograma, umbral, alCambiarUmbral, cargando }: Props) {
  return (
    <>
      <h1 className="titulo-pagina">Grafo de conflictos</h1>
      <p className="bajada">
        Cada punto es una materia, pintada con el color de su turno. Una línea une dos
        materias en conflicto, y es más gruesa cuantos más estudiantes afectados predice el
        modelo. Dos materias unidas nunca tienen el mismo color.
      </p>

      <section className="controles">
        <ControlUmbral umbral={umbral} alCambiar={alCambiarUmbral} />
        {cronograma && <Resumen cronograma={cronograma} cargando={cargando} />}
      </section>

      {/* Pestañas para elegir cómo ver el grafo. "end" hace que /grafo no quede
          marcado cuando estamos en /grafo/grilla. */}
      <nav className="vistas" aria-label="Forma de ver el grafo">
        <NavLink to="/grafo" end>Por cercanía</NavLink>
        <NavLink to="/grafo/grilla">Por carrera y año</NavLink>
        <NavLink to="/grafo/turnos">Por turno</NavLink>
      </nav>
      <p className="ayuda">{AYUDA_POR_VISTA[vista]}</p>

      {/* El grafo a la izquierda y la leyenda de colores a la derecha (abajo en celular). */}
      {cronograma && (
        <div className="grafo-con-leyenda">
          {vista === 'fuerzas' && (
            <GrafoConflictos nodos={cronograma.grafo.nodos} aristas={cronograma.grafo.aristas} />
          )}
          {vista === 'grilla' && (
            <GrafoGrilla nodos={cronograma.grafo.nodos} aristas={cronograma.grafo.aristas} />
          )}
          {vista === 'turnos' && (
            <GrafoPorTurno nodos={cronograma.grafo.nodos} aristas={cronograma.grafo.aristas} />
          )}
          <LeyendaTurnos turnos={cronograma.turnos} />
        </div>
      )}
    </>
  )
}

export default PaginaGrafo
