# app_libros.py
import streamlit as st
import pandas as pd
from sheets import get_df, get_columnas_perfil
from datetime import datetime

from eleccion_libros import seleccionar_libro, obtener_mensaje_modo
from estilos import aplicar_tema_infantil, ruleta_magica, mostrar_portada
from gamificacion import (
    obtener_nivel, calcular_racha, obtener_logros_desbloqueados,
    verificar_nuevo_logro, LOGROS
)
from perfiles import pagina_perfil, inicializar_avatar_state
from historial import pagina_historial, mostrar_logros
from retos import mostrar_reto_semanal, verificar_reto_completado

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
if "reto_recien_completado" not in st.session_state:
    st.session_state.reto_recien_completado = None

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


def obtener_df_perfil(df, perfil):
    """Obtiene datos filtrados y renombrados para un perfil"""
    cols = get_columnas_perfil(perfil)
    
    # Crear copia con columnas renombradas para compatibilidad
    df_perfil = df.copy()
    df_perfil["favorito"] = df_perfil[cols["favorito"]]
    df_perfil["veces_leido"] = df_perfil[cols["veces"]]
    df_perfil["ultima_lectura"] = df_perfil[cols["ultima"]]
    
    # Filtrar solo libros que este perfil ha leído
    return df_perfil[df_perfil["veces_leido"] > 0]


# ---------------- WIDGET DE RACHA ----------------
def mostrar_widget_racha(df_perfil, perfil):
    """Widget motivacional de racha"""
    
    racha = calcular_racha(df_perfil)
    
    if racha == 0:
        mensaje = "¡Hoy es un buen día para leer! 📖"
        emoji_fuego = "💫"
    elif racha == 1:
        mensaje = "¡Empezaste una racha! ¡Sigue mañana!"
        emoji_fuego = "🔥"
    elif racha == 2:
        mensaje = "¡2 días! ¡Vas muy bien!"
        emoji_fuego = "🔥"
    elif racha < 5:
        mensaje = f"¡{racha} días seguidos! ¡Increíble!"
        emoji_fuego = "🔥🔥"
    elif racha < 7:
        mensaje = f"¡WOW! ¡{racha} días! ¡Eres una estrella!"
        emoji_fuego = "🔥🔥🔥"
    else:
        mensaje = f"¡{racha} DÍAS! ¡SÚPER LECTORA!"
        emoji_fuego = "👑🔥👑"
    
    with st.container(border=True):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(f"<h1 style='text-align: center; margin: 0;'>{emoji_fuego}</h1>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='text-align: center; color: #ff69b4; margin: 0;'>{racha} {'día' if racha == 1 else 'días'}</h2>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center; color: #666;'>{mensaje}</p>", unsafe_allow_html=True)


# ---------------- NAVEGACIÓN SIDEBAR ----------------
with st.sidebar:
    st.markdown("""
    <div style='text-align: center; padding: 20px;'>
        <span style='font-size: 60px;'>📚</span>
        <h2 style='color: #ff69b4; margin: 10px 0;'>Mis Libros</h2>
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
    
    # Mini-stats en sidebar
    df_sidebar = cargar_datos()
    df_perfil_sidebar = obtener_df_perfil(df_sidebar, perfil)
    
    if not df_perfil_sidebar.empty:
        nivel = obtener_nivel(df_perfil_sidebar["veces_leido"].sum())
        racha = calcular_racha(df_perfil_sidebar)
        
        st.divider()
        st.markdown(f"""
        <div style='text-align: center; padding: 10px;'>
            <span style='font-size: 35px;'>{nivel["icono"]}</span><br>
            <span style='color: #333; font-size: 14px;'>Nivel {nivel["nivel"]}: {nivel["nombre"]}</span><br>
            <span style='color: #ff5722; font-size: 16px; font-weight: bold;'>🔥 {racha} días</span>
        </div>
        """, unsafe_allow_html=True)


# ---------------- PÁGINA RULETA ----------------
def pagina_ruleta():
    st.title("📖 Noche de Lectura")
    
    df = cargar_datos()
    df_perfil = obtener_df_perfil(df, perfil)
    cols = get_columnas_perfil(perfil)
    
    # Widget de racha
    mostrar_widget_racha(df_perfil, perfil)
    
    # Reto semanal
    _, sheet = get_df()
    reto = mostrar_reto_semanal(df_perfil, perfil, sheet)
    
    # Celebraciones
    if st.session_state.reto_recien_completado:
        reto_info = st.session_state.reto_recien_completado
        st.balloons()
        st.success(f"🎉 ¡Completaste el reto: {reto_info['nombre']}! Premio: {reto_info['recompensa']}")
        st.session_state.reto_recien_completado = None
    
    if st.session_state.nuevo_logro:
        logro = LOGROS[st.session_state.nuevo_logro]
        st.balloons()
        st.success(f"🏆 ¡Desbloqueaste: {logro['icono']} {logro['nombre']}!")
        st.session_state.nuevo_logro = None
    
    st.divider()
    
    # Controles
    st.subheader("🎮 ¿Qué quieres leer?")
    
    col_edad, col_modo = st.columns([1, 2])
    
    with col_edad:
        edad = st.slider("👧 Edad", 2, 9, 5)
    
    with col_modo:
        modo = st.radio(
            "📚 Modo",
            ["🎡 Sorpresa", "🌙 Cortito", "⭐ Favoritos", "🆕 Nuevos", "📋 Elegir"],
            horizontal=True
        )
    
    # Configurar filtros
    if modo == "🌙 Cortito":
        max_duracion, solo_favoritos, solo_nuevos, modo_key = 7, False, False, "cortito"
    elif modo == "⭐ Favoritos":
        max_duracion, solo_favoritos, solo_nuevos, modo_key = None, True, False, "favoritos"
    elif modo == "🆕 Nuevos":
        max_duracion, solo_favoritos, solo_nuevos, modo_key = None, False, True, "nuevos"
    elif modo == "📋 Elegir":
        # MODO ELEGIR MANUALMENTE
        max_duracion, solo_favoritos, solo_nuevos, modo_key = None, False, False, "elegir"
    else:
        max_duracion, solo_favoritos, solo_nuevos, modo_key = None, False, False, "default"
    
    # --- MODO ELEGIR MANUALMENTE ---
    if modo == "📋 Elegir":
        st.markdown("")
        st.subheader("📚 Elige un libro")
        
        # Filtrar libros activos y de edad apropiada
        df_elegibles = df[
            (df["activa"] == True) &
            (df["edad_min"] <= edad) &
            (df["edad_max"] >= edad)
        ].sort_values("titulo")
        
        if df_elegibles.empty:
            st.warning("No hay libros disponibles para esta edad.")
        else:
            # Selector de libro
            opciones = df_elegibles["titulo"].tolist()
            libro_elegido = st.selectbox(
                "Selecciona el libro:",
                opciones,
                key="selector_libro_manual"
            )
            
            if st.button("📖 ¡Este quiero leer!", use_container_width=True):
                libro_row = df_elegibles[df_elegibles["titulo"] == libro_elegido].iloc[0]
                st.session_state.libro_actual = libro_row.to_dict()
                # Agregar datos del perfil al libro
                st.session_state.libro_actual["favorito"] = libro_row[cols["favorito"]]
                st.session_state.libro_actual["veces_leido"] = libro_row[cols["veces"]]
                st.balloons()
    
    # --- MODO RULETA ---
    else:
        st.markdown("")
        if st.button("🎡 ¡Girar la ruleta!", use_container_width=True):
            cargar_datos.clear()
            df = cargar_datos()
            
            libro = seleccionar_libro(
                df, 
                perfil=perfil,  # NUEVO: pasar perfil
                edad_nina=edad, 
                max_duracion=max_duracion,
                permitir_interactivo=True, 
                solo_favoritos=solo_favoritos,
                solo_nuevos=solo_nuevos
            )
            
            if libro is None:
                st.session_state.libro_actual = None
                mensaje = obtener_mensaje_modo(modo_key, False)
                st.warning(mensaje)
            else:
                libro_dict = libro.to_dict()
                # Agregar datos del perfil al libro
                libro_dict["favorito"] = libro[cols["favorito"]]
                libro_dict["veces_leido"] = libro[cols["veces"]]
                st.session_state.libro_actual = libro_dict
                
                df_filtrado = df[
                    (df["edad_min"] <= edad) & (df["edad_max"] >= edad) & (df["activa"] == True)
                ]
                if solo_favoritos:
                    df_filtrado = df_filtrado[df_filtrado[cols["favorito"]] == True]
                elif solo_nuevos:
                    df_filtrado = df_filtrado[df_filtrado[cols["veces"]] == 0]
                elif max_duracion:
                    df_filtrado = df_filtrado[df_filtrado["duracion_min"] <= max_duracion]
                
                titulos = df_filtrado["titulo"].tolist()
                if len(titulos) < 3:
                    titulos = titulos * 3
                
                ruleta_magica(titulos, libro["titulo"])
                st.balloons()
    
    # --- MOSTRAR LIBRO SELECCIONADO ---
    if st.session_state.libro_actual is not None:
        libro = st.session_state.libro_actual
        es_favorito = libro.get("favorito", False)
        estrella = "⭐" if es_favorito else ""
        
        with st.container(border=True):
            col_izq, col_centro, col_der = st.columns([1, 2, 1])
            with col_centro:
                portada_url = libro.get("portada_url", "")
                mostrar_portada(portada_url, ancho=180)

            st.markdown(f"<h2 style='text-align: center; color: #d63384;'>{libro['titulo']} {estrella}</h2>", unsafe_allow_html=True)
            
            col_info1, col_info2, col_info3 = st.columns(3)
            col_info1.metric("👧 Lectora", f"{PERFILES[perfil]} {perfil}")
            col_info2.metric("⏱️ Duración", f"{libro['duracion_min']} min")
            col_info3.metric("📍 Ubicación", libro["ubicacion"])
        
        col1, col2 = st.columns(2)
        
        with col1:
            btn_text = "💖 ¡Ya es favorito!" if es_favorito else "⭐ ¡Es mi favorito!"
            if st.button(btn_text, key="btn_fav", use_container_width=True, disabled=es_favorito):
                df_fresh, sheet = get_df()
                # Actualizar columna del perfil
                df_fresh.loc[df_fresh["id"] == libro["id"], cols["favorito"]] = True
                sheet.update([df_fresh.columns.values.tolist()] + df_fresh.astype(str).values.tolist())
                cargar_datos.clear()
                st.session_state.libro_actual["favorito"] = True
                st.toast("⭐ ¡Favorito guardado!")
                st.rerun()
        
        with col2:
            if st.button("✅ ¡Lo leímos!", key="btn_leido", use_container_width=True):
                # Guardar estado anterior
                df_antes = cargar_datos()
                df_perfil_antes = obtener_df_perfil(df_antes, perfil)
                
                # Actualizar
                df_fresh, sheet = get_df()
                idx = df_fresh["id"] == libro["id"]
                df_fresh.loc[idx, cols["ultima"]] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                df_fresh.loc[idx, cols["veces"]] = df_fresh.loc[idx, cols["veces"]] + 1
                sheet.update([df_fresh.columns.values.tolist()] + df_fresh.astype(str).values.tolist())
                
                cargar_datos.clear()
                
                # Verificar logros
                df_despues = cargar_datos()
                df_perfil_despues = obtener_df_perfil(df_despues, perfil)
                
                nuevo_logro = verificar_nuevo_logro(df_perfil_antes, df_perfil_despues)
                if nuevo_logro:
                    st.session_state.nuevo_logro = nuevo_logro
                
                # Verificar reto
                reto_actual = st.session_state.get(f"reto_actual_{perfil}")
                if reto_actual:
                    reto_nuevo, reto_info = verificar_reto_completado(df_perfil_despues, perfil, reto_actual)
                    if reto_nuevo:
                        st.session_state.reto_recien_completado = reto_info
                
                st.session_state.libro_actual = None
                st.balloons()
                st.toast("✅ ¡Lectura registrada!")
                st.rerun()
        
        if st.button("🔄 Elegir otro libro", use_container_width=True):
            st.session_state.libro_actual = None
            st.rerun()


# ---------------- RENDERIZAR PÁGINA ----------------
df = cargar_datos()

if pagina == "🎡 Ruleta":
    pagina_ruleta()
elif pagina == "📖 Mi Diario":
    df_perfil = obtener_df_perfil(df, perfil)
    pagina_historial(df_perfil, perfil)
elif pagina == "👤 Mi Perfil":
    df_perfil = obtener_df_perfil(df, perfil)
    pagina_perfil(perfil, df_perfil)
elif pagina == "🏆 Logros":
    st.title("🏆 Mis Logros")
    df_perfil = obtener_df_perfil(df, perfil)
    mostrar_logros(df_perfil)
