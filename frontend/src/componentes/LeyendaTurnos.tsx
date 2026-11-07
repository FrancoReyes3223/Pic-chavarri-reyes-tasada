// Tablita que explica qué turno representa cada color del grafo.
import type { Turno } from '../api'
import { colorDelTurno, turnoRayado } from '../colores'

interface Props {
  turnos: Turno[]
}

function LeyendaTurnos({ turnos }: Props) {
  return (
    <table className="leyenda">
      <caption>Qué representa cada color</caption>
      <thead>
        <tr>
          <th scope="col">Color</th>
          <th scope="col">Turno</th>
          <th scope="col" className="numero">Materias</th>
        </tr>
      </thead>
      <tbody>
        {turnos.map((turno) => (
          <tr key={turno.turno}>
            <td>
              {/* Un círculo igual a los nodos del grafo. */}
              <span
                className={turnoRayado(turno.turno) ? 'muestra-color rayada' : 'muestra-color'}
                style={{ backgroundColor: colorDelTurno(turno.turno) }}
                aria-hidden="true"
              />
            </td>
            <th scope="row">Turno {turno.turno}</th>
            <td className="numero">{turno.materias.length}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

export default LeyendaTurnos
