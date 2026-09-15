# -*- coding: utf-8 -*-
"""views/acerca_de.py - Informacion del proyecto y como usarlo."""

import streamlit as st

from core.labels import ITEM_TYPE_NAMES
from core.ui import centered_logo, page_header

LOGO_URL = (
    "https://upload.wikimedia.org/wikipedia/commons/d/db/"
    "Logotipo_de_la_Corporaci%C3%B3n_Universitaria_Minuto_de_Dios.svg"
)


def render():
    centered_logo(LOGO_URL, width=130, caption="UNIMINUTO")
    page_header(
        "Inventario de Laboratorio UNIMINUTO",
        subtitle="Trazabilidad de equipos y materiales del laboratorio de ingeniería",
    )

    st.markdown(
        """
        <p style="text-align:center; max-width:760px; margin:0 auto 1.5rem auto;">
        Este sistema fue creado para el <b>laboratorio de ingeniería de UNIMINUTO</b>, donde
        conviven muchos tipos de productos identificados con una serie propia de códigos
        de barras. Su objetivo es saber en todo momento <b>qué equipos y materiales existen,
        dónde están y quién los tiene prestados</b>, sin depender de planillas sueltas.
        </p>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<h3 style="text-align:center;">¿Cómo funciona?</h3>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f'<div style="text-align:center;">'
            f'<h5>🗄️ {ITEM_TYPE_NAMES["master"]}</h5>'
            f"<p>La caja, kit o gabinete físico que agrupa productos relacionados.</p>"
            f"</div>",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f'<div style="text-align:center;">'
            f'<h5>🧩 {ITEM_TYPE_NAMES["child"]}</h5>'
            f"<p>Una subdivisión dentro de un Contenedor Principal para una característica "
            f"concreta (ej. \"Resistencias 220 Ω\", \"Tornillos M4\").</p>"
            f"</div>",
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f'<div style="text-align:center;">'
            f'<h5>🔹 {ITEM_TYPE_NAMES["standalone"]}</h5>'
            f"<p>Un producto con su propio código, sin contenedor.</p>"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown('<h3 style="text-align:center;">Roles institucionales</h3>', unsafe_allow_html=True)
    r1, r2, r3 = st.columns(3)
    with r1:
        st.markdown(
            '<div style="text-align:center;"><h5>🎓 Estudiante</h5>'
            "<p>Escanea, solicita salida y reingresa lo que él mismo tomó prestado.</p></div>",
            unsafe_allow_html=True,
        )
    with r2:
        st.markdown(
            '<div style="text-align:center;"><h5>👨‍🏫 Profesor</h5>'
            "<p>Administra el inventario, registra préstamos de cualquiera y ve reportes.</p></div>",
            unsafe_allow_html=True,
        )
    with r3:
        st.markdown(
            '<div style="text-align:center;"><h5>🔐 Perfil maestro</h5>'
            "<p>Gestiona usuarios, roles y tiene visibilidad total del laboratorio.</p></div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown(
        '<p style="text-align:center; color: var(--subtle-text-color);">'
        "Para dudas sobre el uso del sistema o solicitudes de soporte, contacta al "
        "administrador del laboratorio (perfil maestro) desde tu programa académico.</p>",
        unsafe_allow_html=True,
    )
