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

---

## 3. Configuración de Claude Code para el proyecto

**Fecha:** 03/11/2026
**Prompt:**
> ahora lo ideal seria crear un .claude en el que hayan skills, contexto del proyecto, etc

**Resultado:** creó la carpeta [`.claude/`](.claude/) con:
- [`CLAUDE.md`](.claude/CLAUDE.md): contexto del proyecto, decisiones ya tomadas, estructura, cómo correr y convenciones.
- Tres skills: `registrar-prompt` (mantiene este archivo), `regenerar-dataset` y `preparar-defensa`.

**Por qué fue útil:** los tres integrantes trabajamos con el mismo contexto, y la IA no vuelve a proponer cosas que ya descartamos (por ejemplo, clasificación).

---

## 4. Escalado para KNN y selección de modelos con cross-validation

**Fecha:** 04/11/2026
**Prompt:**
> No me terminan de cuadrar los resultados de KNN, dan demasiado mal aunque el modelo deberia funcionar correctamente para el contexto, puede ser que no esten escaladas las features?

**Resultado:** explicó que el árbol no era realmente mejor: KNN usa distancias y estaba en desventaja porque las features no estaban escaladas (`inscriptos_prom` va de 35 a 219 y `mismo_anio` vale 0 o 1). Cambió [`backend/entrenamiento.py`](backend/entrenamiento.py):
- KNN ahora va en un pipeline con `StandardScaler`.
- Los hiperparámetros (`max_depth` del árbol, `k` de KNN) y el modelo ganador se eligen con `GridSearchCV` sobre train, usando `GroupKFold` por período. Antes se elegían mirando el test.
- El test se usa una sola vez, al final.
- El gráfico de overfitting ahora compara train contra validación.

Resultado: gana KNN con k=15 (MAE CV 0.946; MAE test 1.021, R² 0.886). El árbol queda con `max_depth=5` (MAE test 1.038) y la regresión lineal con MAE test 1.069.

**Correcciones nuestras:** el script original elegía el mejor modelo y la mejor profundidad con el MAE de test, y no escalaba las features para KNN.

**Por qué fue útil:** el MAE de test que reportamos ahora es una estimación honesta, escalando las features de forma justa para KNN y porque el test no participó en ninguna decisión.

## 5. Creación de la API FastAPI con datos mock y desacople

**Fecha:** 05/11/2026
**Prompt:**
> ### 3. OBJETIVO INMEDIATO (FASE DE DESACOPLE PARA INTEGRANTE B)
> Escribir el archivo `backend/app/main.py` para la API con FastAPI.
> Dado que el Integrante A todavía está desarrollando `grafo.py` y `coloreo.py`, la API debe:
> 1. Proveer datos de prueba estructurados y realistas (*mock data*) para que el Integrante C (Frontend) pueda empezar a consumir la API y renderizar el grafo y el cronograma hoy mismo sin bloquearse.
> 2. Dejar la arquitectura preparada con una bandera o función puente (`MODO_MOCK = True / False`) para que, apenas el Integrante A entregue las funciones reales `construir_grafo(umbral)` y `colorear_cronograma(grafo)`, la integración se haga en 2 líneas de código.
> 
> ### 4. REQUERIMIENTOS TÉCNICOS PARA `backend/app/main.py`
> 1. **Framework:** FastAPI con tipado estricto y modelos Pydantic para las respuestas.
> 2. **CORS:** Configurar `CORSMiddleware` permitiendo orígenes locales de desarrollo (`http://localhost:5173`, `http://127.0.0.1:5173` de Vite) y comodín `*` para métodos y headers.
> 3. **Endpoint `GET /`:** Health check simple que devuelva estado del servicio y versión.
> 4. **Endpoint `GET /metricas`:** Devuelve las métricas de comparación de los 3 modelos evaluados y cuál fue el seleccionado, para que el frontend pueda mostrarlas en una pestaña/tarjeta informativa.
> 5. **Endpoint `GET /cronograma`:**
>    - Parámetro Query: `umbral: float = Query(5.0, ge=0.0, description="Umbral mínimo de estudiantes para considerar conflicto")`.
>    - Respuesta JSON: Contrato acordado para el Frontend con estructura limpia (`umbral`, `total_materias`, `total_turnos`, `total_conflictos`, `turnos`, `grafo` con `nodos` y `aristas`).
>    - Si `MODO_MOCK` está activo: cargar materias reales desde `backend/data/materias.csv`, simular asignación coherente de turnos y aristas de conflicto coherentes con el umbral.
>    - Si `MODO_MOCK` está desactivado: importar y llamar a `app.grafo` y `app.coloreo`.
> 
> ### 5. CONVENCIONES Y ESTILO
> - Código, nombres de variables y comentarios en español, sin tildes en identificadores.
> - Manejo de rutas relativas con `pathlib.Path` para funcionar desde cualquier directorio.
> - Instrucciones para correrlo con `uvicorn`.

**Resultado:** generó [`backend/app/main.py`](backend/app/main.py) con FastAPI:
- CORS habilitado para el puerto de desarrollo de Vite (`5173`) y cualquier origen local.
- Endpoints `GET /` (health check), `GET /metricas` (métricas de comparación de los 3 modelos) y `GET /cronograma` con el contrato JSON acordado.
- Modo mock realista basado en [`backend/data/materias.csv`](backend/data/materias.csv) y [`backend/data/pares_proximo_periodo.csv`](backend/data/pares_proximo_periodo.csv) que colorea mediante algoritmo voraz para que el frontend ya pueda interactuar con el slider y ver cambios de turnos.
- Bandera `MODO_MOCK = True` preparada para conectar `grafo.py` y `coloreo.py` en cuanto el integrante A los finalice.

**Por qué fue útil:** permitió al integrante B dejar la API operativa y al integrante C comenzar a trabajar en el frontend sin tener que esperar a que se termine la lógica de grafos.



## 6. Cómo construir un grafo y qué librerías usar

**Fecha:** 05/11/2026
**Prompt:**
> Tengo que empezar con la construccion del grafo basado en las predicciones del modelo, recomendame librerias y ayudame a construir el grafo, no modifiques codigo.

**Resultado:** explicó para qué sirve cada librería (networkx, pandas, joblib y pathlib) y los pasos para construir el grafo: definir nodos, aristas y pesos, predecir, agregar todos los nodos, filtrar por umbral, agregar las aristas y comprobar el resultado. No cambió código.


---

## 7. Reemplazo de comprensiones por bucles comunes

**Fecha:** 06/11/2026
**Prompt:**
> no vimos compresiones, asi que intenta evitar esa sintaxis en todos los lados que puedas

**Resultado:** la IA reemplazó por bucles `for` las 14 comprensiones y expresiones generadoras que había en [`coloreo.py`](backend/app/coloreo.py), [`main.py`](backend/app/main.py) y [`generar_dataset.py`](backend/data/generar_dataset.py), y sacó una variable sin uso de `main.py`. Comparamos las salidas del cronograma real, del mock y del coloreo antes y después, y regeneramos el dataset: todo dio idéntico.

**Correcciones nuestras:** le pedimos evitar una sintaxis que no vimos en clase, para poder explicar cada línea en la defensa.

---

## 8. Proyecto base del frontend y conexión con la API

**Fecha:** 06/11/2026
**Prompt:**
> empezamos con el paso 1 asi tenemos el frontend y la conexion con la API

**Resultado:** creó el proyecto [`frontend/`](frontend/) con Vite + React + TypeScript y sacó los archivos de ejemplo de la plantilla:
- [`frontend/src/api.ts`](frontend/src/api.ts): los tipos del JSON (copiados de los modelos Pydantic de `main.py`) y las funciones que llaman a `/`, `/cronograma` y `/metricas`.
- [`frontend/src/App.tsx`](frontend/src/App.tsx): una página mínima que muestra si la API responde (y si está en modo mock) y un resumen del cronograma para umbral 5. Si la API no está levantada, explica cómo levantarla.
- [`frontend/src/index.css`](frontend/src/index.css): paleta neutra con el color reservado para los turnos, tipografía Archivo y modo oscuro.
- Sección del frontend en el [`README.md`](README.md).

Lo probamos con la API en modo mock y apagándola, en escritorio y en celular.

**Correcciones nuestras:** antes de empezar decidimos usar el formato JSON que devuelve hoy `/cronograma` y no el que figuraba como acordado en `CLAUDE.md`, que no coincidía con la API.

**Por qué fue útil:** confirma que el frontend y el backend se comunican antes de armar el slider, el cronograma y el grafo.

---

## 9. Grafo de conflictos coloreado por turno

**Fecha:** 06/11/2026
**Prompt:**
> Vamos con el paso 3: el grafo de conflictos en el frontend.
> Cada materia tiene que ser un nodo pintado con el color de su turno (el mismo que usa la grilla del cronograma), y cada arista une dos materias en conflicto. Si se puede, que el grosor de la arista muestre el peso, o sea cuántos estudiantes afectados predice el modelo.
> El grafo se tiene que actualizar cuando muevo el slider de umbral, y al pasar el mouse por un nodo quiero ver el nombre de la materia y su turno.
> Antes de programar, mostrame 2 o 3 librerías para dibujarlo con sus ventajas y desventajas, y elegimos juntos. Quiero algo simple

**Resultado:** comparó tres opciones: un SVG dibujado a mano (sin librería), `react-force-graph-2d` y Cytoscape.js. Recomendó el SVG propio por ser el más fácil de explicar; nosotros elegimos `react-force-graph-2d`. Con eso creó [`GrafoConflictos.tsx`](frontend/src/componentes/GrafoConflictos.tsx):
- Los nodos se ubican con una simulación de fuerzas (las aristas atraen, los nodos se repelen), así las materias con muchos conflictos entre sí quedan cerca.
- Cada nodo usa el color de su turno, el mismo de la grilla; del turno 9 en adelante, con rayas.
- El grosor de cada arista es proporcional a los estudiantes afectados que predice el modelo.
- Al pasar el mouse por un nodo se ve la materia, su turno, carrera, año y cantidad de conflictos.
- Al mover el slider, las materias arrancan desde la posición anterior para que el grafo no se desarme.

Lo probamos con umbral 1 (14 turnos, 623 conflictos), 5 y 30 (3 turnos, casi todas las materias sueltas), en escritorio, celular y modo oscuro.

**Correcciones nuestras:** elegimos `react-force-graph-2d` en lugar del SVG propio que recomendaba.

**Por qué fue útil:** se ve el grafo coloreado que arma el backend y cómo cambia con el umbral, que es lo central del TP.

---

## 10. Una página por sección en el frontend

**Fecha:** 07/11/2026
**Prompt:**
> quiero hacer muchos cambios del frontend. para empezar cada una de las secciones tiene que ser un /xxx nuevo (/cronograma, /grafo (con el umbral de conflicto ahi tambien) /modelo (con la explicacion del modelo), etc)

**Resultado:** separó el frontend en páginas con `react-router-dom`: `/` (inicio con los tres pasos del sistema), `/grafo` (slider de umbral y grafo), `/cronograma` (grilla de turnos), `/modelo` (qué predice, cómo se evaluó y la tabla de métricas) y una página para direcciones que no existen. Agregó una barra de navegación. El umbral se guarda en [`App.tsx`](frontend/src/App.tsx), así el que se elige en `/grafo` es el mismo que usa `/cronograma`. Cada página está en [`frontend/src/paginas/`](frontend/src/paginas/). Lo comprobamos con capturas de cada página en escritorio.

---

## Casos en que la IA se equivocó o propuso algo que no queríamos

| Situación | Cómo nos dimos cuenta | Qué hicimos |
|---|---|---|
| Agregó la variable de clasificación `hubo_conflicto` aunque íbamos a usar regresión | Revisando el código generado | Le pedimos que la eliminara |
| Metió el entrenamiento de modelos dentro del generador de datos (`--verificar`) | Nos dio resultados para determinar el under/overfitting aunque unicamnente habiamos generado la database | Lo sacamos y lo dejamos para cuando implementemos y entrenemos los modelos reales |
| Asumió el uso de Jupyter Notebook (.ipynb) agregando dependencias innecesarias | Cuestionando la necesidad técnica del notebook | Reemplazamos el plan por el script `entrenamiento.py` directo |
| Usó comprensiones, una sintaxis que no vimos en clase | Revisando `colorear_grafo`: un `for` y un `if` dentro de las llaves no parecían hacer nada | Le pedimos reemplazarlas por bucles comunes en todo el backend |
