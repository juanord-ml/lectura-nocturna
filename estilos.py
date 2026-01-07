# estilos.py
import streamlit as st
import random
import time


def aplicar_tema_infantil():
    """Aplica el tema visual colorido para niñas"""
    st.markdown("""
    <style>
    /* Fondo con gradiente suave */
    .stApp {
        background: linear-gradient(180deg, #fff5f8 0%, #f0f8ff 100%);
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
        color: #ff85a2 !important;
    }
    
    /* Tarjetas redondeadas */
    [data-testid="metric-container"] {
        background: white;
        border-radius: 15px;
        padding: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Radio buttons más grandes */
    .stRadio > div {
        gap: 15px !important;
    }
    
    .stRadio label {
        font-size: 18px !important;
        padding: 8px 16px !important;
        background: white !important;
        border-radius: 15px !important;
        border: 2px solid #ffd1dc !important;
    }
    
    /* Sidebar bonito */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffe4ec 0%, #fff0f5 100%);
    }
    
    /* Tabs bonitos */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 15px;
        background: white;
        border: 2px solid #ffd1dc;
    }
    
    /* Divider rosa */
    hr {
        border-color: #ffd1dc !important;
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
        <span style="font-size: 24px; color: #ff69b4;">
            {mensaje}
        </span>
    </div>
    """, unsafe_allow_html=True)


def ruleta_magica(titulos, ganador):
    """Ruleta con más personalidad y animación"""
    
    placeholder = st.empty()
    
    # Fase 1: Muy rápido con estrellas
    for _ in range(15):
        titulo_random = random.choice(titulos)
        placeholder.markdown(f"""
        <div style="
            text-align: center; 
            font-size: 28px;
            background: white;
            padding: 20px;
            border-radius: 15px;
            border: 3px solid #ffd1dc;
        ">
            ✨ {titulo_random} ✨
        </div>
        """, unsafe_allow_html=True)
        time.sleep(0.05)
    
    # Fase 2: Más lento con suspenso
    for _ in range(8):
        titulo_random = random.choice(titulos)
        placeholder.markdown(f"""
        <div style="
            text-align: center; 
            font-size: 32px;
            background: linear-gradient(135deg, #fff0f5, #ffe4ec);
            padding: 25px;
            border-radius: 15px;
            border: 3px solid #ff69b4;
        ">
            🌟 {titulo_random} 🌟
        </div>
        """, unsafe_allow_html=True)
        time.sleep(0.15)
    
    # Fase 3: Aún más lento
    for _ in range(5):
        titulo_random = random.choice(titulos)
        placeholder.markdown(f"""
        <div style="
            text-align: center; 
            font-size: 34px;
            background: linear-gradient(135deg, #fecfef, #ff9a9e);
            padding: 25px;
            border-radius: 15px;
        ">
            🎯 {titulo_random} 🎯
        </div>
        """, unsafe_allow_html=True)
        time.sleep(0.25)
    
    # Fase 4: Revelar ganador
    placeholder.markdown(f"""
    <div style="
        text-align: center;
        font-size: 36px;
        background: linear-gradient(135deg, #ff9a9e, #fecfef);
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 5px 25px rgba(255,105,180,0.4);
    ">
        🎉 ¡Esta noche leemos! 🎉<br>
        <strong style="font-size: 42px;">📖 {ganador}</strong>
    </div>
    """, unsafe_allow_html=True)
