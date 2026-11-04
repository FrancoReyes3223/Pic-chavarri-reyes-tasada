---
name: preparar-defensa
description: Explica una parte del código del TP como para la defensa oral y hace preguntas de práctica. Usar cuando el usuario pida "explicame X", "qué me pueden preguntar de Y" o quiera practicar la defensa.
---

# Preparar la defensa oral

En la defensa los profes preguntan sobre cualquier parte del trabajo. El objetivo es que el usuario **entienda** el código, no darle un texto para memorizar.

## Al explicar

1. Leer el archivo o la función pedida antes de explicar; no explicar de memoria.
2. Explicar en este orden:
   - **Qué problema resuelve** dentro del pipeline (datos → modelo → grafo → coloreo → web).
   - **Cómo lo hace**, paso a paso, citando líneas como `archivo:línea`.
   - **Por qué así** y no de otra forma: la decisión de diseño y su alternativa.
3. Relacionarlo con los conceptos de clase cuando aplique: train/test, overfitting, métricas MAE/RMSE/R², escalado, coloreo de grafos, número cromático.
4. Usar lenguaje simple y ejemplos concretos con los datos del TP (por ejemplo, "Bases de Datos y Sistemas Operativos son del mismo año de Sistemas...").

## Preguntas de práctica

Al final, proponer 3 preguntas del estilo de una defensa sobre ese tema y esperar la respuesta del usuario antes de corregirla. Ejemplos:

- ¿Por qué el greedy no garantiza la cantidad mínima de turnos?
- ¿Qué pasa con el grafo y la cantidad de turnos si bajan el umbral?
- ¿Por qué la feature histórica usa solo períodos anteriores?
- ¿Cómo saben que el modelo no está sobreajustando?
- ¿Qué reglas del dataset sintético descubrió el modelo?
