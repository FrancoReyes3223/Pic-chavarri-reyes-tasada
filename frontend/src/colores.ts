// Color de cada turno. Lo usan el cronograma y, más adelante, el grafo.
//
// Tenemos 8 colores bien distinguibles entre sí (definidos en index.css como
// --turno-1 a --turno-8, con una versión para modo oscuro). Con umbrales bajos
// pueden hacer falta más de 8 turnos: del 9 en adelante se repite el color
// pero con rayas, así dos turnos nunca se ven iguales.
// Igual el número del turno siempre aparece escrito: el color ayuda, no es lo único.

const CANTIDAD_DE_COLORES = 8

// Devuelve el color del turno (los turnos empiezan en 1).
export function colorDelTurno(turno: number): string {
  const posicion = ((turno - 1) % CANTIDAD_DE_COLORES) + 1
  return `var(--turno-${posicion})`
}

// true si el turno lleva rayas (turnos 9 a 16, 25 a 32, ...).
export function turnoRayado(turno: number): boolean {
  const vuelta = Math.floor((turno - 1) / CANTIDAD_DE_COLORES)
  return vuelta % 2 === 1
}
