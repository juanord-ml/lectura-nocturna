# sonidos.py
import streamlit as st

# URLs de sonidos gratuitos (cortos y divertidos)
SONIDOS = {
    "ruleta": "https://www.soundjay.com/buttons/sounds/button-09a.mp3",
    "exito": "https://www.soundjay.com/buttons/sounds/button-3.mp3",
    "logro": "https://www.soundjay.com/fanfare/sounds/tada-fanfare-a.mp3",
    "click": "https://www.soundjay.com/buttons/sounds/button-16.mp3"
}


def reproducir_sonido(tipo="exito"):
    """Reproduce un sonido según el tipo"""
    
    url = SONIDOS.get(tipo, SONIDOS["exito"])
    
    # Usar HTML audio con autoplay
    st.markdown(f"""
    <audio autoplay>
        <source src="{url}" type="audio/mpeg">
    </audio>
    """, unsafe_allow_html=True)


def sonido_celebracion():
    """Sonido especial para celebraciones grandes"""
    st.markdown("""
    <audio autoplay>
        <source src="https://www.soundjay.com/human/sounds/applause-01.mp3" type="audio/mpeg">
    </audio>
    """, unsafe_allow_html=True)


def activar_sonidos():
    """Verifica si los sonidos están activados"""
    if "sonidos_activos" not in st.session_state:
        st.session_state.sonidos_activos = True
    return st.session_state.sonidos_activos


def toggle_sonidos():
    """Widget para activar/desactivar sonidos"""
    actual = st.session_state.get("sonidos_activos", True)
    
    icono = "🔊" if actual else "🔇"
    
    if st.button(f"{icono}", key="btn_sonido", help="Activar/Desactivar sonidos"):
        st.session_state.sonidos_activos = not actual
        st.rerun()
