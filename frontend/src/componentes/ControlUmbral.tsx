// Slider para elegir el umbral de conflicto.
// El umbral es la cantidad mínima de estudiantes afectados (según el modelo)
// para que dos materias no puedan ir en el mismo turno.

// Empieza en 1 y no en 0: con umbral 0 todos los pares serían conflicto,
// y la API real lo rechaza.
export const UMBRAL_MINIMO = 1
export const UMBRAL_MAXIMO = 30

interface Props {
  umbral: number
  alCambiar: (nuevoUmbral: number) => void
}

function ControlUmbral({ umbral, alCambiar }: Props) {
  return (
    <div className="control-umbral">
      <label htmlFor="umbral">Umbral de conflicto</label>
      <div className="control-umbral-fila">
        <input
          id="umbral"
          type="range"
          min={UMBRAL_MINIMO}
          max={UMBRAL_MAXIMO}
          step={1}
          value={umbral}
          onChange={(evento) => alCambiar(Number(evento.target.value))}
        />
        <output htmlFor="umbral">{umbral}</output>
      </div>
      <p className="ayuda">
        Dos materias van en turnos distintos si el modelo predice que al menos{' '}
        {umbral} {umbral === 1 ? 'estudiante quiere' : 'estudiantes quieren'} rendir las dos.
        Más bajo: más pares en conflicto y más turnos.
      </p>
    </div>
  )
}

export default ControlUmbral
