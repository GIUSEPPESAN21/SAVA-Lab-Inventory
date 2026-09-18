# -*- coding: utf-8 -*-
"""Pruebas de core/storage._validate_item_data: los items NUEVOS deben
cumplir uno de los 3 formatos de codigo de core/barcode.py; los items ya
existentes (edicion) no se revalidan, para no romper catalogos cargados
con la nomenclatura anterior."""

import pandas as pd
import pytest

from core.storage import SHEET_COLUMNS, _validate_item_data

EMPTY_ITEMS = pd.DataFrame(columns=SHEET_COLUMNS["items"])


def test_new_item_with_valid_standard_code_is_accepted():
    _validate_item_data(
        {"item_type": "standalone", "parent_id": ""}, EMPTY_ITEMS, "1-2-05-12-001", is_new=True
    )


def test_new_item_with_valid_mesa_code_is_accepted():
    _validate_item_data(
        {"item_type": "standalone", "parent_id": ""}, EMPTY_ITEMS, "M1-E2", is_new=True
    )


def test_new_item_with_invalid_code_is_rejected():
    with pytest.raises(ValueError):
        _validate_item_data(
            {"item_type": "standalone", "parent_id": ""}, EMPTY_ITEMS, "CAJA-001", is_new=True
        )


def test_editing_existing_item_does_not_revalidate_legacy_code():
    """Un item cargado antes de este cambio (id con la nomenclatura vieja)
    debe poder seguir editandose sin que su id sea rechazado."""
    _validate_item_data(
        {"item_type": "standalone", "parent_id": ""}, EMPTY_ITEMS, "CAJA-001", is_new=False
    )
