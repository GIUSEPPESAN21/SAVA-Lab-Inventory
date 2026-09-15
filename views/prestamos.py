# -*- coding: utf-8 -*-
"""views/prestamos.py - Panel de prestamos: 'Mis prestamos' para estudiantes,
'Quien tiene que' completo para profesor/maestro."""

import streamlit as st

from core import loans as loans_core


def _loan_row(storage, loan: dict, user: dict, key_prefix: str):
    overdue = loans_core.is_overdue(loan)
    with st.container(border=True):
        c1, c2, c3 = st.columns([3, 2, 1])
        tag = " ⚠️ VENCIDO" if overdue else ""
        c1.markdown(f"**{loan['item_name']}** x{loan['quantity']}{tag}")
        c1.caption(f"Prestado a: {loan['user_name']} ({loan['user_role']})")
        checkout_at = loan.get("checkout_at")
        c2.caption(f"Salida: {checkout_at.strftime('%d/%m/%Y %H:%M') if checkout_at else 'N/A'}")
        expected = loan.get("expected_return_at")
        if expected:
            c2.caption(f"Devolver antes de: {expected.strftime('%d/%m/%Y')}")
        can_checkin = user["role"] != "estudiante" or loan["user_id"] == user["id"]
        if can_checkin and c3.button("Reingresar", key=f"{key_prefix}_{loan['id']}", use_container_width=True):
            ok, msg = loans_core.checkin(storage, loan["id"], user)
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)
        if loan.get("notes"):
            st.caption(f"Notas: {loan['notes']}")


def render():
    storage = st.session_state.storage
    user = st.session_state.user

    if user["role"] == "estudiante":
        st.subheader("📋 Mis prestamos")
        loans = storage.get_open_loans_for_user(user["id"])
        if not loans:
            st.info("No tienes prestamos activos.")
        for loan in loans:
            _loan_row(storage, loan, user, "mine")
        return

    tab_activos, tab_historial = st.tabs(["📋 Prestamos activos", "🗂️ Historial completo"])

    with tab_activos:
        loans = storage.get_all_loans(status="out")
        overdue_count = len([l for l in loans if loans_core.is_overdue(l)])
        c1, c2 = st.columns(2)
        c1.metric("Prestamos activos", len(loans))
        c2.metric("Vencidos", overdue_count)
        st.markdown("---")
        if not loans:
            st.info("No hay prestamos activos.")
        for loan in loans:
            _loan_row(storage, loan, user, "active")

    with tab_historial:
        all_loans = storage.get_all_loans()
        returned = [l for l in all_loans if l.get("status") == "returned"]
        if not returned:
            st.info("Aun no hay prestamos devueltos en el historial.")
        for loan in returned:
            with st.container(border=True):
                st.write(
                    f"**{loan['item_name']}** x{loan['quantity']} · {loan['user_name']} ({loan['user_role']})"
                )
                co = loan.get("checkout_at")
                ret = loan.get("return_at")
                st.caption(
                    f"Salida: {co.strftime('%d/%m/%Y %H:%M') if co else 'N/A'} · "
                    f"Reingreso: {ret.strftime('%d/%m/%Y %H:%M') if ret else 'N/A'}"
                )
