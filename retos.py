# retos.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random

RETOS_DISPONIBLES = [
    {
        "id": "leer_3_dias",
        "nombre": "📚 Lectora Constante",
        "descripcion": "Lee 3 días esta semana",
        "meta": 3,
        "tipo": "dias_lectura",
        "recompensa": "🌟 Estrella Brillante"
    },
    {
        "id": "leer_5_dias",
        "nombre": "📖 Súper Lectora",
        "descripcion": "Lee 5 días esta semana",
        "meta": 5,
        "tipo": "dias_lectura",
        "recompensa": "👑 Corona Dorada"
    },
    {
        "id": "libro_nuevo",
        "nombre": "🆕 Exploradora",
        "descripcion": "Lee un libro que nunca hayas leído",
        "meta": 1,
        "tipo": "libro_nuevo",
        "recompensa": "🗺️ Mapa del Tesoro"
    },
    {
        "id": "dos_libros_nuevos",
        "nombre": "🧭 Gran Exploradora",
        "descripcion": "Lee 2 libros nuevos esta semana",
        "meta": 2,
        "tipo": "libro_nuevo",
        "recompensa": "🏆 Trofeo Aventura"
    },
    {
        "id": "leer_20_min",
        "nombre": "⏱️ Mini Maratón",
        "descripcion": "Lee 20 minutos en total esta semana",
        "meta": 20,
        "tipo": "minutos",
        "recompensa": "🏃 Zapatillas Mágicas"
    },
    {
        "id": "leer_45_min",
        "nombre": "🏅 Gran Maratón",
        "descripcion": "Lee 45 minutos en total esta semana",
        "meta": 45,
        "tipo": "minutos",
        "recompensa": "🥇 Medalla de Oro"
    },
    {
        "id": "favorito_nuevo",
        "nombre": "💖 Coleccionista",
        "descripcion": "Marca un libro como favorito",
        "meta": 1,
        "tipo": "favorito",
        "recompensa": "💎 Diamante Rosa"
    },
    {
        "id": "tres_lecturas",
        "nombre": "📚 Triple Lectura",
        "descripcion": "Lee 3 veces esta semana",
        "meta": 3,
        "tipo": "lecturas",
        "recompensa": "🎀 Lazo Especial"
    },
]


def obtener_inicio_semana():
    """Obtiene el lunes de la semana actual"""
    hoy = datetime.now()
    inicio = hoy - timedelta(days=hoy.weekday())
    return inicio.replace(hour=0, minute=0, second=0, microsecond=0)


def obtener_reto_semanal(perfil):
    """Obtiene o genera el reto de la semana para un perfil"""
    
    key = f"reto_semanal_{perfil}"
    key_fecha = f"reto_fecha_{perfil}"
    
    inicio_semana = obtener_inicio_semana().date()
    
    if key not in st.session_state or st.session_state.get(key_fecha) != inicio_semana:
        st.session_state[key] = random.choice(RETOS_DISPONIBLES)
        st.session_state[key_fecha] = inicio_semana
        st.session_state[f"reto_completado_{perfil}"] = False
    
    return st.session_state[key]


def calcular_progreso_reto(df_perfil, reto):
    """Calcula el progreso del reto actual"""
    
    inicio_semana = obtener_inicio_semana()
    
    if df_perfil.empty:
        return 0, reto["meta"]
    
    df_temp = df_perfil.copy()
    df_temp["fecha_lectura"] = pd.to_datetime(df_temp["ultima_lectura"], errors="coerce")
    
    df_semana = df_temp[df_temp["fecha_lectura"] >= inicio_semana]
    
    progreso = 0
    
    if reto["tipo"] == "dias_lectura":
        if not df_semana.empty:
            dias = df_semana["fecha_lectura"].dt.date.nunique()
            progreso = dias
    
    elif reto["tipo"] == "minutos":
        progreso = int(df_semana["duracion_min"].sum())
    
    elif reto["tipo"] == "libro_nuevo":
        progreso = df_semana[df_semana["veces_leido"] == 1].shape[0]
    
    elif reto["tipo"] == "favorito":
        progreso = df_semana[df_semana["favorito"] == True].shape[0]
    
    elif reto["tipo"] == "lecturas":
        progreso = df_semana.shape[0]
    
    return min(progreso, reto["meta"]), reto["meta"]


def verificar_reto_completado(df_perfil, perfil):
    """Verifica si el reto se completó y retorna True si es nuevo"""
    
    reto = obtener_reto_semanal(perfil)
    progreso, meta = calcular_progreso_reto(df_perfil, reto)
    
    key_completado = f"reto_completado_{perfil}"
    ya_completado = st.session_state.get(key_completado, False)
    
    if progreso >= meta and not ya_completado:
        st.session_state[key_completado] = True
        return True, reto
    
    return False, None


def mostrar_reto_semanal(df_perfil, perfil):
    """Muestra el widget del reto semanal usando componentes nativos de Streamlit"""
    
    reto = obtener_reto_semanal(perfil)
    progreso, meta = calcular_progreso_reto(df_perfil, reto)
    completado = progreso >= meta
    
    # Calcular días restantes
    hoy = datetime.now()
    fin_semana = obtener_inicio_semana() + timedelta(days=6)
    dias_restantes = max((fin_semana.date() - hoy.date()).days + 1, 0)
    
    # Usar container de Streamlit
    with st.container():
        # Header del reto
        if completado:
            st.success(f"🎯 RETO DE LA SEMANA ✅ ¡COMPLETADO!")
        else:
            st.info(f"🎯 RETO DE LA SEMANA • {dias_restantes} días restantes")
        
        # Nombre del reto
        st.markdown(f"### {reto['nombre']}")
        
        # Descripción
        st.write(reto['descripcion'])
        
        # Barra de progreso nativa de Streamlit
        porcentaje = progreso / meta if meta > 0 else 0
        st.progress(min(porcentaje, 1.0))
        
        # Texto de progreso
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Progreso", f"{progreso}/{meta}")
        with col2:
            st.metric("Premio", reto['recompensa'])
        
        st.divider()
