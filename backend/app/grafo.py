"""
Construcción del grafo de conflictos a partir de las predicciones del modelo.

    Nodo:   materia que se rinde en el período.
    Arista: par de materias con estudiantes afectados predichos >= umbral_afectados.
    Peso:   cantidad de estudiantes afectados que predice el modelo.

Predecir se hace una sola vez; construir el grafo, cada vez que cambia el umbral.
"""

from pathlib import Path

import joblib
import networkx as nx
import pandas as pd

CARPETA_BACKEND = Path(__file__).resolve().parent.parent
RUTA_MODELO = CARPETA_BACKEND / 'app' / 'modelo.pkl'
RUTA_MATERIAS = CARPETA_BACKEND / 'data' / 'materias.csv'
RUTA_PARES = CARPETA_BACKEND / 'data' / 'pares_proximo_periodo.csv'


def cargar_materias():
    """Devuelve el catálogo de materias (materia_id, nombre, carrera, anio)."""
    # Devuelve un DataFrame (tabla de pandas).
    return pd.read_csv(RUTA_MATERIAS)


def cargar_modelo():
    """Devuelve el modelo entrenado y la lista de features en el orden con el que se entrenó."""
    # Devuelve una tupla (Pipeline de sklearn, lista de str).
    archivo_modelo = joblib.load(RUTA_MODELO)  # diccionario {'modelo', 'nombre', 'features'}
    return archivo_modelo['modelo'], archivo_modelo['features']


def predecir_afectados_por_par():
    """Predice cuántos estudiantes se verían afectados en cada par de materias del próximo período."""
    modelo, nombres_features = cargar_modelo()  # modelo: Pipeline. nombres_features: lista de str.
    pares_proximo = pd.read_csv(RUTA_PARES)  # DataFrame: una fila por par de materias

    # El modelo necesita las columnas en el mismo orden con el que se entrenó.
    afectados_por_par = pares_proximo[['materia_id_1', 'materia_id_2']].copy()  # DataFrame
    afectados_por_par['afectados_predichos'] = modelo.predict(pares_proximo[nombres_features])
    return afectados_por_par


def agregar_materias(grafo_conflictos, materias):
    """Agrega cada materia como un nodo, con su nombre, carrera y año."""
    # grafo_conflictos: grafo de networkx (nx.Graph). materias: DataFrame.
    for materia in materias.itertuples():  # materia: una fila, se accede con materia.nombre
        grafo_conflictos.add_node(
            materia.materia_id,
            nombre=materia.nombre,
            carrera=materia.carrera,
            anio=materia.anio,
        )


def filtrar_pares_en_conflicto(afectados_por_par, umbral_afectados):
    """Devuelve solo los pares cuyos afectados predichos alcanzan el umbral."""
    # afectados_por_par: DataFrame. umbral_afectados: float. Devuelve un DataFrame.
    cumple_umbral = afectados_por_par['afectados_predichos'] >= umbral_afectados  # Serie de bool, uno por fila
    return afectados_por_par[cumple_umbral]


def agregar_conflictos(grafo_conflictos, pares_en_conflicto):
    """Agrega una arista por cada par en conflicto; el peso es la cantidad de afectados predichos."""
    # grafo_conflictos: nx.Graph. pares_en_conflicto: DataFrame.
    for par_materias in pares_en_conflicto.itertuples():  # par_materias: una fila del DataFrame
        grafo_conflictos.add_edge(
            par_materias.materia_id_1,
            par_materias.materia_id_2,
            weight=float(par_materias.afectados_predichos),
        )


def construir_grafo(materias, afectados_por_par, umbral_afectados):
    """Une con una arista los pares de materias cuyos afectados predichos alcanzan el umbral."""
    # materias y afectados_por_par: DataFrame. umbral_afectados: float. Devuelve un nx.Graph.
    if umbral_afectados <= 0:
        # Con umbral 0, un par con 0 afectados predichos también sería un conflicto.
        raise ValueError('El umbral de afectados tiene que ser mayor a 0')

    grafo_conflictos = nx.Graph()  # nodos: ids de materias (str). Aristas con 'weight' (float).

    # Primero todas las materias, también las que no tengan ningún conflicto:
    # esas quedan como nodos aislados y igual necesitan un turno.
    agregar_materias(grafo_conflictos, materias)

    pares_en_conflicto = filtrar_pares_en_conflicto(afectados_por_par, umbral_afectados)  # DataFrame
    agregar_conflictos(grafo_conflictos, pares_en_conflicto)

    return grafo_conflictos


if __name__ == '__main__':
    # Prueba manual: cómo cambia el grafo según el umbral.
    materias = cargar_materias()
    afectados_por_par = predecir_afectados_por_par()

    print(f'{"Umbral":>8} {"Nodos":>7} {"Aristas":>8} {"Aisladas":>9}')
    for umbral_afectados in [0.5, 1, 2, 3, 5, 8, 10, 15]:
        grafo_conflictos = construir_grafo(materias, afectados_por_par, umbral_afectados)
        materias_aisladas = nx.number_of_isolates(grafo_conflictos)
        print(f'{umbral_afectados:>8} {grafo_conflictos.number_of_nodes():>7} '
              f'{grafo_conflictos.number_of_edges():>8} {materias_aisladas:>9}')
