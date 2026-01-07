# historial.py
import streamlit as st
import pandas as pd
from datetime import datetime
import calendar
from gamificacion import (
    calcular_racha, obtener_nivel, obtener_logros_desbloqueados, LOGROS
)


def mostrar_calendario_lecturas(df_perfil, mes=None, año=None):
    """Muestra un calendario visual con los días de lectura"""
    hoy = datetime.now()
    mes = mes or hoy.month
    año = año or hoy.year
    
    # Obtener fechas de lectura
    fechas_lectura = set()
    if not df_perfil.empty:
        fechas_lectura = set(
            pd.to_datetime(df_perfil["ultima_lectura"], errors="coerce")
            .dt.date.dropna()
        )
    
    cal = calendar.monthcalendar(año, mes)
    nombre_mes = calendar.month_name[mes]
    
    # Navegación de meses
    col_nav1, col_nav2, col_nav3 = st.columns([1, 2, 1])
    
    with col_nav1:
        if st.button("◀️ Anterior", key="mes_ant"):
            if mes == 1:
                st.session_state.cal_mes = 12
                st.session_state.cal_año = año - 1
            else:
                st.session_state.cal_mes = mes - 1
            st.rerun()
    
    with col_nav2:
        st.markdown(f"### 📅 {nombre_mes} {año}")
    
    with col_nav3:
        if st.button("Siguiente ▶️", key="mes_sig"):
            if mes == 12:
                st.session_state.cal_mes = 1
                st.session_state.cal_año = año + 1
            else:
                st.session_state.cal_mes = mes + 1
            st.rerun()
    
    # Encabezado días de la semana
    dias_semana = ["L", "M", "X", "J", "V", "S", "D"]
    cols = st.columns(7)
    for i, dia in enumerate(dias_semana):
        cols[i].markdown(f"**{dia}**")
    
    # Días del mes
    for semana in cal:
        cols = st.columns(7)
        for i, dia in enumerate(semana):
            if dia == 0:
                cols[i].write("")
            else:
                fecha = datetime(año, mes, dia).date()
                if fecha in fechas_lectura:
                    cols[i].markdown(f"🌟 **{dia}**")
                elif fecha == hoy.date():
                    cols[i].markdown(f"📍 {dia}")
                else:
                    cols[i].write(f"{dia}")
    
    # Leyenda
    st.caption("🌟 = Día con lectura | 📍 = Hoy")


def mostrar_lista_lecturas(df_perfil):
    """Muestra lista cronológica de lecturas con portadas"""
    if df_perfil.empty:
        st.info("No hay lecturas registradas aún.")
        return
    
    df_ordenado = df_perfil.sort_values("ultima_lectura", ascending=False).head(10)
    
    for _, libro in df_ordenado.iterrows():
        fecha_dt = pd.to_datetime(libro["ultima_lectura"], errors="coerce")
        fecha = fecha_dt.strftime("%d %b %Y") if pd.notna(fecha_dt) else "Sin fecha"
        fav = "⭐" if libro["favorito"] else ""
        
        with st.container(border=True):
            col_img, col_info = st.columns([1, 3])
            
            with col_img:
                portada_url = libro.get("portada_url", "")
                if portada_url and str(portada_url).startswith("http"):
                    st.image(portada_url, width=80)
                else:
                    st.markdown("<div style='font-size: 50px; text-align: center;'>📖</div>", unsafe_allow_html=True)
            
            with col_info:
                st.markdown(f"**{libro['titulo']}** {fav}")
                st.caption(f"📅 {fecha} · ⏱️ {libro['duracion_min']} min · 🔄 {libro['veces_leido']}x")


def mostrar_logros(df_perfil):
    """Muestra logros desbloqueados y bloqueados"""
    st.markdown("### 🏆 Mis Logros")
    
    desbloqueados = obtener_logros_desbloqueados(df_perfil)
    
    cols = st.columns(3)
    for i, (key, logro) in enumerate(LOGROS.items()):
        with cols[i % 3]:
            if key in desbloqueados:
                # CORREGIDO: colores de texto más oscuros
                st.markdown(f"""
                <div style="
                    text-align: center;
                    background: linear-gradient(135deg, #fff9c4, #ffecb3);
                    border-radius: 15px;
                    padding: 15px;
                    margin: 5px;
                    box-shadow: 0 3px 10px rgba(255,193,7,0.3);
                ">
                    <span style="font-size: 40px;">{logro['icono']}</span><br>
                    <strong style="color: #d63384;">{logro['nombre']}</strong><br>
                    <small style="color: #666666;">{logro['desc']}</small>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="
                    text-align: center;
                    background: #f0f0f0;
                    border-radius: 15px;
                    padding: 15px;
                    margin: 5px;
                    opacity: 0.6;
                ">
                    <span style="font-size: 40px;">🔒</span><br>
                    <strong style="color: #666666;">???</strong><br>
                    <small style="color: #888888;">{logro['desc']}</small>
                </div>
                """, unsafe_allow_html=True)


def pagina_historial(df, perfil):
    """Página principal del historial/diario de lecturas"""
    st.header("📖 Mi Diario de Lecturas")
    
    df_perfil = df[df["ultima_lectora"] == perfil].copy()
    
    if df_perfil.empty:
        st.info("¡Aún no hay lecturas! Gira la ruleta para comenzar 🎡")
        return
    
    # Resumen visual
    col1, col2, col3, col4 = st.columns(4)
    
    racha = calcular_racha(df_perfil)
    nivel = obtener_nivel(df_perfil["veces_leido"].sum())
    total_lecturas = df_perfil["veces_leido"].sum()
    minutos = df_perfil["duracion_min"].sum()
    
    col1.metric("🔥 Racha", f"{racha} días")
    col2.metric("📚 Lecturas", total_lecturas)
    col3.metric("⏱️ Minutos", minutos)
    col4.metric("⭐ Nivel", nivel["nombre"])
    
    st.divider()
    
    # Tabs para diferentes vistas
    tab1, tab2, tab3 = st.tabs(["📅 Calendario", "📋 Lista", "🏆 Logros"])
    
    # Inicializar estado del calendario
    if "cal_mes" not in st.session_state:
        st.session_state.cal_mes = datetime.now().month
    if "cal_año" not in st.session_state:
        st.session_state.cal_año = datetime.now().year
    
    with tab1:
        mostrar_calendario_lecturas(
            df_perfil, 
            mes=st.session_state.cal_mes, 
            año=st.session_state.cal_año
        )
    
    with tab2:
        mostrar_lista_lecturas(df_perfil)
    
    with tab3:
        mostrar_logros(df_perfil)
