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
    
    # Si no hay reto o es de otra semana, generar nuevo
    if key not in st.session_state or st.session_state.get(key_fecha) != inicio_semana:
        # Seleccionar reto aleatorio
        st.session_state[key] = random.choice(RETOS_DISPONIBLES)
        st.session_state[key_fecha] = inicio_semana
        # Resetear estado de completado
        st.session_state[f"reto_completado_{perfil}"] = False
    
    return st.session_state[key]


def calcular_progreso_reto(df_perfil, reto):
    """Calcula el progreso del reto actual"""
    
    inicio_semana = obtener_inicio_semana()
    
    if df_perfil.empty:
        return 0, reto["meta"]
    
    # Convertir fechas
    df_temp = df_perfil.copy()
    df_temp["fecha_lectura"] = pd.to_datetime(df_temp["ultima_lectura"], errors="coerce")
    
    # Filtrar lecturas de esta semana
    df_semana = df_temp[df_temp["fecha_lectura"] >= inicio_semana]
    
    progreso = 0
    
    if reto["tipo"] == "dias_lectura":
        # Días únicos con lectura
        if not df_semana.empty:
            dias = df_semana["fecha_lectura"].dt.date.nunique()
            progreso = dias
    
    elif reto["tipo"] == "minutos":
        # Suma de minutos leídos esta semana
        progreso = int(df_semana["duracion_min"].sum())
    
    elif reto["tipo"] == "libro_nuevo":
        # Libros con veces_leido == 1 (primera vez)
        # Esto cuenta libros que se leyeron por primera vez esta semana
        progreso = df_semana[df_semana["veces_leido"] == 1].shape[0]
    
    elif reto["tipo"] == "favorito":
        # Favoritos marcados (en general)
        progreso = df_semana[df_semana["favorito"] == True].shape[0]
    
    elif reto["tipo"] == "lecturas":
        # Total de lecturas esta semana
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
    """Muestra el widget del reto semanal"""
    
    reto = obtener_reto_semanal(perfil)
    progreso, meta = calcular_progreso_reto(df_perfil, reto)
    completado = progreso >= meta
    
    # Calcular porcentaje
    porcentaje = min((progreso / meta) * 100, 100) if meta > 0 else 0
    
    # Colores según estado
    if completado:
        color_fondo = "#d4edda"
        color_borde = "#28a745"
        color_barra = "#28a745"
    elif porcentaje >= 50:
        color_fondo = "#fff3cd"
        color_borde = "#ffc107"
        color_barra = "#ffc107"
    else:
        color_fondo = "#ffe4ec"
        color_borde = "#ff69b4"
        color_barra = "#ff69b4"
    
    # Días restantes de la semana
    hoy = datetime.now()
    fin_semana = obtener_inicio_semana() + timedelta(days=6)
    dias_restantes = (fin_semana.date() - hoy.date()).days + 1
    
    st.markdown(f"""
    <div style="
        background: {color_fondo};
        border: 3px solid {color_borde};
        border-radius: 20px;
        padding: 20px;
        margin: 15px 0;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    ">
        <div style="font-size: 14px; color: #666; margin-bottom: 5px;">
            🎯 RETO DE LA SEMANA {'✅ ¡COMPLETADO!' if completado else f'• {dias_restantes} días restantes'}
        </div>
        <div style="font-size: 28px; margin: 10px 0;">
            {reto['nombre']}
        </div>
        <div style="color: #555; font-size: 16px; margin: 10px 0;">
            {reto['descripcion']}
        </div>
        
        <!-- Barra de progreso -->
        <div style="
            background: #e0e0e0;
            border-radius: 15px;
            height: 25px;
            margin: 15px 0;
            overflow: hidden;
            position: relative;
        ">
            <div style="
                background: linear-gradient(90deg, {color_barra}, {color_barra}aa);
                height: 100%;
                width: {porcentaje}%;
                border-radius: 15px;
                transition: width 0.5s ease;
            "></div>
            <div style="
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                color: #333;
                font-weight: bold;
                font-size: 14px;
            ">
                {progreso}/{meta}
            </div>
        </div>
        
        <div style="
            background: {'linear-gradient(135deg, #ffd700, #ffec8b)' if completado else '#f5f5f5'};
            border-radius: 10px;
            padding: 10px;
            margin-top: 10px;
        ">
            <span style="font-size: 14px; color: #666;">
                {'🎁 ¡Ganaste: ' if completado else '🎁 Premio: '}
            </span>
            <span style="font-size: 16px; font-weight: bold; color: #333;">
                {reto['recompensa']}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
