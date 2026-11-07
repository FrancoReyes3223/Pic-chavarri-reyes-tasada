import { useEffect, useState } from 'react'
import { NavLink, Route, Routes } from 'react-router-dom'
import { URL_API, obtenerCronograma, obtenerEstado, obtenerMetricas } from './api'
import type { Cronograma as DatosCronograma, EstadoApi, Metricas } from './api'
import Inicio from './paginas/Inicio'
import NoEncontrada from './paginas/NoEncontrada'
import PaginaCronograma from './paginas/PaginaCronograma'
import PaginaGrafo from './paginas/PaginaGrafo'
import PaginaModelo from './paginas/PaginaModelo'

// Umbral con el que arranca la página (después lo mueven los sliders de /grafo y /cronograma).
const UMBRAL_INICIAL = 5

// Milisegundos que esperamos después de mover el slider antes de pedirle el
// cronograma a la API. Así no mandamos un pedido por cada paso mientras se arrastra.
const ESPERA_SLIDER = 200

// App guarda los datos que comparten las páginas (el umbral y lo que devuelve la API)
// y elige qué página mostrar según la dirección. Como el umbral vive acá y no en
// una página, el slider de /grafo y el de /cronograma muestran y cambian el mismo valor.
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
    <>
      <header className="barra">
        <div className="barra-contenido">
          <NavLink to="/" className="marca">
            Mesas de examen
          </NavLink>
          <nav aria-label="Secciones">
            <ul className="navegacion">
              <li><NavLink to="/grafo">Grafo</NavLink></li>
              <li><NavLink to="/cronograma">Cronograma</NavLink></li>
              <li><NavLink to="/modelo">Modelo</NavLink></li>
            </ul>
          </nav>
          <LineaDeEstado estadoApi={estadoApi} error={error} />
        </div>
      </header>

      <main className="pagina">
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

        {/* Cada Route asocia una dirección con una página. path="*" atrapa cualquier otra. */}
        <Routes>
          <Route path="/" element={<Inicio />} />
          {/* Las tres direcciones del grafo usan la misma página; solo cambia cómo se dibuja. */}
          <Route
            path="/grafo"
            element={
              <PaginaGrafo
                vista="fuerzas"
                cronograma={cronograma}
                umbral={umbral}
                alCambiarUmbral={setUmbral}
                cargando={cargando}
              />
            }
          />
          <Route
            path="/grafo/grilla"
            element={
              <PaginaGrafo
                vista="grilla"
                cronograma={cronograma}
                umbral={umbral}
                alCambiarUmbral={setUmbral}
                cargando={cargando}
              />
            }
          />
          <Route
            path="/grafo/turnos"
            element={
              <PaginaGrafo
                vista="turnos"
                cronograma={cronograma}
                umbral={umbral}
                alCambiarUmbral={setUmbral}
                cargando={cargando}
              />
            }
          />
          <Route
            path="/cronograma"
            element={
              <PaginaCronograma
                cronograma={cronograma}
                umbral={umbral}
                alCambiarUmbral={setUmbral}
                cargando={cargando}
              />
            }
          />
          <Route path="/modelo" element={<PaginaModelo metricas={metricas} />} />
          <Route path="*" element={<NoEncontrada />} />
        </Routes>
      </main>
    </>
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
  const origen = estadoApi.modo_mock ? 'datos de prueba' : 'predicciones del modelo'
  return <p className="estado conectado">API conectada, {origen}</p>
}

export default App
