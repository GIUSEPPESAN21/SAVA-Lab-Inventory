# -*- coding: utf-8 -*-
"""views/acerca_de.py - Informacion del proyecto y como usarlo."""

import streamlit as st

LOGO_URL = (
    "https://upload.wikimedia.org/wikipedia/commons/d/db/"
    "Logotipo_de_la_Corporaci%C3%B3n_Universitaria_Minuto_de_Dios.svg"
)


def render():
    col_logo, col_title = st.columns([1, 4])
    with col_logo:
        st.image(LOGO_URL, width=140, caption="UNIMINUTO")
    with col_title:
        st.title("Inventario de Laboratorio UNIMINUTO")
        st.subheader("Trazabilidad de equipos y materiales del laboratorio de ingeniería")

    st.markdown("---")

    st.markdown("""
    Este sistema fue creado para el **laboratorio de ingeniería de UNIMINUTO**, donde
    conviven muchos tipos de productos identificados con una serie propia de códigos
    de barras. Su objetivo es saber en todo momento **qué equipos y materiales existen,
    dónde están y quién los tiene prestados**, sin depender de planillas sueltas.
    """)

    st.subheader("¿Cómo funciona?")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("##### 📦 Códigos jerárquicos")
        st.markdown(
            "Un **contenedor maestro** (una caja o kit) agrupa varios **ítems hijos**, "
            "cada uno con su propio código de barras individual."
        )
    with c2:
        st.markdown("##### 🔁 Salida y reingreso")
        st.markdown(
            "Cada préstamo queda registrado: quién lo tomó, cuándo y cuándo debe "
            "devolverlo. La disponibilidad se calcula siempre en tiempo real."
        )
    with c3:
        st.markdown("##### 👥 Roles institucionales")
        st.markdown(
            "Estudiantes, profesores y el perfil maestro tienen permisos distintos, "
            "usando el correo institucional de UNIMINUTO para identificarse."
        )

    st.markdown("---")
    st.subheader("Soporte")
    st.markdown(
        "Para dudas sobre el uso del sistema o solicitudes de soporte, contacta al "
        "administrador del laboratorio (perfil maestro) desde tu programa académico."
    )
