// Resumen del cronograma escrito como una oración. Lo muestran /grafo y /cronograma.
import type { Cronograma } from '../api'

interface Props {
  cronograma: Cronograma
  cargando: boolean
}

function Resumen({ cronograma, cargando }: Props) {
  // aria-live hace que un lector de pantalla lea el resumen nuevo al mover el slider.
  return (
    <p className={cargando ? 'resumen actualizando' : 'resumen'} aria-live="polite">
      Con un umbral de <strong>{cronograma.umbral}</strong>{' '}
      {cronograma.umbral === 1 ? 'estudiante' : 'estudiantes'}, las{' '}
      <strong>{cronograma.total_materias}</strong> materias necesitan{' '}
      <strong>{cronograma.total_turnos} turnos</strong> para separar los{' '}
      <strong>{cronograma.total_conflictos}</strong> pares en conflicto.
    </p>
  )
}

export default Resumen
