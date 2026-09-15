# -*- coding: utf-8 -*-
"""views/acerca_de.py - Informacion institucional del proyecto."""

import streamlit as st

LOGO_URL = "https://github.com/GIUSEPPESAN21/LOGO-SAVA/blob/main/LOGO%20COLIBRI.png?raw=true"


def render():
    st.title("Sobre SAVA Lab Inventory")
    st.subheader("Gestion inteligente de inventario para laboratorios de ingenieria")

    st.markdown("""
    **SAVA Lab Inventory** nace para resolver un problema muy concreto de los laboratorios de
    ingenieria: saber en todo momento **que equipos y materiales existen, donde estan y quien
    los tiene prestados**. Usa una jerarquia de codigos de barras (contenedor maestro + items
    hijos) para identificar tanto cajas/kits completos como cada componente individual dentro
    de ellos, y un sistema de roles (estudiante, profesor, maestro) para dar trazabilidad
    completa a cada salida y reingreso.
    """)

    st.markdown("---")
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image(LOGO_URL, width=180, caption="SAVA")
    with col2:
        st.markdown("#### Joseph Javier Sanchez Acuna")
        st.markdown("**CEO - SAVA SOFTWARE FOR ENGINEERING**")
        st.markdown(
            "- **LinkedIn:** [joseph-javier-sánchez-acuña](https://www.linkedin.com/in/joseph-javier-sánchez-acuña-150410275)\n"
            "- **GitHub:** [GIUSEPPESAN21](https://github.com/GIUSEPPESAN21)"
        )
