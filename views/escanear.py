# -*- coding: utf-8 -*-
"""views/escanear.py - Flujo central: escanear codigo maestro/hijo/individual,
dar salida (checkout) y registrar reingreso (checkin)."""

from datetime import datetime, timedelta, timezone

import streamlit as st

from core import barcode, loans as loans_core, notifications


def _render_item_actions(item: dict, parent: dict = None):
    storage = st.session_state.storage
    user = st.session_state.user

    if parent:
        st.caption(f"📦 Pertenece al contenedor: **{parent.get('name')}** (`{parent.get('id')}`)")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Disponibles", item["available"])
    c2.metric("Total propiedad del lab", item.get("quantity", 0))
    c3.metric("Ubicacion", item.get("location") or "N/A")
    c4.metric("Categoria", item.get("category") or "N/A")

    if item.get("description"):
        st.caption(item["description"])

    st.markdown("##### 📤 Dar salida (checkout)")
    if item["available"] <= 0:
        st.warning("No hay unidades disponibles para dar salida en este momento.")
    else:
        with st.form(f"checkout_form_{item['id']}"):
            qty = st.number_input("Cantidad", min_value=1, max_value=int(item["available"]), value=1, step=1)
            with_date = st.checkbox("Definir fecha esperada de devolucion")
            expected_date = None
            if with_date:
                expected_date = st.date_input("Devolver antes de", value=datetime.now().date() + timedelta(days=7))
            notes = st.text_input("Notas (opcional)", placeholder="Motivo de uso, practica, proyecto...")
            submitted = st.form_submit_button("✅ Confirmar salida", type="primary", use_container_width=True)

            if submitted:
                expected_dt = None
                if with_date:
                    expected_dt = datetime.combine(expected_date, datetime.min.time()).replace(tzinfo=timezone.utc)
                ok, msg, loan = loans_core.checkout(storage, item["id"], int(qty), user, expected_dt, notes)
                if ok:
                    st.success(msg)
                    notifications.send_whatsapp_alert(f"📤 Salida: {msg}")
                    st.session_state.scan_result = barcode.scan(storage, item["id"])
                    st.rerun()
                else:
                    st.error(msg)

    st.markdown("##### 📥 Reingresar (checkin)")
    open_loans = storage.get_open_loans_for_item(item["id"])
    if user["role"] == "estudiante":
        open_loans = [l for l in open_loans if l["user_id"] == user["id"]]

    if not open_loans:
        st.info("No hay prestamos abiertos de este item para reingresar.")
    else:
        for loan in open_loans:
            overdue_tag = " ⚠️ VENCIDO" if loans_core.is_overdue(loan) else ""
            with st.container(border=True):
                cc1, cc2 = st.columns([3, 1])
                cc1.write(f"**{loan['user_name']}** ({loan['user_role']}) · {loan['quantity']} u.{overdue_tag}")
                if cc2.button("Reingresar", key=f"checkin_{loan['id']}", use_container_width=True):
                    ok, msg = loans_core.checkin(storage, loan["id"], user)
                    if ok:
                        st.success(msg)
                        st.session_state.scan_result = barcode.scan(storage, item["id"])
                        st.rerun()
                    else:
                        st.error(msg)


def _render_new_item_wizard(scanned_code: str):
    storage = st.session_state.storage
    user = st.session_state.user

    st.warning(f"El codigo `{scanned_code}` no existe todavia en el inventario.")

    if user["role"] == "estudiante":
        st.info("Pide a un profesor o al administrador del laboratorio que registre este item.")
        return

    item_kind = st.radio(
        "¿Que quieres registrar?",
        ("Item individual", "Contenedor maestro nuevo", "Item dentro de un contenedor existente"),
        horizontal=True,
    )

    with st.form("new_item_form"):
        name = st.text_input("Nombre")
        category = st.text_input("Categoria", placeholder="Electronica, Mecanica, EPP, Herramientas...")
        description = st.text_area("Descripcion", height=80)
        location = st.text_input("Ubicacion fisica", placeholder="Estante 3, Gabinete B...")

        parent_id = ""
        if item_kind == "Item dentro de un contenedor existente":
            masters = storage.get_all_masters()
            options = {f"{m['name']} ({m['id']})": m["id"] for m in masters}
            if not options:
                st.warning("Todavia no hay contenedores maestros creados.")
            else:
                choice = st.selectbox("Contenedor maestro", list(options.keys()))
                parent_id = options.get(choice, "")

        quantity, min_alert = 0, 0
        if item_kind != "Contenedor maestro nuevo":
            quantity = st.number_input("Cantidad inicial", min_value=0, step=1, value=1)
            min_alert = st.number_input("Umbral de alerta de disponibilidad", min_value=0, step=1, value=0)

        submitted = st.form_submit_button("💾 Registrar item", type="primary", use_container_width=True)

        if submitted:
            if not name:
                st.error("El nombre es obligatorio.")
            elif item_kind == "Item dentro de un contenedor existente" and not parent_id:
                st.error("Debes seleccionar un contenedor maestro.")
            else:
                item_type = {
                    "Item individual": "standalone",
                    "Contenedor maestro nuevo": "master",
                    "Item dentro de un contenedor existente": "child",
                }[item_kind]
                data = {
                    "name": name, "category": category, "description": description,
                    "item_type": item_type, "parent_id": parent_id, "unit": "unidad",
                    "quantity": int(quantity), "location": location,
                    "min_stock_alert": int(min_alert), "status": "active",
                    "created_by": user["institutional_email"],
                }
                try:
                    storage.save_item(data, scanned_code, is_new=True, actor_email=user["institutional_email"])
                    st.success(f"¡'{name}' registrado correctamente!")
                    st.session_state.scan_result = barcode.scan(storage, scanned_code)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al registrar: {e}")


def render():
    storage = st.session_state.storage

    st.info("Conecta tu lector de codigo de barras USB. Haz clic en el campo y escanea, o escribe el codigo manualmente.")

    with st.form("scan_form", clear_on_submit=True):
        code = st.text_input("Codigo de barras", placeholder="Escanea aqui...")
        submitted = st.form_submit_button("Buscar", use_container_width=True)
        if submitted and code:
            st.session_state.scan_result = barcode.scan(storage, code)
        elif submitted and not code:
            st.warning("Ingresa o escanea un codigo.")

    result = st.session_state.get("scan_result")
    st.markdown("---")

    if not result:
        st.caption("Esperando escaneo...")
        return

    if result["status"] == "error":
        st.error(result["message"])
    elif result["status"] == "not_found":
        _render_new_item_wizard(result["barcode"])
    elif result["status"] == "found_master":
        item = result["item"]
        st.success(f"📦 Contenedor: **{item['name']}** (`{item['id']}`)")
        if item.get("description"):
            st.caption(item["description"])
        st.caption(f"Ubicacion: {item.get('location') or 'N/A'}")
        children = result["children"]
        if not children:
            st.info("Este contenedor todavia no tiene items registrados dentro.")
        else:
            for child in children:
                with st.expander(f"{child['name']} — {child['available']} disponibles"):
                    _render_item_actions(child, parent=item)
    elif result["status"] == "found_item":
        item = result["item"]
        st.success(f"✔️ Item encontrado: **{item['name']}** (`{item['id']}`)")
        _render_item_actions(item, parent=result.get("parent"))
