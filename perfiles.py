# perfiles.py
import streamlit as st
from gamificacion import obtener_nivel, obtener_siguiente_nivel, calcular_racha, NIVELES

# ---------------- AVATARES ----------------
AVATARES = {
    "Clara": {
        "opciones": ["🐭", "🦄", "🐱", "🦋", "🐰", "🧚‍♀️"],
        "fondos": ["🌸", "🌈", "⭐", "🌙", "🦩", "🍦"]
    },
    "Gracia": {
        "opciones": ["🐥", "🦊", "🐻", "🌻", "🐸", "🧜‍♀️"],
        "fondos": ["🌻", "☀️", "🎀", "💜", "🌺", "🍭"]
    }
}


def inicializar_avatar_state():
    """Inicializa el estado de avatares si no existe"""
    if "avatares" not in st.session_state:
        st.session_state.avatares = {
            "Clara": {"avatar": "🐭", "fondo": "🌸"},
            "Gracia": {"avatar": "🐥", "fondo": "🌻"}
        }


def pagina_perfil(perfil, df_perfil):
    """Página de perfil con avatar y estadísticas"""
    inicializar_avatar_state()
    
    st.header(f"👤 Mi Perfil: {perfil}")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Selector de avatar
        avatar_actual = st.session_state.avatares[perfil]["avatar"]
        fondo_actual = st.session_state.avatares[perfil]["fondo"]
        
        nuevo_avatar = st.selectbox(
            "🎭 Mi personaje",
            AVATARES[perfil]["opciones"],
            index=AVATARES[perfil]["opciones"].index(avatar_actual) if avatar_actual in AVATARES[perfil]["opciones"] else 0,
            key=f"avatar_{perfil}"
        )
        
        nuevo_fondo = st.selectbox(
            "🖼️ Mi fondo",
            AVATARES[perfil]["fondos"],
            index=AVATARES[perfil]["fondos"].index(fondo_actual) if fondo_actual in AVATARES[perfil]["fondos"] else 0,
            key=f"fondo_{perfil}"
        )
        
        # Guardar cambios
        st.session_state.avatares[perfil]["avatar"] = nuevo_avatar
        st.session_state.avatares[perfil]["fondo"] = nuevo_fondo
        
        # Avatar grande visual - CORREGIDO COLOR
        st.markdown(f"""
        <div style="
            font-size: 80px; 
            text-align: center;
            background: linear-gradient(135deg, #fff0f5, #ffe4ec);
            border-radius: 20px;
            padding: 20px;
            margin: 10px 0;
            box-shadow: 0 4px 15px rgba(255,105,180,0.2);
        ">
            {nuevo_fondo}<br>{nuevo_avatar}
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if df_perfil.empty:
            st.info("¡Aún no hay lecturas! Gira la ruleta para comenzar 🎡")
            total_leidos = 0
        else:
            total_leidos = df_perfil["veces_leido"].sum()
        
        nivel = obtener_nivel(total_leidos)
        
        # CORREGIDO: color de texto más oscuro
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #fff9c4, #ffecb3);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            margin-bottom: 20px;
        ">
            <span style="font-size: 50px;">{nivel['icono']}</span>
            <h2 style="margin: 10px 0; color: #d63384 !important;">Nivel {nivel['nivel']}: {nivel['nombre']}</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Barra de progreso al siguiente nivel
        siguiente = obtener_siguiente_nivel(total_leidos)
        if siguiente:
            progreso = total_leidos / siguiente["libros"]
            st.progress(min(progreso, 1.0))
            st.caption(f"📚 {total_leidos}/{siguiente['libros']} lecturas para **{siguiente['icono']} {siguiente['nombre']}**")
        else:
            st.success("🎉 ¡Has alcanzado el nivel máximo!")
        
        st.divider()
        
        # Estadísticas rápidas
        if not df_perfil.empty:
            racha = calcular_racha(df_perfil)
            favoritos = df_perfil[df_perfil["favorito"] == True].shape[0]
            minutos = df_perfil["duracion_min"].sum()
            
            c1, c2, c3 = st.columns(3)
            c1.metric("🔥 Racha", f"{racha} días")
            c2.metric("⭐ Favoritos", favoritos)
            c3.metric("⏱️ Minutos", minutos)
