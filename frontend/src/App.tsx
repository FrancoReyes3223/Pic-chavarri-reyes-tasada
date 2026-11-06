import { useEffect, useState } from 'react'
import { URL_API, obtenerCronograma, obtenerEstado } from './api'
import type { Cronograma, EstadoApi } from './api'

// Umbral fijo por ahora. En el paso 2 lo va a controlar el slider.
const UMBRAL_INICIAL = 5

function App() {
  // Lo que devuelve la API. Empiezan en null porque al abrir la página todavía no llegó nada.
  const [estadoApi, setEstadoApi] = useState<EstadoApi | null>(null)
  const [cronograma, setCronograma] = useState<Cronograma | null>(null)
  const [error, setError] = useState<string | null>(null)

  // useEffect con [] se ejecuta una sola vez, cuando la página se abre.
  useEffect(() => {
    async function cargarDatos() {
      try {
        setEstadoApi(await obtenerEstado())
        setCronograma(await obtenerCronograma(UMBRAL_INICIAL))
      } catch (e) {
        setError(e instanceof Error ? e.message : String(e))
      }
    }
    cargarDatos()
  }, [])

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
        </section>
      )}

      {cronograma && (
        <p className="resumen">
          Con un umbral de <strong>{cronograma.umbral}</strong> estudiantes, las{' '}
          <strong>{cronograma.total_materias}</strong> materias necesitan{' '}
          <strong>{cronograma.total_turnos} turnos</strong> para separar los{' '}
          <strong>{cronograma.total_conflictos}</strong> pares en conflicto.
        </p>
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
