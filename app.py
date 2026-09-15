# -*- coding: utf-8 -*-
"""
SAVA Lab Inventory
Gestion de inventario y prestamos (checkout/checkin) para laboratorios de
ingenieria, con codigos de barras jerarquicos (contenedor maestro + items
hijos) y login por roles (estudiante / profesor / maestro).
"""

import streamlit as st

from core.storage import LabStorage
from core import auth

st.set_page_config(
    page_title="SAVA Lab Inventory",
    page_icon="🧪",
    layout="wide",
)


@st.cache_data
def load_css():
    try:
        with open("style.css") as f:
            return f.read()
    except FileNotFoundError:
        return ""


css = load_css()
if css:
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


@st.cache_resource
def get_storage():
    return LabStorage()


try:
    storage = get_storage()
except Exception as e:
    st.error(f"**Error critico de inicializacion de la base de datos:** {e}")
    st.stop()

st.session_state.storage = storage
auth.ensure_master_seed(storage)

if "user" not in st.session_state:
    st.session_state.user = None

if not st.session_state.user:
    from views import login
    login.render()
    st.stop()

user = st.session_state.user

from views import inicio, escanear, inventario, prestamos, usuarios, reportes, acerca_de

pages = {
    "inicio": st.Page(inicio.render, title="Inicio", icon="🏠", default=True),
    "escanear": st.Page(escanear.render, title="Escanear", icon="🛰️"),
    "prestamos": st.Page(prestamos.render, title="Prestamos", icon="📋"),
}

if user["role"] in ("profesor", "maestro"):
    pages["inventario"] = st.Page(inventario.render, title="Inventario", icon="📦")
    pages["reportes"] = st.Page(reportes.render, title="Reportes", icon="📊")

if user["role"] == "maestro":
    pages["usuarios"] = st.Page(usuarios.render, title="Usuarios", icon="👥")

pages["acerca_de"] = st.Page(acerca_de.render, title="Acerca de SAVA", icon="🏢")

st.session_state.pages = pages

ROLE_LABELS = {"estudiante": "Estudiante", "profesor": "Profesor", "maestro": "Perfil maestro"}

with st.sidebar:
    st.markdown(
        f"""
        <div class="user-chip">
            <div class="user-avatar">{user['full_name'][:1].upper()}</div>
            <div>
                <div class="user-name">{user['full_name']}</div>
                <div class="user-role role-{user['role']}">{ROLE_LABELS.get(user['role'], user['role'])}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")
    if st.button("🚪 Cerrar sesion", use_container_width=True):
        st.session_state.user = None
        st.rerun()
    st.markdown("---")
    st.caption("© 2026 SAVA Software for Engineering.")

nav = st.navigation(list(pages.values()))
nav.run()
