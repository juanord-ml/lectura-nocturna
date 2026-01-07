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

# Diccionario para búsqueda rápida
RETOS_POR_ID = {r["id"]: r for r in RETOS_DISPONIBLES}


def obtener_inicio_semana():
    """Obtiene el lunes de la semana actual"""
    hoy = datetime.now()
    inicio = hoy - timedelta(days=hoy.weekday())
    return inicio.replace(hour=0, minute=0, second=0, microsecond=0)


def obtener_reto_semanal_persistente(perfil, sheet):
    """
    Obtiene el reto de la semana desde Google Sheets.
    Si no existe o es de otra semana, genera uno nuevo y lo guarda.
    """
    
    inicio_semana = obtener_inicio_semana().strftime("%Y-%m-%d")
    
    # Nombres de columnas según perfil
    col_reto = f"reto_{perfil.lower()}"
    col_semana = f"reto_{perfil.lower()}_semana"
    
    try:
        # Leer la configuración desde la fila 2 (después del header)
        # Usaremos celdas específicas para guardar los retos
        # Buscar en qué columna están
        headers = sheet.row_values(1)
        
        if col_reto in headers and col_semana in headers:
            col_reto_idx = headers.index(col_reto) + 1
            col_semana_idx = headers.index(col_semana) + 1
            
            # Leer valores actuales (fila 2)
            reto_actual = sheet.cell(2, col_reto_idx).value
            semana_actual = sheet.cell(2, col_semana_idx).value
            
            # Verificar si es la misma semana
            if semana_actual == inicio_semana and reto_actual in RETOS_POR_ID:
                # Devolver el reto existente
                return RETOS_POR_ID[reto_actual]
            
            # Es otra semana o no hay reto, generar nuevo
            nuevo_reto = random.choice(RETOS_DISPONIBLES)
            
            # Guardar en Google Sheets
            sheet.update_cell(2, col_reto_idx, nuevo_reto["id"])
            sheet.update_cell(2, col_semana_idx, inicio_semana)
            
            return nuevo_reto
        else:
            # Las columnas no existen, usar método de session_state como fallback
            return obtener_reto_semanal_fallback(perfil)
            
    except Exception as e:
        # Si hay error, usar fallback
        st.warning(f"Usando reto temporal: {e}")
        return obtener_reto_semanal_fallback(perfil)


def obtener_reto_semanal_fallback(perfil):
    """Fallback usando session_state (se pierde al cerrar)"""
    
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


def verificar_reto_completado(df_perfil, perfil, reto):
    """Verifica si el reto se completó y retorna True si es nuevo"""
    
    progreso, meta = calcular_progreso_reto(df_perfil, reto)
    
    key_completado = f"reto_completado_{perfil}"
    ya_completado = st.session_state.get(key_completado, False)
    
    if progreso >= meta and not ya_completado:
        st.session_state[key_completado] = True
        return True, reto
    
    return False, None


def mostrar_reto_semanal(df_perfil, perfil, sheet=None):
    """Muestra el widget del reto semanal"""
    
    # Obtener reto (persistente si hay sheet, fallback si no)
    if sheet:
        reto = obtener_reto_semanal_persistente(perfil, sheet)
    else:
        reto = obtener_reto_semanal_fallback(perfil)
    
    # Guardar en session_state para uso posterior
    st.session_state[f"reto_actual_{perfil}"] = reto
    
    progreso, meta = calcular_progreso_reto(df_perfil, reto)
    completado = progreso >= meta
    
    # Marcar como completado si es necesario
    if completado:
        st.session_state[f"reto_completado_{perfil}"] = True
    
    # Calcular días restantes
    hoy = datetime.now()
    fin_semana = obtener_inicio_semana() + timedelta(days=6)
    dias_restantes = max((fin_semana.date() - hoy.date()).days + 1, 0)
    
    # Mostrar el reto
    if completado:
        header_text = "🎯 RETO SEMANAL ✅ ¡COMPLETADO!"
    else:
        header_text = f"🎯 RETO SEMANAL • {dias_restantes} días restantes"
    
    with st.container(border=True):
        st.caption(header_text)
        st.subheader(reto["nombre"])
        st.write(reto["descripcion"])
        
        # Barra de progreso
        porcentaje = progreso / meta if meta > 0 else 0
        st.progress(min(porcentaje, 1.0))
        
        # Métricas
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Progreso", value=f"{progreso} / {meta}")
        with col2:
            st.metric(label="🎁 Premio", value=reto["recompensa"])
    
    return reto
