# gamificacion.py
import pandas as pd
from datetime import datetime, timedelta

# ---------------- LOGROS ----------------
LOGROS = {
    "primera_lectura": {"icono": "🌟", "nombre": "Primera Aventura", "desc": "¡Leíste tu primer libro!"},
    "racha_3": {"icono": "🔥", "nombre": "En Llamas", "desc": "3 días seguidos leyendo"},
    "racha_7": {"icono": "⚡", "nombre": "Súper Lectora", "desc": "7 días seguidos leyendo"},
    "explorador_5": {"icono": "🗺️", "nombre": "Exploradora", "desc": "5 libros diferentes"},
    "explorador_20": {"icono": "🧭", "nombre": "Gran Exploradora", "desc": "20 libros diferentes"},
    "favoritos_3": {"icono": "💖", "nombre": "Coleccionista", "desc": "3 libros favoritos"},
    "libro_largo": {"icono": "📚", "nombre": "Maratonista", "desc": "Libro de +15 minutos"},
    "nocturna": {"icono": "🌙", "nombre": "Lectura Nocturna", "desc": "Leer después de las 8pm"},
    "madrugadora": {"icono": "🌅", "nombre": "Madrugadora", "desc": "Leer antes de las 9am"},
}

# ---------------- NIVELES ----------------
NIVELES = [
    {"nivel": 1, "nombre": "Semillita", "icono": "🌱", "libros": 0},
    {"nivel": 2, "nombre": "Brote", "icono": "🌿", "libros": 5},
    {"nivel": 3, "nombre": "Florcita", "icono": "🌸", "libros": 15},
    {"nivel": 4, "nombre": "Árbol", "icono": "🌳", "libros": 30},
    {"nivel": 5, "nombre": "Bosque Mágico", "icono": "🏰", "libros": 50},
    {"nivel": 6, "nombre": "Reina Lectora", "icono": "👑", "libros": 100},
]


def obtener_nivel(total_libros):
    """Obtiene el nivel actual basado en total de libros leídos"""
    nivel_actual = NIVELES[0]
    for nivel in NIVELES:
        if total_libros >= nivel["libros"]:
            nivel_actual = nivel
    return nivel_actual


def obtener_siguiente_nivel(total_libros):
    """Obtiene el siguiente nivel a alcanzar"""
    for nivel in NIVELES:
        if nivel["libros"] > total_libros:
            return nivel
    return None


def calcular_racha(df_perfil):
    """Calcula días consecutivos de lectura"""
    if df_perfil.empty:
        return 0
    
    # Obtener fechas únicas de lectura
    fechas = pd.to_datetime(df_perfil["ultima_lectura"], errors="coerce").dt.date
    fechas = sorted(set(fechas.dropna()), reverse=True)
    
    if not fechas:
        return 0
    
    hoy = datetime.now().date()
    
    # Si la última lectura fue hace más de 1 día, racha rota
    if fechas[0] < hoy - timedelta(days=1):
        return 0
    
    racha = 1
    for i in range(len(fechas) - 1):
        if fechas[i] - fechas[i+1] == timedelta(days=1):
            racha += 1
        else:
            break
    
    return racha


def obtener_logros_desbloqueados(df_perfil):
    """Determina qué logros están desbloqueados"""
    if df_perfil.empty:
        return []
    
    desbloqueados = []
    
    total_libros = df_perfil["veces_leido"].sum()
    libros_unicos = df_perfil.shape[0]
    total_favoritos = df_perfil[df_perfil["favorito"] == True].shape[0]
    racha = calcular_racha(df_perfil)
    
    # Verificar logros por cantidad
    if total_libros >= 1:
        desbloqueados.append("primera_lectura")
    if racha >= 3:
        desbloqueados.append("racha_3")
    if racha >= 7:
        desbloqueados.append("racha_7")
    if libros_unicos >= 5:
        desbloqueados.append("explorador_5")
    if libros_unicos >= 20:
        desbloqueados.append("explorador_20")
    if total_favoritos >= 3:
        desbloqueados.append("favoritos_3")
    
    # Verificar libro largo
    if not df_perfil[df_perfil["duracion_min"] > 15].empty:
        desbloqueados.append("libro_largo")
    
    # Verificar hora de lectura
    horas = pd.to_datetime(df_perfil["ultima_lectura"], errors="coerce").dt.hour
    if any(horas >= 20):
        desbloqueados.append("nocturna")
    if any(horas < 9):
        desbloqueados.append("madrugadora")
    
    return desbloqueados


def verificar_nuevo_logro(df_perfil_anterior, df_perfil_nuevo):
    """Verifica si se desbloqueó un nuevo logro"""
    logros_antes = set(obtener_logros_desbloqueados(df_perfil_anterior))
    logros_ahora = set(obtener_logros_desbloqueados(df_perfil_nuevo))
    
    nuevos = logros_ahora - logros_antes
    
    if nuevos:
        return list(nuevos)[0]  # Retorna el primer nuevo logro
    return None
