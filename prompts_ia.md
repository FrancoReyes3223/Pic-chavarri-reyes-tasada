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

## 5. Migración de notebook a script independiente y entrenamiento de modelos

**Fecha:** 04/11/2026
**Prompt:**
> pero por que usamos cuadernos??? yo pense que eso era por una cuestion didactica que usaba el profesor para impartir las clases, no que es necesario usar un notebook para entrenar?? o me equivoco

**Resultado:** Se acordó prescindir de Jupyter y estructurar todo el flujo de Machine Learning en [`backend/entrenamiento.py`](backend/entrenamiento.py). El script realiza EDA con guardado de histograma, partición temporal (períodos 1-6 train, 7-8 test) y comparación de 3 modelos (`LinearRegression`, `DecisionTreeRegressor`, `KNeighborsRegressor`).

**Correcciones nuestras:**
- Reemplazamos la idea inicial del notebook por un script Python ejecutable desde consola.

**Por qué fue útil:** Simplificó el entorno de desarrollo y dejó el código listo para integrarse directamente con los módulos del backend.

---

## 6. Análisis de overfitting y guardado del modelo ganador

**Fecha:** 04/11/2026
**Prompt:**
> seguimos con el paso de terminar el modelo. asi podemos ya guardar el modelo ganador y seguir avanzando

**Resultado:** agregó al final de [`backend/entrenamiento.py`](backend/entrenamiento.py):
- un análisis de overfitting: entrena el árbol con `max_depth` de 1 a 20 y grafica el MAE de train y test en [`backend/app/overfitting_arbol.png`](backend/app/overfitting_arbol.png);
- el guardado del modelo ganador con `joblib` en `backend/app/modelo.pkl`, junto con su nombre y la lista de features.

Al correrlo: gana el árbol con `max_depth=5` (MAE test 1.038, R² 0.869), muy cerca de la regresión lineal (MAE test 1.069). La profundidad con menor error en test es 4; con `max_depth=20` el MAE de train baja a 0.07 pero el de test sube a 1.27 (overfitting).

**Por qué fue útil:** deja el modelo listo para que el backend lo cargue sin reentrenar, y el gráfico sirve para el informe.

---

## Casos en que la IA se equivocó o propuso algo que no queríamos

| Situación | Cómo nos dimos cuenta | Qué hicimos |
|---|---|---|
| Agregó la variable de clasificación `hubo_conflicto` aunque íbamos a usar regresión | Revisando el código generado | Le pedimos que la eliminara |
| Metió el entrenamiento de modelos dentro del generador de datos (`--verificar`) | Nos dio resultados para determinar el under/overfitting aunque unicamnente habiamos generado la database | Lo sacamos y lo dejamos para cuando implementemos y entrenemos los modelos reales |
| Asumió el uso de Jupyter Notebook (.ipynb) agregando dependencias innecesarias | Cuestionando la necesidad técnica del notebook | Reemplazamos el plan por el script `entrenamiento.py` directo |
