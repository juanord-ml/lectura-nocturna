# app_libros.py
import streamlit as st
import pandas as pd
from sheets import get_df
from datetime import datetime
from eleccion_libros import seleccionar_libro, obtener_mensaje_modo

# Importar módulos de gamificación
from gamificacion import (
    obtener_nivel, calcular_racha, obtener_logros_desbloqueados,
    verificar_nuevo_logro, LOGROS
)
from perfiles import pagina_perfil, inicializar_avatar_state
from historial import pagina_historial, mostrar_logros
from estilos import aplicar_tema_infantil, celebrar_logro, ruleta_magica

# NUEVOS IMPORTS
from sonidos import reproducir_sonido, sonido_celebracion, activar_sonidos, toggle_sonidos
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
if "sonidos_activos" not in st.session_state:
    st.session_state.sonidos_activos = True

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


# ---------------- WIDGET DE RACHA ----------------
def mostrar_widget_racha(df_perfil, perfil):
    """Widget motivacional de racha"""
    
    racha = calcular_racha(df_perfil)
    
    # Configurar mensaje y colores según racha
    if racha == 0:
        mensaje = "¡Hoy es un buen día para leer! 📖"
        color = "#ffc107"
        emoji_fuego = "💫"
    elif racha == 1:
        mensaje = "¡Empezaste una racha! ¡Sigue mañana!"
        color = "#ff9800"
        emoji_fuego = "🔥"
    elif racha == 2:
        mensaje = "¡2 días! ¡Vas muy bien!"
        color = "#ff5722"
        emoji_fuego = "🔥"
    elif racha < 5:
        mensaje = f"¡{racha} días seguidos! ¡Increíble!"
        color = "#f44336"
        emoji_fuego = "🔥🔥"
    elif racha < 7:
        mensaje = f"¡WOW! ¡{racha} días! ¡Eres una estrella!"
        color = "#e91e63"
        emoji_fuego = "🔥🔥🔥"
    else:
        mensaje = f"¡{racha} DÍAS! ¡SÚPER LECTORA!"
        color = "#9c27b0"
        emoji_fuego = "👑🔥👑"
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {color}22, {color}44);
        border: 3px solid {color};
        border-radius: 20px;
        padding: 15px 20px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px {color}33;
    ">
        <div style="font-size: 35px; margin-bottom: 5px;">
            {emoji_fuego}
        </div>
        <div style="
            font-size: 32px; 
            font-weight: bold; 
            color: {color};
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        ">
            {racha} {'día' if racha == 1 else 'días'}
        </div>
        <div style="font-size: 16px; color: #555; margin-top: 5px;">
            {mensaje}
        </div>
    </div>
    """, unsafe_allow_html=True)


# ---------------- NAVEGACIÓN SIDEBAR ----------------
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 20px;">
        <span style="font-size: 60px;">📚</span>
        <h2 style="color: #ff69b4; margin: 10px 0;">Mis Libros</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Toggle de sonidos
    col_sonido, col_texto = st.columns([1, 3])
    with col_sonido:
        toggle_sonidos()
    with col_texto:
        st.caption("Sonidos" if st.session_state.sonidos_activos else "Silencio")
    
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
    
    # Mostrar mini-stats en sidebar
    df_sidebar = cargar_datos()
    df_perfil_sidebar = df_sidebar[df_sidebar["ultima_lectora"] == perfil]
    
    if not df_perfil_sidebar.empty:
        nivel = obtener_nivel(df_perfil_sidebar["veces_leido"].sum())
        racha = calcular_racha(df_perfil_sidebar)
        
        st.divider()
        st.markdown(f"""
        <div style="text-align: center; padding: 10px;">
            <span style="font-size: 35px;">{nivel['icono']}</span><br>
            <span style="color: #333; font-size: 14px;">Nivel {nivel['nivel']}: {nivel['nombre']}</span><br>
            <span style="color: #ff5722; font-size: 16px; font-weight: bold;">🔥 {racha} días</span>
        </div>
        """, unsafe_allow_html=True)


# ---------------- PÁGINA RULETA ----------------
def pagina_ruleta():
    st.title("📖 Noche de Lectura")
    
    df = cargar_datos()
    df_perfil = df[df["ultima_lectora"] == perfil].copy()
    
    # Widget de racha
    mostrar_widget_racha(df_perfil, perfil)
    
    # Reto semanal
    mostrar_reto_semanal(df_perfil, perfil)
    
    # Verificar si hay celebración de reto pendiente
    if st.session_state.reto_recien_completado:
        reto = st.session_state.reto_recien_completado
        celebrar_logro(f"¡Completaste el reto: {reto['nombre']}! 🎉\nPremio: {reto['recompensa']}", "nivel")
        if activar_sonidos():
            sonido_celebracion()
        st.session_state.reto_recien_completado = None
    
    # Mostrar nuevo logro si existe
    if st.session_state.nuevo_logro:
        logro = LOGROS[st.session_state.nuevo_logro]
        celebrar_logro(f"¡Desbloqueaste: {logro['icono']} {logro['nombre']}!", "nivel")
        if activar_sonidos():
            sonido_celebracion()
        st.session_state.nuevo_logro = None
    
    st.divider()
    
    # Controles de selección
    st.subheader("🎮 ¿Qué quieres leer?")
    
    col_edad, col_modo = st.columns([1, 2])
    
    with col_edad:
        edad = st.slider("👧 Edad", 2, 9, 5)
    
    with col_modo:
        modo = st.radio(
            "📚 Modo",
            ["🎡 Sorpresa", "🌙 Cortito", "⭐ Favoritos", "🆕 Nuevos"],
            horizontal=True,
            help="Sorpresa = cualquier libro, Cortito = menos de 7 min, Favoritos = solo ⭐, Nuevos = nunca leídos"
        )
    
    # Configurar filtros según modo
    if modo == "🌙 Cortito":
        max_duracion = 7
        solo_favoritos = False
        solo_nuevos = False
        modo_key = "cortito"
    elif modo == "⭐ Favoritos":
        max_duracion = None
        solo_favoritos = True
        solo_nuevos = False
        modo_key = "favoritos"
    elif modo == "🆕 Nuevos":
        max_duracion = None
        solo_favoritos = False
        solo_nuevos = True
        modo_key = "nuevos"
    else:  # Sorpresa
        max_duracion = None
        solo_favoritos = False
        solo_nuevos = False
        modo_key = "default"
    
    # Botón de ruleta
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🎡 ¡Girar la ruleta!", use_container_width=True):
        cargar_datos.clear()
        df = cargar_datos()
        
        libro = seleccionar_libro(
            df,
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
            st.session_state.libro_actual = libro.to_dict()
            
            # Obtener títulos para la animación de ruleta
            df_filtrado = df[
                (df["edad_min"] <= edad) &
                (df["edad_max"] >= edad) &
                (df["activa"] == True)
            ]
            
            if solo_favoritos:
                df_filtrado = df_filtrado[df_filtrado["favorito"] == True]
            elif solo_nuevos:
                df_filtrado = df_filtrado[df_filtrado["veces_leido"] == 0]
            elif max_duracion:
                df_filtrado = df_filtrado[df_filtrado["duracion_min"] <= max_duracion]
            
            titulos = df_filtrado["titulo"].tolist()
            
            if len(titulos) < 3:
                titulos = titulos * 3  # Repetir si hay pocos
            
            # Reproducir sonido de ruleta
            if activar_sonidos():
                reproducir_sonido("ruleta")
            
            ruleta_magica(titulos, libro["titulo"])
            st.balloons()
            
            # Sonido de éxito
            if activar_sonidos():
                reproducir_sonido("exito")
    
    # Mostrar libro seleccionado
    if st.session_state.libro_actual is not None:
        libro = st.session_state.libro_actual
        
        # Tarjeta del libro
        es_favorito = libro.get('favorito', False)
        estrella = "⭐" if es_favorito else ""
        
        st.markdown(f"""
        <div style="
            background: white;
            border-radius: 25px;
            padding: 30px;
            margin: 25px 0;
            box-shadow: 0 8px 25px rgba(255,105,180,0.2);
            border: 4px solid #ff69b4;
            text-align: center;
        ">
            <div style="font-size: 50px; margin-bottom: 15px;">📖</div>
            <h2 style="color: #d63384; margin: 10px 0; font-size: 28px;">
                {libro['titulo']} {estrella}
            </h2>
            <div style="
                display: flex;
                justify-content: center;
                gap: 20px;
                margin: 20px 0;
                flex-wrap: wrap;
            ">
                <span style="
                    background: #ffe4ec;
                    padding: 8px 15px;
                    border-radius: 20px;
                    color: #333;
                ">
                    👧 {PERFILES[perfil]} {perfil}
                </span>
                <span style="
                    background: #e3f2fd;
                    padding: 8px 15px;
                    border-radius: 20px;
                    color: #333;
                ">
                    ⏱️ {libro['duracion_min']} min
                </span>
                <span style="
                    background: #f3e5f5;
                    padding: 8px 15px;
                    border-radius: 20px;
                    color: #333;
                ">
                    📍 {libro['ubicacion']}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Botones de acción
        col1, col2 = st.columns(2)
        
        with col1:
            btn_fav_text = "💖 ¡Ya es favorito!" if es_favorito else "⭐ ¡Es mi favorito!"
            btn_fav_disabled = es_favorito
            
            if st.button(btn_fav_text, key="btn_favorito", use_container_width=True, disabled=btn_fav_disabled):
                df_fresh, sheet = get_df()
                df_fresh.loc[df_fresh["id"] == libro["id"], "favorito"] = True
                sheet.update(
                    [df_fresh.columns.values.tolist()] +
                    df_fresh.astype(str).values.tolist()
                )
                cargar_datos.clear()
                
                # Actualizar libro actual
                st.session_state.libro_actual["favorito"] = True
                
                if activar_sonidos():
                    reproducir_sonido("exito")
                
                st.toast("⭐ ¡Favorito guardado!")
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
                
                cargar_datos.clear()
                
                # Verificar nuevos logros
                df_despues, _ = get_df()
                df_perfil_despues = df_despues[df_despues["ultima_lectora"] == perfil].copy()
                
                nuevo_logro = verificar_nuevo_logro(df_perfil_antes, df_perfil_despues)
                if nuevo_logro:
                    st.session_state.nuevo_logro = nuevo_logro
                
                # Verificar reto completado
                reto_nuevo, reto_info = verificar_reto_completado(df_perfil_despues, perfil)
                if reto_nuevo:
                    st.session_state.reto_recien_completado = reto_info
                
                if activar_sonidos():
                    sonido_celebracion()
                
                st.session_state.libro_actual = None
                st.toast("✅ ¡Lectura registrada! 🎉")
                st.rerun()
        
        # Botón para elegir otro
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Elegir otro libro", use_container_width=True):
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
