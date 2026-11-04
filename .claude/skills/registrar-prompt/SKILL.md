---
name: registrar-prompt
description: Agrega una entrada a prompts_ia.md con un prompt destacado del usuario (para la sección "Uso de IA" del informe). Usar después de cada pedido relevante (código nuevo, corrección de algo que propuso la IA, pregunta conceptual), o cuando el usuario diga "registrá esto" o "anotá el prompt".
---

# Registrar un prompt en prompts_ia.md

El informe del TP exige una sección de uso de IA con prompts útiles, casos en que la IA se equivocó y cómo se detectaron. Este registro es la fuente para escribirla.

## Cuándo registrar

- **Sí:** pedidos que generan o cambian código, correcciones del usuario a algo que propuso la IA, preguntas para entender un concepto o el código, decisiones de diseño.
- **No:** pedidos triviales (instalar algo, renombrar un archivo), confirmaciones, ni preguntas que repiten algo ya registrado.

## Formato de cada entrada

Agregarla antes de la sección "Casos en que la IA se equivocó...", numerada a continuación de la última:

```markdown
## N. Título corto

**Fecha:** DD/MM/AAAA
**Prompt:**
> texto del prompt TAL CUAL lo escribió el usuario (con sus errores de tipeo)

**Resultado:** qué se obtuvo, en una a tres líneas, con enlaces a los archivos creados o modificados.

**Correcciones nuestras:** (solo si hubo) qué cambiaron y por qué.

**Por qué fue útil:** (opcional) una línea.

---
```

## Reglas

- El prompt va **textual**: no corregir ni resumir lo que escribió el usuario.
- Si el usuario corrigió o rechazó algo que propuso la IA, agregar también una fila a la tabla final "Casos en que la IA se equivocó o propuso algo que no queríamos" (Situación | Cómo nos dimos cuenta | Qué hicimos).
- Redactar en primera persona del plural ("le pedimos", "decidimos"), porque el archivo lo firma el grupo.
- No inventar resultados: si algo no se ejecutó o no se probó, decirlo.

## Aviso obligatorio al usuario

Cada vez que se agregue o modifique algo en `prompts_ia.md`, terminar la respuesta con este bloque, bien visible y separado del resto:

```markdown
---

> ## ⚠️ SE ACTUALIZÓ prompts_ia.md
> **Entrada N: Título** ([ver archivo](prompts_ia.md))
> - Qué se agregó: ...
> - **Revisen:** las partes escritas por la IA que conviene ajustar con sus palabras (resultado, correcciones, "por qué fue útil") y si la entrada realmente vale la pena para el informe.
```

Si se agregó una fila a la tabla de errores de la IA, mencionarla también en el aviso.
