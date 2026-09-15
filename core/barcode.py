# -*- coding: utf-8 -*-
"""
core/barcode.py - Resolucion de codigos de barras (ver core/labels.py para
los nombres que ve el usuario).

Convencion de codigos de barras del laboratorio:
- "master" (Contenedor Principal): codigo pegado a una caja, gabinete o kit.
  No tiene cantidad propia; agrupa Contenedores de Caracteristica.
- "child" (Contenedor de Caracteristica): codigo de una subdivision DENTRO
  de un Contenedor Principal (parent_id apunta al id del maestro).
- "standalone" (Item Individual): codigo de un producto que no pertenece
  a ningun Contenedor Principal.
"""

import logging

logger = logging.getLogger(__name__)


def scan(storage, code: str) -> dict:
    code = (code or "").strip()
    if not code:
        return {"status": "error", "message": "El codigo de barras no puede estar vacio."}

    try:
        item = storage.get_item(code)
        if not item:
            return {"status": "not_found", "barcode": code}

        if item.get("status") == "retired":
            return {"status": "error", "message": f"El item '{item.get('name')}' fue dado de baja."}

        if item.get("item_type") == "master":
            children = storage.get_children(code)
            for child in children:
                child["available"] = storage.get_available_quantity(child["id"])
            return {"status": "found_master", "item": item, "children": children}

        item["available"] = storage.get_available_quantity(code)
        parent = None
        if item.get("parent_id"):
            parent = storage.get_item(item["parent_id"])
        return {"status": "found_item", "item": item, "parent": parent}

    except Exception as e:
        logger.error(f"Error al escanear el codigo '{code}': {e}")
        return {"status": "error", "message": str(e)}
