# -*- coding: utf-8 -*-
"""
core/loans.py - Logica de negocio de salida (checkout) y reingreso (checkin).

La cantidad total de un item (items.quantity) solo cambia por Alta/Ajuste/Baja.
La disponibilidad se calcula en vivo como quantity - suma(prestamos abiertos),
de forma que siempre queda una auditoria completa de quien tiene que en 'loans'.
"""

import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def checkout(storage, item_id: str, quantity: int, user: dict, expected_return_at=None, notes: str = ""):
    if quantity <= 0:
        return False, "La cantidad debe ser mayor a 0.", None

    item = storage.get_item(item_id)
    if not item:
        return False, f"El item '{item_id}' no existe.", None
    if item.get("item_type") == "master":
        return False, "No se puede dar salida a un contenedor maestro, solo a sus items.", None

    available = storage.get_available_quantity(item_id)
    if quantity > available:
        return False, f"Stock insuficiente. Disponible: {available}.", None

    loan = storage.create_loan(item, quantity, user, expected_return_at=expected_return_at, notes=notes)
    return True, f"Salida registrada: '{item.get('name')}' x{quantity} para {user.get('full_name')}.", loan


def checkin(storage, loan_id: str, actor_user: dict):
    ok, msg = storage.return_loan(loan_id, actor_email=actor_user.get("institutional_email", ""))
    return ok, msg


def is_overdue(loan: dict) -> bool:
    if loan.get("status") != "out":
        return False
    expected = loan.get("expected_return_at")
    if not expected:
        return False
    return expected < datetime.now(timezone.utc)


def get_overdue_loans(storage) -> list:
    open_loans = storage.get_all_loans(status="out")
    return [l for l in open_loans if is_overdue(l)]


def get_loans_for_view(storage, user: dict) -> list:
    """Estudiante ve solo lo suyo; profesor/maestro ven todos los prestamos abiertos."""
    if user.get("role") == "estudiante":
        return storage.get_open_loans_for_user(user["id"])
    return storage.get_all_loans(status="out")
