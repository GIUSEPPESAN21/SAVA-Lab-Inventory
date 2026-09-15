# -*- coding: utf-8 -*-
"""Prueba de humo end-to-end usando streamlit.testing.v1.AppTest: simula un
login real (sin navegador) contra la app completa, con la cuenta maestra
sembrada desde secrets locales de prueba."""

import pytest

pytest.importorskip("streamlit.testing.v1")

from streamlit.testing.v1 import AppTest


def test_login_screen_renders_without_exceptions():
    at = AppTest.from_file("app.py")
    at.run()
    assert not at.exception
    assert any("SAVA Lab Inventory" in md.value for md in at.markdown)


def test_master_login_succeeds_and_shows_navigation():
    at = AppTest.from_file("app.py")
    at.run()
    assert not at.exception

    # Los widgets dentro de un st.form no exponen una key legible facil de
    # adivinar; se localizan por orden dentro del primer formulario (login).
    email_input = at.text_input[0]
    password_input = at.text_input[1]
    email_input.input("admin@uniminuto.edu.co")
    password_input.input("TestPassword123")
    at.button[0].click().run()

    assert not at.exception
    assert at.session_state["user"] is not None
    assert at.session_state["user"]["role"] == "maestro"


def test_student_self_registration_end_to_end():
    at = AppTest.from_file("app.py")
    at.run()
    assert not at.exception

    # Widgets del formulario de registro (2da pestana) aparecen despues de
    # los del login (1era pestana) en el orden de ejecucion del script.
    full_name_input, email_input, program_input, pw_input, pw2_input = at.text_input[2:7]
    full_name_input.input("Estudiante de Prueba")
    email_input.input("estudiante.prueba@uniandes.edu.co")
    program_input.input("Ingenieria Industrial")
    pw_input.input("ClaveSegura123")
    pw2_input.input("ClaveSegura123")
    at.button[1].click().run()

    assert not at.exception
    assert any("estudiante" in s.value.lower() for s in at.success)
