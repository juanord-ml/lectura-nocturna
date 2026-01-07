# eleccion_libros.py
import random
from datetime import datetime, timedelta

DIAS_NO_REPETIR = 5


def seleccionar_libro(
    df,
    edad_nina,
    max_duracion=None,
    permitir_interactivo=True,
    solo_favoritos=False,
    solo_nuevos=False
):
    """
    Selecciona un libro basado en criterios.
    
    Parámetros:
    - df: DataFrame con los libros
    - edad_nina: Edad de la niña
    - max_duracion: Duración máxima en minutos (None = sin límite)
    - permitir_interactivo: Si permite libros interactivos
    - solo_favoritos: Solo mostrar libros marcados como favoritos
    - solo_nuevos: Solo mostrar libros nunca leídos
    """
    hoy = datetime.now()

    # Filtro base: activos y edad apropiada
    candidatos = df[
        (df["activa"] == True) &
        (df["edad_min"] <= edad_nina) &
        (df["edad_max"] >= edad_nina)
    ].copy()

    # Filtro por duración
    if max_duracion:
        candidatos = candidatos[candidatos["duracion_min"] <= max_duracion]

    # Filtro por interactivo
    if not permitir_interactivo:
        candidatos = candidatos[candidatos["interactivo"] == False]
    
    # Filtro: solo favoritos
    if solo_favoritos:
        candidatos = candidatos[candidatos["favorito"] == True]
        # Para favoritos, no aplicamos el filtro de días
    
    # Filtro: solo libros nuevos (nunca leídos)
    elif solo_nuevos:
        candidatos = candidatos[candidatos["veces_leido"] == 0]
    
    # Filtro normal: no repetir en X días
    else:
        candidatos = candidatos[
            (candidatos["ultima_lectura"].isna()) |
            (candidatos["ultima_lectura"] < hoy - timedelta(days=DIAS_NO_REPETIR))
        ]

    if candidatos.empty:
        return None

    def peso(row):
        """Calcula el peso/probabilidad de selección"""
        w = 1.0
        
        # Favoritos tienen más probabilidad (pero no en modo favoritos)
        if not solo_favoritos and row["favorito"]:
            w *= 1.5
        
        # Libros nuevos tienen más probabilidad (pero no en modo nuevos)
        if not solo_nuevos and row["veces_leido"] == 0:
            w *= 1.4
        
        # Libros interactivos ligeramente más probables
        if row["interactivo"]:
            w *= 1.2
        
        # Libros poco leídos tienen más probabilidad
        if row["veces_leido"] > 0 and row["veces_leido"] < 3:
            w *= 1.1
        
        return w

    pesos = candidatos.apply(peso, axis=1)

    elegido = random.choices(
        list(candidatos.index),
        weights=pesos,
        k=1
    )[0]

    return candidatos.loc[elegido]


def obtener_mensaje_modo(modo, hay_libros):
    """Retorna un mensaje apropiado si no hay libros para el modo"""
    
    mensajes = {
        "favoritos": "😢 No tienes favoritos aún. ¡Marca algunos libros con ⭐!",
        "nuevos": "🎉 ¡Ya leíste todos los libros! ¡Eres increíble!",
        "cortito": "📚 No hay libros cortitos disponibles ahora.",
        "default": "📖 No hay libros disponibles con estos filtros."
    }
    
    if hay_libros:
        return None
    
    return mensajes.get(modo, mensajes["default"])
