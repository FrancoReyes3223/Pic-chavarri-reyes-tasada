// Página /modelo: cómo se predicen los estudiantes afectados y cómo se eligió el modelo.
import type { Metricas } from '../api'
import TablaMetricas from '../componentes/TablaMetricas'

interface Props {
  metricas: Metricas | null
}

function PaginaModelo({ metricas }: Props) {
  return (
    <>
      <h1 className="titulo-pagina">El modelo</h1>
      <p className="bajada">
        Para cada par de materias, el modelo predice cuántos estudiantes querrían rendir las
        dos en el próximo período. Esa predicción es el peso de la arista en el grafo.
      </p>

      <section className="seccion">
        <h2>Qué predice y con qué datos</h2>
        <p className="texto">
          Es un modelo de <strong>regresión</strong>: predice un número, la cantidad de
          estudiantes afectados, y no una categoría. Lo entrenamos con un dataset sintético de
          45 materias (3 carreras, 5 años y 3 materias por año): 990 pares de materias en 8
          períodos.
        </p>
        <p className="texto">Para cada par usa estos datos:</p>
        <ul className="lista">
          <li>Cuántos estudiantes compartieron las dos materias en los períodos anteriores.</li>
          <li>Si son del mismo año y de la misma carrera, y cuántos años las separan.</li>
          <li>El año de la materia más baja del par.</li>
          <li>El promedio de inscriptos de cada una.</li>
        </ul>
      </section>

      <section className="seccion">
        <h2>Cómo lo evaluamos</h2>
        <ul className="lista">
          <li>
            <strong>Partición temporal:</strong> entrenamos con los períodos 1 a 6 y dejamos los
            períodos 7 y 8 como test, igual que pasaría en la realidad: se predice el futuro con
            el pasado.
          </li>
          <li>
            <strong>Validación cruzada por período:</strong> los hiperparámetros y el modelo
            ganador se eligieron con <code>GroupKFold</code> sobre los datos de entrenamiento.
            Cada vuelta deja afuera un período entero.
          </li>
          <li>
            <strong>El test se miró una sola vez</strong>, al final, para que el error que
            reportamos sea una estimación honesta.
          </li>
        </ul>
      </section>

      <section className="seccion">
        <h2>Cómo se eligió el modelo</h2>
        {metricas ? (
          <TablaMetricas metricas={metricas} />
        ) : (
          <p className="ayuda">Cargando métricas…</p>
        )}
        <p className="texto">
          KNN predice promediando los 15 pares de materias más parecidos. Como compara
          distancias, primero escalamos los datos con <code>StandardScaler</code>: si no, el
          promedio de inscriptos (de 35 a 219) pesaría mucho más que "mismo año" (0 o 1).
        </p>
        <p className="texto">
          Un árbol muy profundo (<code>max_depth=20</code>) memoriza los datos: su error en
          entrenamiento es 0.08 estudiantes, pero en validación sube a 1.23. Eso es
          sobreajuste, y por eso la profundidad se eligió con validación cruzada (quedó en 5).
        </p>
      </section>
    </>
  )
}

export default PaginaModelo
