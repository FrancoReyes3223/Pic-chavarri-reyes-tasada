---
name: regenerar-dataset
description: Regenera los CSV del dataset sintético con backend/data/generar_dataset.py y revisa que el resultado tenga sentido. Usar cuando se cambien reglas o parámetros del generador, o cuando el usuario pida regenerar o revisar el dataset.
---

# Regenerar el dataset

## Pasos

1. Si hace falta, crear el entorno: `cd backend && python -m venv .venv && .venv/Scripts/python -m pip install -r requirements.txt`.
2. Correr desde `backend/`:
   ```
   PYTHONIOENCODING=utf-8 .venv/Scripts/python data/generar_dataset.py
   ```
3. Revisar el resumen que imprime y compararlo con la referencia de abajo (semilla 42).

## Referencia actual (seed 42)

- 7920 filas históricas (8 períodos × 990 pares) y 45 materias.
- Afectados: media ≈ 2.2, mediana 0, máximo ≈ 67. La mediana en 0 es esperable: la mayoría de los pares casi no comparten alumnos.
- Correlación de `cant_estudiantes_compartidos_historico` con el target ≈ 0.93.

## Si se cambiaron reglas

- Actualizar el docstring del generador (sección REGLAS) para que coincida con el código. Es lo que se cita en el informe.
- Si cambian las cantidades de arriba, actualizar esta referencia y la sección "Estructura" de `.claude/CLAUDE.md`.
- No meter entrenamiento de modelos en el generador: eso va en el notebook.
- Mantener la regla de no fuga de información: las features solo pueden usar períodos **anteriores**.
