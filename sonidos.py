# sonidos.py
import streamlit as st


def mostrar_celebracion(tipo="exito"):
    """Muestra una celebración visual (sin sonido)"""
    
    if tipo == "exito":
        st.balloons()
    elif tipo == "logro":
        st.balloons()
        st.snow()
    elif tipo == "racha":
        st.balloons()


def toggle_sonidos():
    """Ya no se necesita - lo dejamos vacío para no romper imports"""
    pass


def activar_sonidos():
    """Ya no se necesita"""
    return False
