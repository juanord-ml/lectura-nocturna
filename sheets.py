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

# --- CAST DE TIPOS (CRÍTICO) ---
    INT_COLS = [
    "id",
    "edad_min",
    "edad_max",
    "duracion_min",
    "veces_leido"
    ]

    BOOL_COLS = [
    "interactivo",
    "favorito",
    "activa"
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


    # normalizaciones defensivas
    if "ultima_lectura" in df.columns:
        df["ultima_lectura"] = pd.to_datetime(
            df["ultima_lectura"],
            errors="coerce"
        )

    return df, sheet
