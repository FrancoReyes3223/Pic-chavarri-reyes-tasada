// Página para cualquier dirección que no existe.
import { Link } from 'react-router-dom'

function NoEncontrada() {
  return (
    <>
      <h1 className="titulo-pagina">Página no encontrada</h1>
      <p className="bajada">
        Esta dirección no existe. Volvé al <Link to="/">inicio</Link>.
      </p>
    </>
  )
}

export default NoEncontrada
