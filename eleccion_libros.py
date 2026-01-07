import random
from datetime import datetime, timedelta

DIAS_NO_REPETIR = 5


def seleccionar_libro(
    df,
    edad_nina,
    max_duracion=None,
    permitir_interactivo=True
):
    hoy = datetime.now()

    candidatos = df[
        (df["activa"] == True) &
        (df["edad_min"] <= edad_nina) &
        (df["edad_max"] >= edad_nina)
    ]

    if max_duracion:
        candidatos = candidatos[candidatos["duracion_min"] <= max_duracion]

    if not permitir_interactivo:
        candidatos = candidatos[candidatos["interactivo"] == False]

    candidatos = candidatos[
        (candidatos["ultima_lectura"].isna()) |
        (candidatos["ultima_lectura"] < hoy - timedelta(days=DIAS_NO_REPETIR))
    ]

    if candidatos.empty:
        return None

    def peso(row):
        w = 1
        if row["favorito"]:
            w *= 1.5
        if row["veces_leido"] == 0:
            w *= 1.4
        if row["interactivo"]:
            w *= 1.2
        return w

    pesos = candidatos.apply(peso, axis=1)

    elegido = random.choices(
        list(candidatos.index),
        weights=pesos,
        k=1
    )[0]

    return candidatos.loc[elegido]
