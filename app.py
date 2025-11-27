import streamlit as st
import pandas as pd
import folium
from folium.features import DivIcon
from streamlit_folium import st_folium
import base64
from pathlib import Path
import html

st.set_page_config(layout="wide", page_title="Mapa Interativo das Lojas")

st.title("🗺️ Mapa Interativo das Lojas — Hover mostra foto da fachada")

# --------------------------------------------------------------------
# CONFIGURAÇÃO DE ARQUIVOS
# --------------------------------------------------------------------
CSV_PATH = "lojas.csv"
IMAGES_DIR = Path("images")   # pasta onde suas imagens devem estar

# --------------------------------------------------------------------
# CARREGAR DADOS
# --------------------------------------------------------------------
@st.cache_data
def load_data():
    return pd.read_csv(CSV_PATH)

try:
    df = load_data()
except:
    st.error("Erro ao carregar lojas.csv — verifique se está no mesmo diretório.")
    st.stop()

# --------------------------------------------------------------------
# FUNÇÃO: construir HTML para a imagem do tooltip (hover)
# --------------------------------------------------------------------
def build_tooltip_html(row, thumb_width=160):
    img_name = str(row["image"])
    img_path = IMAGES_DIR / img_name

    if img_path.exists():
        with open(img_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            mime = "image/jpeg"
            img_tag = f'<img src="data:{mime};base64,{b64}" style="width:{thumb_width}px; border-radius:8px; margin-bottom:6px;" />'
    else:
        img_tag = f'<div style="width:{thumb_width}px; height:100px; background:#ddd; display:flex; align-items:center; justify-content:center; border-radius:6px;">No Image</div>'

    name = html.escape(str(row["name"]))

    return f"""
    <div style="font-family:Arial; max-width:{thumb_width}px;">
        {img_tag}
        <div style="font-weight:700; margin-top:4px;">{name}</div>
    </div>
    """

# --------------------------------------------------------------------
# GERAR MAPA
# --------------------------------------------------------------------
# Se lat/lon não estiverem preenchidos, centralizar na Felipe Schmidt
if df["lat"].notna().sum() == 0:
    center_lat, center_lon = -27.59539, -48.54805
else:
    center_lat = df["lat"].mean()
    center_lon = df["lon"].mean()

m = folium.Map(location=[center_lat, center_lon], zoom_start=16, tiles="OpenStreetMap")

# --------------------------------------------------------------------
# ADICIONAR MARCADORES
# --------------------------------------------------------------------
for _, row in df.iterrows():
    lat = row["lat"]
    lon = row["lon"]

    if pd.isna(lat) or pd.isna(lon):
        continue

    tooltip_html = build_tooltip_html(row, thumb_width=160)
    tooltip = folium.Tooltip(tooltip_html)

    # Popup grande
    img_path = IMAGES_DIR / row["image"]
    if img_path.exists():
        with open(img_path, "rb") as f:
            data = f.read()
        b64 = base64.b64encode(data).decode()
        mime = "image/jpeg"

        popup_html = f"""
        <div style="width:280px;">
            <img src="data:{mime};base64,{b64}" style="width:100%; border-radius:8px; margin-bottom:8px;" />
            <h5 style="margin:0; font-family:Arial;">{row['name']}</h5>
        </div>
        """
    else:
        popup_html = f"<b>{row['name']}</b><br>Sem foto disponível."

    popup = folium.Popup(popup_html, max_width=300)

    folium.Marker(
        [lat, lon],
        tooltip=tooltip,
        popup=popup,
        icon=folium.Icon(color="purple", icon="info-sign")
    ).add_to(m)

# --------------------------------------------------------------------
# MOSTRAR
# --------------------------------------------------------------------
with st.expander("📄 Ver dados carregados"):
    st.dataframe(df)

st_folium(m, width=1200, height=750)
