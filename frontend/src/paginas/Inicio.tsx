// Página de inicio (/): qué hace el sistema y un acceso a cada sección.
import { Link } from 'react-router-dom'

function Inicio() {
  return (
    <>
      <h1 className="titulo-pagina">Mesas de examen</h1>
      <p className="bajada">
        Cronograma del próximo período. Dos materias van en turnos distintos cuando el
        modelo predice que muchos estudiantes querrían rendir las dos.
      </p>

      <ol className="pasos">
        <li>
          <h2>1. Predecir</h2>
          <p>
            Un modelo de regresión estima, para cada par de materias, cuántos estudiantes
            querrían rendir las dos.
          </p>
          <Link to="/modelo">Ver el modelo</Link>
        </li>
        <li>
          <h2>2. Armar el grafo</h2>
          <p>
            Cada materia es un nodo. Dos materias se unen si los estudiantes afectados
            alcanzan el umbral de conflicto, que se elige con un slider.
          </p>
          <Link to="/grafo">Ver el grafo</Link>
        </li>
        <li>
          <h2>3. Colorear</h2>
          <p>
            Un coloreo greedy le da a cada materia un turno (color) distinto del de todas
            las materias con las que choca.
          </p>
          <Link to="/cronograma">Ver el cronograma</Link>
        </li>
      </ol>
    </>
  )
}

export default Inicio
