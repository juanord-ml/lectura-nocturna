import streamlit as st
import pandas as pd
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

# ---------------- PERFILES ----------------
PERFILES = {
    "Clara": "🐭",
    "Gracia": "🐥"
}

# ---------------- DATA ----------------
df = pd.read_csv("catalogo_libros.csv", parse_dates=["ultima_lectura"])

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

    libro = seleccionar_libro(
        edad_nina=edad,
        max_duracion=max_duracion,
        permitir_interactivo=True
    )

    if libro is None:
        st.warning("No hay libros elegibles hoy.")
    else:
        titulos = df[
            (df["edad_min"] <= edad) &
            (df["edad_max"] >= edad) &
            (df["activa"] == True)
        ]["titulo"].tolist()

        ruleta_visual(titulos, libro["titulo"])
        st.balloons()

        st.markdown(f"""
        ### 📖 {libro['titulo']}
        - 👧 Lectora: **{PERFILES[perfil]} {perfil}**
        - ⏱️ {libro['duracion_min']} min
        - 📍 {libro['ubicacion']}
        """)

        st.divider()

        col1, col2 = st.columns(2)

        with col1:
            if st.button("⭐ Favorito"):
                df.loc[df["id"] == libro["id"], "favorito"] = True
                df.to_csv("catalogo_libros.csv", index=False)
                st.toast("Favorito guardado")

        with col2:
            if st.button("✅ Leído hoy"):
                idx = df["id"] == libro["id"]
                df.loc[idx, "ultima_lectura"] = datetime.now()
                df.loc[idx, "veces_leido"] += 1
                df.loc[idx, "ultima_lectora"] = perfil
                df.to_csv("catalogo_libros.csv", index=False)
                st.toast("Lectura registrada")

# ---------------- ESTADÍSTICAS ----------------
st.divider()
st.header("📊 Estadísticas")

for hija, icono in PERFILES.items():
    sub = df[df["ultima_lectora"] == hija]

    st.subheader(f"{icono} {hija}")

    if sub.empty:
        st.write("Sin lecturas aún.")
        continue

    col1, col2, col3 = st.columns(3)

    col1.metric("📚 Libros leídos", sub.shape[0])
    col2.metric("⭐ Favoritos", sub[sub["favorito"] == True].shape[0])
    col3.metric("⏱️ Tiempo total",
                f"{sub['duracion_min'].sum()} min")

    st.markdown("**Top libros**")
    st.dataframe(
        sub[["titulo", "veces_leido"]]
        .sort_values("veces_leido", ascending=False)
        .head(5),
        hide_index=True
    )
