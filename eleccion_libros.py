# eleccion_libros.py
import random
from datetime import datetime, timedelta

DIAS_NO_REPETIR = 5


def seleccionar_libro(
    df,
    perfil,
    edad_nina,
    max_duracion=None,
    permitir_interactivo=True,
    solo_favoritos=False,
    solo_nuevos=False
):
    """
    Selecciona un libro basado en criterios y perfil.
    """
    hoy = datetime.now()
    
    # Columnas específicas del perfil
    perfil_lower = perfil.lower()
    col_favorito = f"favorito_{perfil_lower}"
    col_veces = f"veces_{perfil_lower}"
    col_ultima = f"ultima_{perfil_lower}"

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
    
    # Filtro: solo favoritos DEL PERFIL
    if solo_favoritos:
        candidatos = candidatos[candidatos[col_favorito] == True]
    
    # Filtro: solo libros nuevos (nunca leídos POR ESTE PERFIL)
    elif solo_nuevos:
        candidatos = candidatos[candidatos[col_veces] == 0]
    
    # Filtro normal: no repetir en X días PARA ESTE PERFIL
    else:
        candidatos = candidatos[
            (candidatos[col_ultima].isna()) |
            (candidatos[col_ultima] < hoy - timedelta(days=DIAS_NO_REPETIR))
        ]

    if candidatos.empty:
        return None

    def peso(row):
        """Calcula el peso/probabilidad de selección"""
        w = 1.0
        
        # Favoritos tienen más probabilidad
        if not solo_favoritos and row[col_favorito]:
            w *= 1.5
        
        # Libros nuevos tienen más probabilidad
        if not solo_nuevos and row[col_veces] == 0:
            w *= 1.4
        
        # Libros interactivos ligeramente más probables
        if row["interactivo"]:
            w *= 1.2
        
        # Libros poco leídos tienen más probabilidad
        if row[col_veces] > 0 and row[col_veces] < 3:
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
