# app_libros.py
import streamlit as st
import pandas as pd
from sheets import get_df
import random
import time
from datetime import datetime
from eleccion_libros import seleccionar_libro

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="📖 Lectura de Hoy",
    page_icon="📚",
    layout="centered"
)

# ---------------- SESSION STATE ----------------
if "libro_actual" not in st.session_state:
    st.session_state.libro_actual = None

# ---------------- PERFILES ----------------
PERFILES = {
    "Clara": "🐭",
    "Gracia": "🐥"
}

# ---------------- DATA ----------------
@st.cache_data(ttl=60)  # Cache por 60 segundos
def cargar_datos():
    df, _ = get_df()
    return df

def obtener_sheet():
    _, sheet = get_df()
    return sheet

df = cargar_datos()

st.title("📖 Noche de Lectura")

# ---------------- PERFIL ----------------
perfil = st.radio(
    "¿Quién lee hoy?",
    list(PERFILES.keys()),
    horizontal=True,
    format_func=lambda x: f"{PERFILES[x]} {x}"
)

# ---------------- CONTROLES ----------------
edad = st.slider("Edad", 2, 9, 5)

modo = st.radio(
    "Modo",
    ["🎡 Sorpresa", "🌙 Cortito"],
    horizontal=True
)

max_duracion = 7 if modo == "🌙 Cortito" else None

# ---------------- RULETA ----------------
def ruleta_visual(titulos, ganador):
    placeholder = st.empty()

    for _ in range(20):
        placeholder.markdown(f"## 🎡 {random.choice(titulos)}")
        time.sleep(0.05)

    for _ in range(10):
        placeholder.markdown(f"## 🎡 {random.choice(titulos)}")
        time.sleep(0.12)

    placeholder.markdown(f"## 🎉 **{ganador}**")

# ---------------- SELECCIÓN ----------------
if st.button("🎡 Girar la ruleta", use_container_width=True):
    # Limpiar cache para obtener datos frescos
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
        st.warning("No hay libros elegibles hoy.")
    else:
        # Guardar como diccionario para evitar problemas de serialización
        st.session_state.libro_actual = libro.to_dict()

        titulos = df[
            (df["edad_min"] <= edad) &
            (df["edad_max"] >= edad) &
            (df["activa"] == True)
        ]["titulo"].tolist()

        ruleta_visual(titulos, libro["titulo"])
        st.balloons()

# ---------------- MOSTRAR LIBRO SELECCIONADO (FUERA del if del botón) ----------------
if st.session_state.libro_actual is not None:
    libro = st.session_state.libro_actual
    
    st.markdown(f"""
    ### 📖 {libro['titulo']}
    - 👧 Lectora: **{PERFILES[perfil]} {perfil}**
    - ⏱️ {libro['duracion_min']} min
    - 📍 {libro['ubicacion']}
    """)

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        if st.button("⭐ Favorito", key="btn_favorito"):
            df_fresh, sheet = get_df()
            df_fresh.loc[df_fresh["id"] == libro["id"], "favorito"] = True
            sheet.update(
                [df_fresh.columns.values.tolist()] +
                df_fresh.astype(str).values.tolist()
            )
            cargar_datos.clear()  # Limpiar cache
            st.toast("⭐ Favorito guardado!")
            st.rerun()

    with col2:
        if st.button("✅ Leído hoy", key="btn_leido"):
            df_fresh, sheet = get_df()
            idx = df_fresh["id"] == libro["id"]
            df_fresh.loc[idx, "ultima_lectura"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            df_fresh.loc[idx, "veces_leido"] = df_fresh.loc[idx, "veces_leido"] + 1
            df_fresh.loc[idx, "ultima_lectora"] = perfil
            sheet.update(
                [df_fresh.columns.values.tolist()] +
                df_fresh.astype(str).values.tolist()
            )
            cargar_datos.clear()  # Limpiar cache
            st.toast("✅ Lectura registrada!")
            st.session_state.libro_actual = None  # Limpiar selección
            st.rerun()

# ---------------- ESTADÍSTICAS ----------------
st.divider()
st.header("📊 Estadísticas")

# Recargar datos frescos para estadísticas
df_stats = cargar_datos()

for hija, icono in PERFILES.items():
    sub = df_stats[df_stats["ultima_lectora"] == hija]

    st.subheader(f"{icono} {hija}")

    if sub.empty:
        st.write("Sin lecturas aún.")
        continue

    col1, col2, col3 = st.columns(3)

    col1.metric("📚 Libros leídos", sub.shape[0])
    col2.metric("⭐ Favoritos", sub[sub["favorito"] == True].shape[0])
    col3.metric("⏱️ Tiempo total", f"{sub['duracion_min'].sum()} min")

    st.markdown("**Top libros**")
    st.dataframe(
        sub[["titulo", "veces_leido"]]
        .sort_values("veces_leido", ascending=False)
        .head(5),
        hide_index=True
    )



