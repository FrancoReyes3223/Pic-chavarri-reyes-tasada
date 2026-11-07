"""
Coloreo greedy del grafo de conflictos: cada color es un turno de examen.

Dos materias unidas por una arista nunca reciben el mismo turno. Entre los turnos
permitidos, cada materia va al que tiene menos materias, así los turnos quedan parejos.
El greedy no garantiza la menor cantidad de turnos posible, porque nunca cambia una
decisión ya tomada.
"""

import networkx as nx


def ordenar_materias(grafo_conflictos):
    """Ordena las materias de mayor a menor cantidad de estudiantes en conflicto (grado ponderado)."""
    # El signo menos ordena de mayor a menor. Los empates se resuelven por id,
    # así el mismo umbral siempre da el mismo cronograma.
    return sorted(
        grafo_conflictos.nodes,
        key=lambda materia_id: (-grafo_conflictos.degree(materia_id, weight='weight'), materia_id),
    )


def colorear_grafo(grafo_conflictos):
    """
    Asigna a cada materia, de los turnos que no usa ninguna vecina, el que tiene menos materias.
    Si todos los turnos tienen alguna vecina, abre uno nuevo. Devuelve {materia_id: turno}.
    """
    turno_por_materia = {}
    materias_por_turno = []  # materias_por_turno[t] = cuántas materias tiene el turno t

    for materia_id in ordenar_materias(grafo_conflictos):
        turnos_ocupados = set()
        for vecina in grafo_conflictos.neighbors(materia_id):
            # Las vecinas que todavía no tienen turno no restringen a esta materia.
            if vecina in turno_por_materia:
                turnos_ocupados.add(turno_por_materia[vecina])

        # De los turnos que ya existen y están libres, elegimos el que tiene menos materias.
        # Con "<" (y no "<="), si dos empatan queda el de número más bajo.
        turno_elegido = None
        for turno in range(len(materias_por_turno)):
            if turno in turnos_ocupados:
                continue
            if turno_elegido is None or materias_por_turno[turno] < materias_por_turno[turno_elegido]:
                turno_elegido = turno

        if turno_elegido is None:
            # Todos los turnos tienen alguna vecina: hace falta un turno nuevo.
            turno_elegido = len(materias_por_turno)
            materias_por_turno.append(0)

        turno_por_materia[materia_id] = turno_elegido
        materias_por_turno[turno_elegido] += 1

    return turno_por_materia


def verificar_coloreo(grafo_conflictos, turno_por_materia):
    """Devuelve True si todas las materias tienen turno y ninguna arista une dos materias del mismo turno."""
    for materia_id in grafo_conflictos.nodes:
        if materia_id not in turno_por_materia:
            return False

    for materia_1, materia_2 in grafo_conflictos.edges:
        if turno_por_materia[materia_1] == turno_por_materia[materia_2]:
            return False

    return True


def cantidad_de_turnos(turno_por_materia):
    """Devuelve cuántos turnos distintos usa un coloreo."""
    return len(set(turno_por_materia.values()))


if __name__ == '__main__':
    # Prueba manual: valida el coloreo y lo compara con dos referencias para cada umbral.
    # La clique más grande es el mínimo teórico: sus materias necesitan un turno cada una.
    from grafo import cargar_materias, construir_grafo, predecir_afectados_por_par

    materias = cargar_materias()
    afectados_por_par = predecir_afectados_por_par()

    # "Mas" y "Menos": cuántas materias tienen el turno más cargado y el más vacío.
    print(f'{"Umbral":>8} {"Aristas":>8} {"Turnos":>7} {"Mas":>5} {"Menos":>6} '
          f'{"Clique":>7} {"networkx":>9} {"Valido":>7}')
    for umbral_afectados in [0.5, 1, 2, 3, 5, 8, 10, 15]:
        grafo_conflictos = construir_grafo(materias, afectados_por_par, umbral_afectados)
        turno_por_materia = colorear_grafo(grafo_conflictos)

        clique_mas_grande = 0
        for clique in nx.find_cliques(grafo_conflictos):
            if len(clique) > clique_mas_grande:
                clique_mas_grande = len(clique)

        turnos_networkx = cantidad_de_turnos(nx.greedy_color(grafo_conflictos, strategy='largest_first'))
        es_valido = verificar_coloreo(grafo_conflictos, turno_por_materia)

        materias_por_turno = {}
        for turno in turno_por_materia.values():
            materias_por_turno[turno] = materias_por_turno.get(turno, 0) + 1

        print(f'{umbral_afectados:>8} {grafo_conflictos.number_of_edges():>8} '
              f'{cantidad_de_turnos(turno_por_materia):>7} {max(materias_por_turno.values()):>5} '
              f'{min(materias_por_turno.values()):>6} {clique_mas_grande:>7} '
              f'{turnos_networkx:>9} {str(es_valido):>7}')
