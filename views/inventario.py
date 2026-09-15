# -*- coding: utf-8 -*-
"""views/inventario.py - Catalogo, alta/edicion/baja de items y contenedores.
Solo profesor/maestro pueden crear, editar o dar de baja."""

import streamlit as st


def _edit_item_form(storage, item: dict, user: dict):
    st.subheader(f"✏️ Editando: {item.get('name')}")
    with st.form("edit_item_form"):
        name = st.text_input("Nombre", value=item.get("name", ""))
        category = st.text_input("Categoria", value=item.get("category", ""))
        description = st.text_area("Descripcion", value=item.get("description", ""))
        location = st.text_input("Ubicacion", value=item.get("location", ""))

        quantity, min_alert = item.get("quantity", 0), item.get("min_stock_alert", 0)
        if item.get("item_type") != "master":
            quantity = st.number_input("Cantidad total", value=int(item.get("quantity", 0)), min_value=0, step=1)
            min_alert = st.number_input("Umbral de alerta", value=int(item.get("min_stock_alert", 0)), min_value=0, step=1)

        c1, c2, c3 = st.columns(3)
        save = c1.form_submit_button("Guardar cambios", type="primary", use_container_width=True)
        retire = c2.form_submit_button("🗑️ Dar de baja", use_container_width=True)
        cancel = c3.form_submit_button("Cancelar", use_container_width=True)

        if save:
            if not name:
                st.warning("El nombre no puede estar vacio.")
            else:
                data = {
                    **item, "name": name, "category": category, "description": description,
                    "location": location, "quantity": int(quantity), "min_stock_alert": int(min_alert),
                }
                storage.save_item(data, item["id"], is_new=False, actor_email=user["institutional_email"])
                st.success("Item actualizado.")
                st.session_state.editing_item_id = None
                st.rerun()

        if retire:
            storage.retire_item(item["id"], actor_email=user["institutional_email"])
            st.success("Item dado de baja.")
            st.session_state.editing_item_id = None
            st.rerun()

        if cancel:
            st.session_state.editing_item_id = None
            st.rerun()


def render():
    storage = st.session_state.storage
    user = st.session_state.user

    if st.session_state.get("editing_item_id"):
        item = storage.get_item(st.session_state.editing_item_id)
        if not item:
            st.error("El item ya no existe.")
            st.session_state.editing_item_id = None
        else:
            _edit_item_form(storage, item, user)
        return

    tab_catalogo, tab_nuevo = st.tabs(["📋 Catalogo", "➕ Nuevo item / contenedor"])

    with tab_catalogo:
        search = st.text_input("Buscar por nombre, categoria o codigo")
        try:
            items = storage.get_all_items()
        except Exception as e:
            st.error(f"Error al cargar el inventario: {e}")
            items = []

        if search:
            s = search.lower()
            items = [
                i for i in items
                if s in (i.get("name") or "").lower()
                or s in (i.get("category") or "").lower()
                or s in (i.get("id") or "").lower()
            ]

        if not items:
            st.info("No se encontraron items.")
        for item in items:
            with st.container(border=True):
                c1, c2, c3, c4, c5 = st.columns([4, 2, 2, 1, 1])
                tag = {"master": "📦 Contenedor", "child": "🔹 Item (en contenedor)", "standalone": "🔸 Item"}.get(
                    item.get("item_type"), item.get("item_type")
                )
                c1.markdown(f"**{item.get('name')}**")
                c1.caption(f"{tag} · ID: {item.get('id')} · {item.get('category') or 'Sin categoria'}")
                if item.get("item_type") == "master":
                    c2.metric("Items dentro", len(storage.get_children(item["id"])))
                else:
                    c2.metric("Disponibles", storage.get_available_quantity(item["id"]))
                c3.metric("Ubicacion", item.get("location") or "N/A")
                if c4.button("✏️", key=f"edit_{item['id']}", help="Editar"):
                    st.session_state.editing_item_id = item["id"]
                    st.rerun()
                c5.write("")

    with tab_nuevo:
        st.caption("También puedes registrar un item nuevo directamente escaneando su código en la sección Escanear.")
        item_kind = st.radio(
            "¿Que quieres registrar?",
            ("Item individual", "Contenedor maestro nuevo", "Item dentro de un contenedor existente"),
            horizontal=True, key="inv_new_kind",
        )
        with st.form("inv_new_item_form"):
            new_id = st.text_input("Codigo de barras")
            name = st.text_input("Nombre")
            category = st.text_input("Categoria")
            description = st.text_area("Descripcion", height=80)
            location = st.text_input("Ubicacion fisica")

            parent_id = ""
            if item_kind == "Item dentro de un contenedor existente":
                masters = storage.get_all_masters()
                options = {f"{m['name']} ({m['id']})": m["id"] for m in masters}
                if options:
                    choice = st.selectbox("Contenedor maestro", list(options.keys()))
                    parent_id = options.get(choice, "")
                else:
                    st.warning("Todavia no hay contenedores maestros creados.")

            quantity, min_alert = 0, 0
            if item_kind != "Contenedor maestro nuevo":
                quantity = st.number_input("Cantidad inicial", min_value=0, step=1, value=1, key="inv_new_qty")
                min_alert = st.number_input("Umbral de alerta", min_value=0, step=1, value=0, key="inv_new_alert")

            submitted = st.form_submit_button("💾 Registrar", type="primary", use_container_width=True)

            if submitted:
                if not new_id or not name:
                    st.error("Codigo de barras y nombre son obligatorios.")
                elif storage.get_item(new_id):
                    st.error("Ya existe un item con ese codigo.")
                else:
                    item_type = {
                        "Item individual": "standalone", "Contenedor maestro nuevo": "master",
                        "Item dentro de un contenedor existente": "child",
                    }[item_kind]
                    data = {
                        "name": name, "category": category, "description": description,
                        "item_type": item_type, "parent_id": parent_id, "unit": "unidad",
                        "quantity": int(quantity), "location": location,
                        "min_stock_alert": int(min_alert), "status": "active",
                        "created_by": user["institutional_email"],
                    }
                    storage.save_item(data, new_id, is_new=True, actor_email=user["institutional_email"])
                    st.success(f"'{name}' registrado correctamente.")
                    st.rerun()
