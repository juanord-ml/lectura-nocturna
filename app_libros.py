# app_libros.py
import streamlit as st
import pandas as pd
from sheets import get_df
from datetime import datetime
from eleccion_libros import seleccionar_libro

# Importar nuevos módulos
from gamificacion import (
    obtener_nivel, calcular_racha, obtener_logros_desbloqueados,
    verificar_nuevo_logro, LOGROS
)
from perfiles import pagina_perfil, inicializar_avatar_state
from historial import pagina_historial, mostrar_logros
from estilos import aplicar_tema_infantil, celebrar_logro, ruleta_magica

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="📖 Lectura de Hoy",
    page_icon="📚",
    layout="centered"
)

# ---------------- APLICAR TEMA ----------------
aplicar_tema_infantil()

# ---------------- SESSION STATE ----------------
if "libro_actual" not in st.session_state:
    st.session_state.libro_actual = None
if "nuevo_logro" not in st.session_state:
    st.session_state.nuevo_logro = None

inicializar_avatar_state()

# ---------------- PERFILES ----------------
PERFILES = {
    "Clara": "🐭",
    "Gracia": "🐥"
}

# ---------------- DATA ----------------
@st.cache_data(ttl=60)
def cargar_datos():
    df, _ = get_df()
    return df

def obtener_sheet():
    _, sheet = get_df()
    return sheet

# ---------------- NAVEGACIÓN SIDEBAR ----------------
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 20px;">
        <span style="font-size: 60px;">📚</span>
        <h2 style="color: #ff69b4;">Mis Libros</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    perfil = st.radio(
        "¿Quién eres?",
        list(PERFILES.keys()),
        format_func=lambda x: f"{PERFILES[x]} {x}"
    )
    
    st.divider()
    
    pagina = st.radio(
        "🧭 Menú",
        ["🎡 Ruleta", "📖 Mi Diario", "👤 Mi Perfil", "🏆 Logros"],
        label_visibility="collapsed"
    )
    
    # Mostrar nivel actual en sidebar
    df_sidebar = cargar_datos()
    df_perfil_sidebar = df_sidebar[df_sidebar["ultima_lectora"] == perfil]
    if not df_perfil_sidebar.empty:
        nivel = obtener_nivel(df_perfil_sidebar["veces_leido"].sum())
        racha = calcular_racha(df_perfil_sidebar)
        st.divider()
        st.markdown(f"""
        <div style="text-align: center; padding: 10px;">
            <span style="font-size: 30px;">{nivel['icono']}</span><br>
            <small>Nivel {nivel['nivel']}</small><br>
            <small>🔥 Racha: {racha} días</small>
        </div>
        """, unsafe_allow_html=True)


# ---------------- PÁGINA RULETA ----------------
def pagina_ruleta():
    st.title("📖 Noche de Lectura")
    
    # Mostrar nuevo logro si existe
    if st.session_state.nuevo_logro:
        logro = LOGROS[st.session_state.nuevo_logro]
        celebrar_logro(f"¡Desbloqueaste: {logro['icono']} {logro['nombre']}!", "nivel")
        st.session_state.nuevo_logro = None
    
    # Controles
    col_ctrl1, col_ctrl2 = st.columns(2)
    
    with col_ctrl1:
        edad = st.slider("👧 Edad", 2, 9, 5)
    
    with col_ctrl2:
        modo = st.radio(
            "📚 Modo",
            ["🎡 Sorpresa", "🌙 Cortito"],
            horizontal=True
        )
    
    max_duracion = 7 if modo == "🌙 Cortito" else None
    
    # Botón de ruleta
    if st.button("🎡 Girar la ruleta", use_container_width=True):
        cargar_datos.clear()
        df = cargar_datos()
        
        libro = seleccionar_libro(
            df,
            edad_nina=edad,
            max_duracion=max_duracion,
            permitir_interactivo=True
        )
        
        if libro is None:
            st.session_state.libro_actual = None
            st.warning("😕 No hay libros elegibles hoy. ¡Intenta con otras opciones!")
        else:
            st.session_state.libro_actual = libro.to_dict()
            
            titulos = df[
                (df["edad_min"] <= edad) &
                (df["edad_max"] >= edad) &
                (df["activa"] == True)
            ]["titulo"].tolist()
            
            ruleta_magica(titulos, libro["titulo"])
            st.balloons()
    
    # Mostrar libro seleccionado
    if st.session_state.libro_actual is not None:
        libro = st.session_state.libro_actual
        
        st.markdown(f"""
        <div style="
            background: white;
            border-radius: 20px;
            padding: 25px;
            margin: 20px 0;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            border: 3px solid #ff69b4;
        ">
            <h2 style="text-align: center; color: #ff69b4;">📖 {libro['titulo']}</h2>
            <p style="text-align: center;">
                👧 Lectora: <strong>{PERFILES[perfil]} {perfil}</strong><br>
                ⏱️ {libro['duracion_min']} minutos<br>
                📍 {libro['ubicacion']}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("⭐ ¡Es mi favorito!", key="btn_favorito", use_container_width=True):
                df_fresh, sheet = get_df()
                df_fresh.loc[df_fresh["id"] == libro["id"], "favorito"] = True
                sheet.update(
                    [df_fresh.columns.values.tolist()] +
                    df_fresh.astype(str).values.tolist()
                )
                cargar_datos.clear()
                celebrar_logro("¡Favorito guardado!", "favorito")
                st.rerun()
        
        with col2:
            if st.button("✅ ¡Lo leímos!", key="btn_leido", use_container_width=True):
                # Guardar estado anterior para verificar nuevos logros
                df_antes, _ = get_df()
                df_perfil_antes = df_antes[df_antes["ultima_lectora"] == perfil].copy()
                
                # Actualizar lectura
                df_fresh, sheet = get_df()
                idx = df_fresh["id"] == libro["id"]
                df_fresh.loc[idx, "ultima_lectura"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                df_fresh.loc[idx, "veces_leido"] = df_fresh.loc[idx, "veces_leido"] + 1
                df_fresh.loc[idx, "ultima_lectora"] = perfil
                sheet.update(
                    [df_fresh.columns.values.tolist()] +
                    df_fresh.astype(str).values.tolist()
                )
                
                # Verificar nuevos logros
                df_despues, _ = get_df()
                df_perfil_despues = df_despues[df_despues["ultima_lectora"] == perfil].copy()
                nuevo_logro = verificar_nuevo_logro(df_perfil_antes, df_perfil_despues)
                
                if nuevo_logro:
                    st.session_state.nuevo_logro = nuevo_logro
                
                cargar_datos.clear()
                st.session_state.libro_actual = None
                st.rerun()


# ---------------- RENDERIZAR PÁGINA SEGÚN SELECCIÓN ----------------
df = cargar_datos()

if pagina == "🎡 Ruleta":
    pagina_ruleta()

elif pagina == "📖 Mi Diario":
    pagina_historial(df, perfil)

elif pagina == "👤 Mi Perfil":
    df_perfil = df[df["ultima_lectora"] == perfil].copy()
    pagina_perfil(perfil, df_perfil)

elif pagina == "🏆 Logros":
    st.title("🏆 Mis Logros")
    df_perfil = df[df["ultima_lectora"] == perfil].copy()
    mostrar_logros(df_perfil)
