// Página /grafo: el slider de umbral y el grafo de conflictos coloreado por turno.
import type { Cronograma } from '../api'
import ControlUmbral from '../componentes/ControlUmbral'
import GrafoConflictos from '../componentes/GrafoConflictos'
import LeyendaTurnos from '../componentes/LeyendaTurnos'
import Resumen from '../componentes/Resumen'

interface Props {
  cronograma: Cronograma | null
  umbral: number
  alCambiarUmbral: (nuevoUmbral: number) => void
  cargando: boolean
}

function PaginaGrafo({ cronograma, umbral, alCambiarUmbral, cargando }: Props) {
  return (
    <>
      <h1 className="titulo-pagina">Grafo de conflictos</h1>
      <p className="bajada">
        Cada punto es una materia, pintada con el color de su turno. Una línea une dos
        materias en conflicto, y es más gruesa cuantos más estudiantes afectados predice el
        modelo. Dos materias unidas nunca tienen el mismo color. Pasá el mouse por un punto
        para ver la materia; con la rueda se hace zoom.
      </p>

      <section className="controles">
        <ControlUmbral umbral={umbral} alCambiar={alCambiarUmbral} />
        {cronograma && <Resumen cronograma={cronograma} cargando={cargando} />}
      </section>

      {/* El grafo a la izquierda y la leyenda de colores a la derecha (abajo en celular). */}
      {cronograma && (
        <div className="grafo-con-leyenda">
          <GrafoConflictos nodos={cronograma.grafo.nodos} aristas={cronograma.grafo.aristas} />
          <LeyendaTurnos turnos={cronograma.turnos} />
        </div>
      )}
    </>
  )
}

export default PaginaGrafo
