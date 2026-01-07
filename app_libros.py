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

# Nuevos imports
from sonidos import activar_sonidos, toggle_sonidos
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
    """Widget motivacional de racha usando componentes nativos"""
    
    racha = calcular_racha(df_perfil)
    
    # Configurar mensaje según racha
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
    
    # Usar componentes nativos de Streamlit
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(f"""
            <div style='text-align: center; 
                        background: linear-gradient(135deg, #ff69b422, #ff69b444); 
                        padding: 20px; 
                        border-radius: 20px;
                        border: 3px solid #ff69b4;
                        margin-bottom: 20px;'>
                <div style='font-size: 40px;'>{emoji_fuego}</div>
                <div style='font-size: 36px; font-weight: bold; color: #ff69b4;'>{racha} {"día" if racha == 1 else "días"}</div>
                <div style='font-size: 16px; color: #666;'>{mensaje}</div>
            </div>
            """, unsafe_allow_html=True)


# ---------------- NAVEGACIÓN SIDEBAR ----------------
with st.sidebar:
    st.markdown("""
    <div style='text-align: center; padding: 20px;'>
        <span style='font-size: 60px;'>📚</span>
        <h2 style='color: #ff69b4; margin: 10px 0;'>Mis Libros</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Toggle de sonidos (visual, sin audio real)
    col_sonido, col_texto = st.columns([1, 3])
    with col_sonido:
        toggle_sonidos()
    with col_texto:
        estado = "🔊 On" if st.session_state.get("sonidos_activos", True) else "🔇 Off"
        st.caption(estado)
    
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
    df_perfil_sidebar = df_sidebar[df_sidebar["ultima_lectora"] == perfil]
    
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
    df_perfil = df[df["ultima_lectora"] == perfil].copy()
    
    # Widget de racha
    mostrar_widget_racha(df_perfil, perfil)
    
    # Reto semanal
    mostrar_reto_semanal(df_perfil, perfil)
    
    # Verificar si hay celebración de reto pendiente
    if st.session_state.reto_recien_completado:
        reto = st.session_state.reto_recien_completado
        st.balloons()
        st.success(f"🎉 ¡Completaste el reto: {reto['nombre']}! Premio: {reto['recompensa']}")
        st.session_state.reto_recien_completado = None
    
    # Mostrar nuevo logro si existe
    if st.session_state.nuevo_logro:
        logro = LOGROS[st.session_state.nuevo_logro]
        st.balloons()
        st.success(f"🏆 ¡Desbloqueaste: {logro['icono']} {logro['nombre']}!")
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
            help="Sorpresa=cualquiera, Cortito=<7min, Favoritos=solo ⭐, Nuevos=nunca leídos"
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
    else:
        max_duracion = None
        solo_favoritos = False
        solo_nuevos = False
        modo_key = "default"
    
    # Botón de ruleta
    st.markdown("")
    
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
            
            # Obtener títulos para la animación
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
                titulos = titulos * 3
            
            ruleta_magica(titulos, libro["titulo"])
            st.balloons()
    
    # Mostrar libro seleccionado
    if st.session_state.libro_actual is not None:
        libro = st.session_state.libro_actual
        
        es_favorito = libro.get("favorito", False)
        estrella = "⭐" if es_favorito else ""
        
        # Tarjeta del libro
        st.markdown(f"""
        <div style='
            background: white;
            border-radius: 25px;
            padding: 30px;
            margin: 25px 0;
            box-shadow: 0 8px 25px rgba(255,105,180,0.2);
            border: 4px solid #ff69b4;
            text-align: center;
        '>
            <div style='font-size: 50px; margin-bottom: 15px;'>📖</div>
            <h2 style='color: #d63384; margin: 10px 0; font-size: 28px;'>
                {libro["titulo"]} {estrella}
            </h2>
            <p style='color: #666;'>
                👧 {PERFILES[perfil]} {perfil} · 
                ⏱️ {libro["duracion_min"]} min · 
                📍 {libro["ubicacion"]}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Botones de acción
        col1, col2 = st.columns(2)
        
        with col1:
            btn_fav_text = "💖 ¡Ya es favorito!" if es_favorito else "⭐ ¡Es mi favorito!"
            
            if st.button(btn_fav_text, key="btn_favorito", use_container_width=True, disabled=es_favorito):
                df_fresh, sheet = get_df()
                df_fresh.loc[df_fresh["id"] == libro["id"], "favorito"] = True
                sheet.update(
                    [df_fresh.columns.values.tolist()] +
                    df_fresh.astype(str).values.tolist()
                )
                cargar_datos.clear()
                st.session_state.libro_actual["favorito"] = True
                st.toast("⭐ ¡Favorito guardado!")
                st.rerun()
        
        with col2:
            if st.button("✅ ¡Lo leímos!", key="btn_leido", use_container_width=True):
                # Guardar estado anterior
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
                
                st.session_state.libro_actual = None
                st.balloons()
                st.toast("✅ ¡Lectura registrada! 🎉")
                st.rerun()
        
        # Botón para elegir otro
        st.markdown("")
        if st.button("🔄 Elegir otro libro", use_container_width=True):
            st.session_state.libro_actual = None
            st.rerun()


# ---------------- RENDERIZAR PÁGINA ----------------
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
