# sheets.py
import gspread
import pandas as pd
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials


SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]


def get_df(sheet_name="Catalogo Libros Hijas"):
    """
    Devuelve:
    - df: DataFrame con el catálogo
    - sheet: objeto sheet para escritura
    """

    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["gcp_service_account"],
        SCOPE
    )

    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).sheet1

    data = sheet.get_all_records()
    df = pd.DataFrame(data)

    # --- CAST DE TIPOS ---
    INT_COLS = [
        "id",
        "edad_min",
        "edad_max",
        "duracion_min",
        "veces_clara",      # NUEVO
        "veces_gracia"      # NUEVO
    ]

    BOOL_COLS = [
        "interactivo",
        "activa",
        "favorito_clara",   # NUEVO
        "favorito_gracia"   # NUEVO
    ]

    DATE_COLS = [
        "ultima_clara",     # NUEVO
        "ultima_gracia"     # NUEVO
    ]

    for col in INT_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    for col in BOOL_COLS:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.upper()
                .isin(["TRUE", "1", "SI", "YES"])
            )

    for col in DATE_COLS:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    return df, sheet


def get_columnas_perfil(perfil):
    """Retorna los nombres de columnas para un perfil específico"""
    perfil_lower = perfil.lower()
    return {
        "favorito": f"favorito_{perfil_lower}",
        "veces": f"veces_{perfil_lower}",
        "ultima": f"ultima_{perfil_lower}"
    }
