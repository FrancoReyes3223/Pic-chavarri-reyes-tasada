// Grilla del cronograma: un bloque por turno con las materias que se rinden en él.
import type { Turno } from '../api'
import { colorDelTurno, turnoRayado } from '../colores'

interface Props {
  turnos: Turno[]
}

function Cronograma({ turnos }: Props) {
  return (
    <ol className="cronograma">
      {turnos.map((turno) => (
        <li key={turno.turno} className="turno">
          {/* Franja con el color del turno: es el mismo color que va a tener en el grafo. */}
          <span
            className={turnoRayado(turno.turno) ? 'franja rayada' : 'franja'}
            style={{ backgroundColor: colorDelTurno(turno.turno) }}
            aria-hidden="true"
          />
          <h3>Turno {turno.turno}</h3>
          <p className="cantidad">
            {turno.materias.length} {turno.materias.length === 1 ? 'materia' : 'materias'}
          </p>
          <ul>
            {turno.materias.map((materia) => (
              <li key={materia.id}>
                <span className="nombre-materia">{materia.nombre}</span>
                <span className="detalle-materia">
                  {materia.carrera}, {materia.anio}.º año
                </span>
              </li>
            ))}
          </ul>
        </li>
      ))}
    </ol>
  )
}

export default Cronograma
