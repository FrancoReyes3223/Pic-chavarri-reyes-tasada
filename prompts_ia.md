# Registro de uso de IA

Prompts que nos resultaron útiles durante el TP, con lo que obtuvimos y las correcciones que hicimos.
Sirve como base para la sección "Uso de IA" del informe.

**Herramienta:** Claude Code (modelo Claude Opus 5.5), como extensión de VS Code.

---

## 1. Plan inicial del TP

**Fecha:** 03/11/2026
**Prompt:**
> tengo que empezar el TP del enunciado, mas especificamente el de planificacion de mesas de examen, sobre machine lerning tene de referencia que esto es lo que dimos en clases: https://github.com/AgustinGurvich/Intro-A-ML
> Dame un orden en el que recomiendes encarar las tareas, considerando la fecha de entrega proxima

**Resultado:** leyó el enunciado y el repositorio de la materia. Propuso:
- usar regresión sobre `cant_estudiantes_afectados`;
- generar un dataset sintético con un script;
- una estructura de carpetas para backend y frontend;
- un esquema del coloreo greedy;
- un plan por días hasta la entrega.

**Por qué fue útil:** nos ayudo como esqueleto para empezar el trabajo, marcando bien las tareas y dandole un orden logico.

---

## 2. Generador del dataset sintético

**Fecha:** 03/11/2026
**Prompt:**
> empeza unicamente por crear el generador del dataset, el dataset tiene que tener una cantidad de datos amplia pero no exagerada(algo como 4-5 años, 3-4 materias por año y 2-3 carreras). Lo que el modelo deberia predecir es un porcentaje de coincidencia de alumnos entre un par de materias, basado en su año, carrera en la que se toma dicha materia y otros datos o factores de aleatoriedad que dejo a tu discrecion.
 
**Resultado:** generó [`backend/data/generar_dataset.py`](backend/data/generar_dataset.py) con siete reglas declaradas (R1 a R7):
- un plan de 45 materias;
- inscriptos por año;
- afinidad entre pares;
- ruido Poisson y Binomial;
- una feature histórica que solo usa períodos anteriores, para evitar fuga de información.

**Correcciones nuestras:**
- Incluía también una variable de clasificación (`hubo_conflicto`). Como elegimos regresión, lo eliminamos.



## 4. Configuración de Claude Code para el proyecto

**Fecha:** 03/11/2026
**Prompt:**
> ahora lo ideal seria crear un .claude en el que hayan skills, contexto del proyecto, etc

**Resultado:** creó la carpeta [`.claude/`](.claude/) con:
- [`CLAUDE.md`](.claude/CLAUDE.md): contexto del proyecto, decisiones ya tomadas, estructura, cómo correr y convenciones.
- Tres skills: `registrar-prompt` (mantiene este archivo), `regenerar-dataset` y `preparar-defensa`.

**Por qué fue útil:** los dos integrantes trabajamos con el mismo contexto, y la IA no vuelve a proponer cosas que ya descartamos (por ejemplo, clasificación).

---

## Casos en que la IA se equivocó o propuso algo que no queríamos

| Situación | Cómo nos dimos cuenta | Qué hicimos |
|---|---|---|
| Agregó la variable de clasificación `hubo_conflicto` aunque íbamos a usar regresión | Revisando el código generado | Le pedimos que la eliminara |
| Metió el entrenamiento de modelos dentro del generador de datos (`--verificar`) | Nos dio resultados para determinar el under/overfitting aunque unicamnente habiamos generado la database| Lo sacamos y lo dejamos para cuando implementemos y entrenemos los modelos reales|
