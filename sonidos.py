# sonidos.py
import streamlit as st

def activar_sonidos():
    """Verifica si los sonidos están activados"""
    if "sonidos_activos" not in st.session_state:
        st.session_state.sonidos_activos = True
    return st.session_state.sonidos_activos


def toggle_sonidos():
    """Widget para activar/desactivar sonidos"""
    if "sonidos_activos" not in st.session_state:
        st.session_state.sonidos_activos = True
    
    actual = st.session_state.sonidos_activos
    icono = "🔊" if actual else "🔇"
    
    if st.button(f"{icono}", key="btn_sonido", help="Activar/Desactivar sonidos"):
        st.session_state.sonidos_activos = not actual
        st.rerun()


def reproducir_sonido(tipo="exito"):
    """
    Nota: Los navegadores bloquean autoplay de audio.
    Esta función ahora solo muestra feedback visual.
    El audio real requiere interacción del usuario.
    """
    pass  # Los sonidos automáticos no funcionan bien en web


def sonido_celebracion():
    """Celebración sin audio (los navegadores lo bloquean)"""
    pass  # Usamos st.balloons() en su lugar
