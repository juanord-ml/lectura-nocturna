import pandas as pd
import random
from datetime import datetime, timedelta

# cargar data
libros = pd.read_csv("catalogo_libros.csv", parse_dates=["ultima_lectura"])

# config
DIAS_NO_REPETIR = 5

def seleccionar_libro(
    edad_nina,
    max_duracion=None,
    permitir_interactivo=True
):
    hoy = datetime.now()

    candidatos = libros[
        (libros["activa"] == True) &
        (libros["edad_min"] <= edad_nina) &
        (libros["edad_max"] >= edad_nina)
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

if __name__ == "__main__":
    libro = seleccionar_libro(
        edad_nina=5,
        max_duracion=10,
        permitir_interactivo=True
    )

    if libro is None:
        print("No hay libros elegibles hoy.")
    else:
        print("\n📖 Libro seleccionado:\n")
        print(f"Título: {libro['titulo']}")
        print(f"Edad: {libro['edad_min']}–{libro['edad_max']}")
        print(f"Duración: {libro['duracion_min']} min")
        print(f"Ubicación: {libro['ubicacion']}")
