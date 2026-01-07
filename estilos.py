# estilos.py
import streamlit as st
import random
import time


def aplicar_tema_infantil():
    """Aplica el tema visual colorido para niñas - OPTIMIZADO PARA MÓVIL"""
    st.markdown("""
    <style>
    /* Fondo con gradiente suave */
    .stApp {
        background: linear-gradient(180deg, #fff5f8 0%, #f0f8ff 100%);
    }
    
    /* ===== CORRECCIÓN PRINCIPAL: TEXTOS VISIBLES ===== */
    
    /* Forzar texto oscuro en toda la app */
    .stApp, .stApp * {
        color: #333333 !important;
    }
    
    /* Labels de los inputs */
    .stRadio > label,
    .stSelectbox > label,
    .stSlider > label,
    .stCheckbox > label,
    .stTextInput > label,
    .stNumberInput > label {
        color: #ff69b4 !important;
        font-weight: 600 !important;
        font-size: 16px !important;
    }
    
    /* Texto dentro de radio buttons */
    .stRadio label span,
    .stRadio [data-testid="stMarkdownContainer"] p {
        color: #333333 !important;
        font-size: 16px !important;
    }
    
    /* Texto de opciones en selectbox */
    .stSelectbox [data-testid="stMarkdownContainer"] p {
        color: #333333 !important;
    }
    
    /* Slider - etiqueta y valor */
    .stSlider label,
    .stSlider [data-testid="stMarkdownContainer"] {
        color: #333333 !important;
    }
    
    /* Botones más divertidos */
    .stButton > button {
        border-radius: 25px !important;
        border: 3px solid #ff69b4 !important;
        background: linear-gradient(90deg, #ff9a9e, #fecfef) !important;
        color: white !important;
        font-weight: bold !important;
        font-size: 18px !important;
        padding: 15px 30px !important;
        transition: transform 0.2s !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2) !important;
    }
    
    .stButton > button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 5px 20px rgba(255,105,180,0.4) !important;
    }
    
    /* Títulos con estilo */
    h1 {
        color: #ff69b4 !important;
        text-shadow: 2px 2px 4px rgba(255,105,180,0.3);
    }
    
    h2, h3 {
        color: #e91e8c !important;
    }
    
    /* Métricas/estadísticas */
    [data-testid="metric-container"] {
        background: white;
        border-radius: 15px;
        padding: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    [data-testid="metric-container"] label {
        color: #666666 !important;
    }
    
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #ff69b4 !important;
    }
    
    /* Radio buttons - contenedor */
    .stRadio > div {
        gap: 10px !important;
    }
    
    .stRadio > div > label {
        font-size: 16px !important;
        padding: 8px 16px !important;
        background: white !important;
        border-radius: 15px !important;
        border: 2px solid #ffd1dc !important;
        color: #333333 !important;
    }
    
    /* Sidebar bonito */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffe4ec 0%, #fff0f5 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: #333333 !important;
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #ff69b4 !important;
    }
    
    /* Tabs bonitos */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 15px;
        background: white;
        border: 2px solid #ffd1dc;
        color: #333333 !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: #ff69b4 !important;
        color: white !important;
    }
    
    /* Divider rosa */
    hr {
        border-color: #ffd1dc !important;
    }
    
    /* Captions y texto pequeño */
    .stCaption, small, .caption {
        color: #666666 !important;
    }
    
    /* Info, warning, success boxes */
    .stAlert {
        color: #333333 !important;
    }
    
    /* DataFrame */
    .stDataFrame {
        color: #333333 !important;
    }
    
    /* ===== MEJORAS MÓVIL ===== */
    @media (max-width: 768px) {
        .stButton > button {
            font-size: 16px !important;
            padding: 12px 20px !important;
        }
        
        h1 {
            font-size: 28px !important;
        }
        
        h2 {
            font-size: 22px !important;
        }
        
        .stRadio > div > label {
            font-size: 14px !important;
            padding: 6px 12px !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)


def celebrar_logro(mensaje, tipo="lectura"):
    """Celebración visual cuando hay un logro"""
    
    efectos = {
        "lectura": "🎉📚⭐🌟✨",
        "racha": "🔥⚡💪🏆🎯",
        "nivel": "👑🎊🏰🌈💫",
        "favorito": "💖💝💗💕❤️"
    }
    
    emojis = efectos.get(tipo, efectos["lectura"])
    
    st.balloons()
    st.markdown(f"""
    <div style="
        text-align: center;
        font-size: 40px;
        padding: 20px;
        background: linear-gradient(135deg, #fff9c4, #ffecb3);
        border-radius: 20px;
        margin: 20px 0;
        box-shadow: 0 5px 20px rgba(255,193,7,0.3);
    ">
        {emojis}<br>
        <span style="font-size: 24px; color: #d63384; font-weight: bold;">
            {mensaje}
        </span>
    </div>
    """, unsafe_allow_html=True)


# estilos.py - Nueva versión de ruleta_magica con portadas

def ruleta_magica(titulos, ganador, portada_ganador=None):
    """Ruleta con animación - ahora acepta portada opcional"""
    
    placeholder = st.empty()
    
    # Fase 1: Muy rápido
    for _ in range(15):
        titulo_random = random.choice(titulos)
        with placeholder.container():
            st.markdown(f"""
            <div style='
                text-align: center; 
                font-size: 24px;
                background: white;
                padding: 20px;
                border-radius: 15px;
                border: 3px solid #ffd1dc;
                color: #333;
            '>
                ✨ {titulo_random} ✨
            </div>
            """, unsafe_allow_html=True)
        time.sleep(0.05)
    
    # Fase 2: Más lento
    for _ in range(8):
        titulo_random = random.choice(titulos)
        with placeholder.container():
            st.markdown(f"""
            <div style='
                text-align: center; 
                font-size: 28px;
                background: linear-gradient(135deg, #fff0f5, #ffe4ec);
                padding: 25px;
                border-radius: 15px;
                border: 3px solid #ff69b4;
                color: #333;
            '>
                🌟 {titulo_random} 🌟
            </div>
            """, unsafe_allow_html=True)
        time.sleep(0.15)
    
    # Fase 3: Aún más lento
    for _ in range(5):
        titulo_random = random.choice(titulos)
        with placeholder.container():
            st.markdown(f"""
            <div style='
                text-align: center; 
                font-size: 30px;
                background: linear-gradient(135deg, #fecfef, #ff9a9e);
                padding: 25px;
                border-radius: 15px;
                color: #333;
            '>
                🎯 {titulo_random} 🎯
            </div>
            """, unsafe_allow_html=True)
        time.sleep(0.25)
    
    # Fase 4: Revelar ganador CON PORTADA
    with placeholder.container():
        st.markdown(f"""
        <div style='
            text-align: center;
            font-size: 28px;
            background: linear-gradient(135deg, #ff9a9e, #fecfef);
            border-radius: 20px;
            padding: 20px;
            box-shadow: 0 5px 25px rgba(255,105,180,0.4);
            color: #333;
        '>
            🎉 ¡Esta noche leemos! 🎉
        </div>
        """, unsafe_allow_html=True)
        
        # Mostrar portada si existe
        if portada_ganador and str(portada_ganador).startswith("http"):
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.image(portada_ganador, width=200)
        
        st.markdown(f"""
        <div style='
            text-align: center;
            font-size: 32px;
            font-weight: bold;
            color: #d63384;
            margin-top: 10px;
        '>
            📖 {ganador}
        </div>
        """, unsafe_allow_html=True)

# Agregar al final de estilos.py

def mostrar_portada(url, ancho=200):
    """Muestra la portada de un libro"""
    if url and str(url).startswith("http"):
        st.image(url, width=ancho)
    else:
        # Placeholder si no hay imagen
        st.markdown(f"""
        <div style='
            width: {ancho}px;
            height: {int(ancho * 1.4)}px;
            background: linear-gradient(135deg, #ff69b4, #ffd1dc);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto;
        '>
            <span style='font-size: 60px;'>📖</span>
        </div>
        """, unsafe_allow_html=True)
