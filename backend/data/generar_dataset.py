"""
Generador del dataset sintético — Planificación de mesas de examen.

Uso:
    python generar_dataset.py               # genera los CSV en esta carpeta
    python generar_dataset.py --seed 7      # otra semilla (mismas reglas, otros datos)

Salidas:
    materias.csv                catálogo de materias (= nodos del grafo)
    pares_historico.csv         una fila por par de materias y por período (para entrenar)
    pares_proximo_periodo.csv   features del período a planificar, SIN target (para predecir
                                y armar el grafo de conflictos)

-------------------------------------------------------------------------------
REGLAS DE GENERACIÓN
-------------------------------------------------------------------------------
R1. Plan de estudios: 3 carreras x 5 años x 3 materias = 45 materias (990 pares).

R2. Inscriptos de cada materia en cada período:
        inscriptos = base_por_año x tamaño_materia x variación_período
    - base_por_año: 160, 120, 90, 70, 55 (años 1 a 5: la matrícula cae con los años)
    - tamaño_materia ~ Uniforme(0.7, 1.3), fijo para cada materia
    - variación_período ~ Normal(1, 0.10), cambia en cada período

R3. Afinidad del par (qué fracción de estudiantes comparten), según la relación:
        misma carrera, mismo año ............. 0.40
        misma carrera, 1 año de diferencia ... 0.15
        misma carrera, 2 años de diferencia .. 0.05
        misma carrera, 3+ años ............... 0.02
        distinta carrera, mismo año 1 o 2 .... 0.12  (ciclo básico común)
        distinta carrera, mismo año 3+ ....... 0.03
        distinta carrera, distinto año ....... 0.01
    multiplicada por un efecto propio del par ~ LogNormal(0, 0.25), fijo en el tiempo
    (hay pares que, por razones no observadas, comparten más o menos alumnos).

R4. Estudiantes compartidos en un período:
        compartidos ~ Poisson(afinidad x min(inscriptos_1, inscriptos_2))

R5. VARIABLE A PREDECIR (regresión): cuántos de esos compartidos quieren rendir ambas
    en el mismo período:
        cant_estudiantes_afectados ~ Binomial(compartidos, p)
        p = 0.55 si son del mismo año, 0.35 si no.

R6. Feature histórica: cant_estudiantes_compartidos_historico es el promedio de
    `compartidos` en los 3 períodos ANTERIORES. Los primeros 3 períodos simulados
    solo se usan como historia y no aparecen en el dataset.

En resumen, lo que el modelo debería descubrir es:
    afectados ≈ p(mismo_anio) x compartidos_historico
-------------------------------------------------------------------------------
POR QUÉ NO DEBERÍA DAR OVERFITTING NI UNDERFITTING
-------------------------------------------------------------------------------
- Hay señal: el target depende de las features de forma clara (R5 + R6), así que un
  modelo razonable aprende la relación (no hay underfitting).
- Hay ruido irreducible (Poisson, Binomial y variación de inscriptos): ningún modelo
  puede acertar perfecto. Un árbol sin límite de profundidad va a memorizar ese ruido
  (train >> test). Eso es overfitting del MODELO y se corrige con max_depth o
  min_samples_leaf, no cambiando el dataset.
- Sin fuga de información (leakage): las features usan solo información previa al
  período (promedios históricos). Los `compartidos` del propio período NO se exportan.
- Volumen: ~7900 filas para ~7 features.
- Las columnas materia_id_* son identificadores. NO se usan como features.
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

# ----------------------------------------------------------------------------- parámetros
SEED = 42
N_PERIODOS = 8                 # períodos que salen en pares_historico.csv
VENTANA_HISTORIA = 3           # R6
INSCRIPTOS_BASE_POR_ANIO = {1: 160, 2: 120, 3: 90, 4: 70, 5: 55}   # R2
TAMANIO_MATERIA = (0.7, 1.3)                                       # R2
VARIACION_INSCRIPTOS = 0.10                                        # R2
DISPERSION_EFECTO_PAR = 0.25                                       # R3
PROB_RENDIR_MISMO_ANIO = 0.55                                      # R5
PROB_RENDIR_DISTINTO_ANIO = 0.35                                   # R5

PLAN = {
    "Sistemas": [
        ["Análisis Matemático I", "Álgebra y Geometría Analítica", "Algoritmos y Estructuras de Datos"],
        ["Análisis Matemático II", "Paradigmas de Programación", "Arquitectura de Computadoras"],
        ["Sistemas Operativos", "Bases de Datos", "Probabilidad y Estadística"],
        ["Redes de Datos", "Ingeniería de Software", "Teoría de la Computación"],
        ["Inteligencia Artificial", "Seguridad Informática", "Proyecto Final (Sistemas)"],
    ],
    "Industrial": [
        ["Física I", "Química General", "Sistemas de Representación"],
        ["Física II", "Termodinámica", "Economía General"],
        ["Investigación Operativa", "Resistencia de Materiales", "Costos Industriales"],
        ["Procesos Industriales", "Logística", "Higiene y Seguridad"],
        ["Gestión de la Calidad", "Planificación de la Producción", "Proyecto Final (Industrial)"],
    ],
    "Civil": [
        ["Introducción a la Ingeniería Civil", "Geología Aplicada", "Dibujo Técnico"],
        ["Estabilidad I", "Tecnología de los Materiales", "Topografía"],
        ["Estabilidad II", "Hidráulica", "Mecánica de Suelos"],
        ["Hormigón Armado", "Vías de Comunicación", "Instalaciones Sanitarias"],
        ["Estructuras Metálicas", "Obras Hidráulicas", "Proyecto Final (Civil)"],
    ],
}

FEATURES = [
    "cant_estudiantes_compartidos_historico",
    "mismo_anio",
    "misma_carrera",
    "diferencia_anios",
    "anio_min",
    "inscriptos_prom_1",
    "inscriptos_prom_2",
]


# ----------------------------------------------------------------------------- R1
def crear_materias(rng):
    filas = []
    for carrera, anios in PLAN.items():
        for anio, nombres in enumerate(anios, start=1):
            for nombre in nombres:
                filas.append({"nombre": nombre, "carrera": carrera, "anio": anio})
    materias = pd.DataFrame(filas)
    ids_materias = []
    for i in range(len(materias)):
        ids_materias.append(f"M{i + 1:02d}")
    materias.insert(0, "materia_id", ids_materias)
    materias["tamanio"] = rng.uniform(*TAMANIO_MATERIA, size=len(materias))
    return materias


# ----------------------------------------------------------------------------- R2
def simular_inscriptos(materias, n_total, rng):
    base = materias["anio"].map(INSCRIPTOS_BASE_POR_ANIO).to_numpy() * materias["tamanio"].to_numpy()
    variacion = rng.normal(1.0, VARIACION_INSCRIPTOS, size=(n_total, len(materias)))
    return np.maximum(5, np.round(base * variacion)).astype(int)   # forma (períodos, materias)


# ----------------------------------------------------------------------------- R3
def afinidad_base(misma_carrera, dif, anio_min):
    return np.select(
        [
            misma_carrera & (dif == 0),
            misma_carrera & (dif == 1),
            misma_carrera & (dif == 2),
            misma_carrera,
            ~misma_carrera & (dif == 0) & (anio_min <= 2),
            ~misma_carrera & (dif == 0),
        ],
        [0.40, 0.15, 0.05, 0.02, 0.12, 0.03],
        default=0.01,
    )


def generar(seed=SEED):
    rng = np.random.default_rng(seed)
    materias = crear_materias(rng)
    n_total = VENTANA_HISTORIA + N_PERIODOS + 1          # historia + dataset + próximo período
    insc = simular_inscriptos(materias, n_total, rng)

    # todos los pares i < j
    i, j = np.triu_indices(len(materias), k=1)
    anio = materias["anio"].to_numpy()
    carrera = materias["carrera"].to_numpy()
    misma_carrera = carrera[i] == carrera[j]
    dif = np.abs(anio[i] - anio[j])
    anio_min = np.minimum(anio[i], anio[j])
    mismo_anio = dif == 0

    efecto_par = rng.lognormal(0.0, DISPERSION_EFECTO_PAR, size=len(i))
    afinidad = np.clip(afinidad_base(misma_carrera, dif, anio_min) * efecto_par, 0, 0.9)
    p_rendir = np.where(mismo_anio, PROB_RENDIR_MISMO_ANIO, PROB_RENDIR_DISTINTO_ANIO)

    # R4: compartidos por período
    min_insc = np.minimum(insc[:, i], insc[:, j])                    # (períodos, pares)
    compartidos = np.minimum(rng.poisson(afinidad * min_insc), min_insc)

    base_cols = pd.DataFrame({
        "materia_id_1": materias["materia_id"].to_numpy()[i],
        "materia_id_2": materias["materia_id"].to_numpy()[j],
        "mismo_anio": mismo_anio.astype(int),
        "misma_carrera": misma_carrera.astype(int),
        "diferencia_anios": dif,
        "anio_min": anio_min,
    })

    historico, proximo = [], None
    for t in range(VENTANA_HISTORIA, n_total):
        ventana = slice(t - VENTANA_HISTORIA, t)                     # R6: solo el pasado
        df = base_cols.copy()
        df.insert(0, "periodo", t - VENTANA_HISTORIA + 1)
        df["inscriptos_prom_1"] = insc[ventana, i].mean(axis=0).round(1)
        df["inscriptos_prom_2"] = insc[ventana, j].mean(axis=0).round(1)
        df["cant_estudiantes_compartidos_historico"] = compartidos[ventana].mean(axis=0).round(2)

        if t == n_total - 1:                                         # período a planificar
            proximo = df
            continue

        df["cant_estudiantes_afectados"] = rng.binomial(compartidos[t], p_rendir)   # R5
        historico.append(df)

    return materias.drop(columns="tamanio"), pd.concat(historico, ignore_index=True), proximo


# ----------------------------------------------------------------------------- chequeos
def resumir(historico):
    y = historico["cant_estudiantes_afectados"]
    print(f"Filas históricas: {len(historico)}  ({historico['periodo'].nunique()} períodos)")
    print(f"Afectados: media={y.mean():.2f}  mediana={y.median():.0f}  máx={y.max()}")
    corr = historico[FEATURES + ["cant_estudiantes_afectados"]].corr()["cant_estudiantes_afectados"]
    print("Correlación de cada feature con el target:")
    print(corr.drop("cant_estudiantes_afectados").round(3).to_string())


# ----------------------------------------------------------------------------- main
def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--salida", type=Path, default=Path(__file__).parent)
    args = parser.parse_args()

    materias, historico, proximo = generar(args.seed)
    args.salida.mkdir(parents=True, exist_ok=True)
    materias.to_csv(args.salida / "materias.csv", index=False)
    historico.to_csv(args.salida / "pares_historico.csv", index=False)
    proximo.to_csv(args.salida / "pares_proximo_periodo.csv", index=False)
    print(f"CSV generados en {args.salida.resolve()}\n")

    resumir(historico)


if __name__ == "__main__":
    main()
