// Página /cronograma: la grilla con las materias de cada turno.
import { Link } from 'react-router-dom'
import type { Cronograma as DatosCronograma } from '../api'
import Cronograma from '../componentes/Cronograma'
import Resumen from '../componentes/Resumen'

interface Props {
  cronograma: DatosCronograma | null
  cargando: boolean
}

function PaginaCronograma({ cronograma, cargando }: Props) {
  return (
    <>
      <h1 className="titulo-pagina">Cronograma</h1>
      <p className="bajada">
        Las materias de un mismo turno se pueden rendir el mismo día: ningún par entre ellas
        alcanza el umbral. El umbral se cambia en la página del{' '}
        <Link to="/grafo">grafo</Link>.
      </p>

      {cronograma && (
        <>
          <section className="controles controles-simple">
            <Resumen cronograma={cronograma} cargando={cargando} />
          </section>
          <div className={cargando ? 'actualizando' : ''}>
            <Cronograma turnos={cronograma.turnos} />
          </div>
        </>
      )}
    </>
  )
}

export default PaginaCronograma
