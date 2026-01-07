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

    # normalizaciones defensivas
    if "ultima_lectura" in df.columns:
        df["ultima_lectura"] = pd.to_datetime(
            df["ultima_lectura"],
            errors="coerce"
        )

    return df, sheet
