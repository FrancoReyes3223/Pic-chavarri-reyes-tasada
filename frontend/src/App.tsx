import { useEffect, useState } from 'react'
import { URL_API, obtenerCronograma, obtenerEstado, obtenerMetricas } from './api'
import type { Cronograma as DatosCronograma, EstadoApi, Metricas } from './api'
import ControlUmbral from './componentes/ControlUmbral'
import Cronograma from './componentes/Cronograma'
import TablaMetricas from './componentes/TablaMetricas'

// Umbral con el que arranca la página (después lo mueve el slider).
const UMBRAL_INICIAL = 5

// Milisegundos que esperamos después de mover el slider antes de pedirle el
// cronograma a la API. Así no mandamos un pedido por cada paso mientras se arrastra.
const ESPERA_SLIDER = 200

function App() {
  // Lo que devuelve la API. Empiezan en null porque al abrir la página todavía no llegó nada.
  const [estadoApi, setEstadoApi] = useState<EstadoApi | null>(null)
  const [metricas, setMetricas] = useState<Metricas | null>(null)
  const [cronograma, setCronograma] = useState<DatosCronograma | null>(null)
  const [error, setError] = useState<string | null>(null)

  // El umbral elegido en el slider y si estamos esperando un cronograma nuevo.
  const [umbral, setUmbral] = useState(UMBRAL_INICIAL)
  const [cargando, setCargando] = useState(true)

  // Estado de la API y métricas: no dependen del umbral, se piden una sola vez.
  useEffect(() => {
    async function cargarDatosFijos() {
      try {
        setEstadoApi(await obtenerEstado())
        setMetricas(await obtenerMetricas())
      } catch (e) {
        setError(e instanceof Error ? e.message : String(e))
      }
    }
    cargarDatosFijos()
  }, [])

  // Cronograma: se vuelve a pedir cada vez que cambia el umbral.
  useEffect(() => {
    // Si el umbral cambia otra vez antes de que llegue la respuesta, React ejecuta
    // la función del return: cancela la espera y marca la respuesta vieja para
    // ignorarla. Así siempre se muestra el cronograma del último umbral elegido.
    let cancelado = false
    setCargando(true)

    const espera = setTimeout(async () => {
      try {
        const datos = await obtenerCronograma(umbral)
        if (!cancelado) {
          setCronograma(datos)
          setError(null)
        }
      } catch (e) {
        if (!cancelado) {
          setError(e instanceof Error ? e.message : String(e))
        }
      } finally {
        if (!cancelado) {
          setCargando(false)
        }
      }
    }, ESPERA_SLIDER)

    return () => {
      cancelado = true
      clearTimeout(espera)
    }
  }, [umbral])

  return (
    <main className="pagina">
      <header className="encabezado">
        <h1>Mesas de examen</h1>
        <p>
          Cronograma del próximo período. Dos materias van en turnos distintos
          cuando el modelo predice que muchos estudiantes querrían rendir las dos.
        </p>
        <LineaDeEstado estadoApi={estadoApi} error={error} />
      </header>

      {error && (
        <section className="aviso-error" role="alert">
          <h2>No se pudo conectar con la API</h2>
          <p>
            El frontend la busca en <code>{URL_API}</code>. Levantala desde la
            carpeta <code>backend</code> con{' '}
            <code>uvicorn app.main:app --reload --port 8000</code> y recargá la
            página.
          </p>
          <p className="ayuda">Detalle: {error}</p>
        </section>
      )}

      <section className="controles">
        <ControlUmbral umbral={umbral} alCambiar={setUmbral} />

        {/* aria-live hace que un lector de pantalla lea el resumen nuevo al mover el slider. */}
        {cronograma && (
          <p className={cargando ? 'resumen actualizando' : 'resumen'} aria-live="polite">
            Con un umbral de <strong>{cronograma.umbral}</strong>{' '}
            {cronograma.umbral === 1 ? 'estudiante' : 'estudiantes'}, las{' '}
            <strong>{cronograma.total_materias}</strong> materias necesitan{' '}
            <strong>{cronograma.total_turnos} turnos</strong> para separar los{' '}
            <strong>{cronograma.total_conflictos}</strong> pares en conflicto.
          </p>
        )}
      </section>

      {cronograma && (
        <section className="seccion">
          <h2>Cronograma</h2>
          <p className="texto">
            Las materias de un mismo turno se pueden rendir el mismo día: ningún par
            entre ellas supera el umbral.
          </p>
          <div className={cargando ? 'actualizando' : ''}>
            <Cronograma turnos={cronograma.turnos} />
          </div>
        </section>
      )}

      {metricas && (
        <section className="seccion">
          <h2>Cómo se eligió el modelo</h2>
          <TablaMetricas metricas={metricas} />
        </section>
      )}
    </main>
  )
}

// Muestra si la API responde y si los datos son de prueba o del modelo.
function LineaDeEstado({ estadoApi, error }: { estadoApi: EstadoApi | null; error: string | null }) {
  if (error) {
    return <p className="estado con-error">Sin conexión con la API</p>
  }
  if (!estadoApi) {
    return <p className="estado">Consultando la API…</p>
  }
  const origen = estadoApi.modo_mock
    ? 'con datos de prueba (modo mock)'
    : 'con las predicciones del modelo'
  return <p className="estado conectado">Conectado a la API, {origen}</p>
}

export default App
