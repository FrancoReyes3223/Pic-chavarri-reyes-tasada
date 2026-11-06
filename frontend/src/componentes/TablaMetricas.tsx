// Tabla que compara los 3 modelos de regresión y marca el elegido.
import type { Metricas } from '../api'

interface Props {
  metricas: Metricas
}

function TablaMetricas({ metricas }: Props) {
  return (
    <>
      <p className="texto">
        {metricas.descripcion} Probamos tres modelos y nos quedamos con{' '}
        {metricas.modelo_seleccionado}. Criterio: {metricas.criterio_seleccion}
      </p>

      {/* El contenedor permite desplazar la tabla de costado en pantallas chicas. */}
      <div className="tabla-contenedor">
        <table className="tabla-metricas">
          <thead>
            <tr>
              <th scope="col">Modelo</th>
              <th scope="col">Hiperparámetro</th>
              <th scope="col" className="numero">MAE validación</th>
              <th scope="col" className="numero">MAE test</th>
              <th scope="col" className="numero">R² test</th>
            </tr>
          </thead>
          <tbody>
            {metricas.modelos.map((fila) => (
              <tr key={fila.modelo} className={fila.es_ganador ? 'ganador' : ''}>
                <th scope="row">
                  {fila.modelo}
                  {fila.es_ganador && <span className="marca-elegido">elegido</span>}
                </th>
                <td>{fila.hiperparametro}</td>
                <td className="numero">{fila.mae_cv.toFixed(3)}</td>
                <td className="numero">{fila.mae_test.toFixed(3)}</td>
                <td className="numero">{fila.r2_test.toFixed(3)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <p className="ayuda">
        MAE: cuántos estudiantes le erra el modelo en promedio por par de materias (más bajo
        es mejor). R²: qué parte de la variación explica el modelo (más cerca de 1 es mejor).
      </p>
    </>
  )
}

export default TablaMetricas
