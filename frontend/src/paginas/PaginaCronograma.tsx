// Página /cronograma: el slider de umbral y la grilla con las materias de cada turno.
// El umbral es el mismo de /grafo (lo guarda App), así que los dos sliders siempre
// muestran el mismo valor.
import type { Cronograma as DatosCronograma } from '../api'
import ControlUmbral from '../componentes/ControlUmbral'
import Cronograma from '../componentes/Cronograma'
import Resumen from '../componentes/Resumen'

interface Props {
  cronograma: DatosCronograma | null
  umbral: number
  alCambiarUmbral: (nuevoUmbral: number) => void
  cargando: boolean
}

function PaginaCronograma({ cronograma, umbral, alCambiarUmbral, cargando }: Props) {
  return (
    <>
      <h1 className="titulo-pagina">Cronograma</h1>
      <p className="bajada">
        Las materias de un mismo turno se pueden rendir el mismo día: ningún par entre ellas
        alcanza el umbral.
      </p>

      <section className="controles">
        <ControlUmbral umbral={umbral} alCambiar={alCambiarUmbral} />
        {cronograma && <Resumen cronograma={cronograma} cargando={cargando} />}
      </section>

      {cronograma && (
        <div className={cargando ? 'actualizando' : ''}>
          <Cronograma turnos={cronograma.turnos} />
        </div>
      )}
    </>
  )
}

export default PaginaCronograma
