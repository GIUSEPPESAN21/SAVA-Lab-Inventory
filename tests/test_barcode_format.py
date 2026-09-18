# -*- coding: utf-8 -*-
"""Pruebas de la nomenclatura de codigos GLIOPS V3 (core/barcode.py):
los 3 formatos validos (estandar numerico, mesas de trabajo, exhibicion
Lego), sus reglas de rango y el rechazo de cualquier otro string."""

import pytest

from core import barcode


@pytest.mark.parametrize(
    "code, expected",
    [
        ("1-2-05-12-001", {"format": "estandar_numerico", "estanteria": 1, "piso": 2, "contenedor": 5, "caja": 12, "item": 1}),
        ("3-6-1-1-1", {"format": "estandar_numerico", "estanteria": 3, "piso": 6, "contenedor": 1, "caja": 1, "item": 1}),
        ("M1-E2", {"format": "mesa_trabajo", "mesa": 1, "equipo": 2}),
        ("M2-E1", {"format": "mesa_trabajo", "mesa": 2, "equipo": 1}),
        ("E3-LM07", {"format": "exhibicion_lego", "estanteria": 3, "modelo": 7}),
        ("E3-LM1", {"format": "exhibicion_lego", "estanteria": 3, "modelo": 1}),
    ],
)
def test_parse_code_valid_formats(code, expected):
    assert barcode.parse_code(code) == expected


@pytest.mark.parametrize(
    "code",
    [
        "4-2-05-12-001",   # estanteria fuera de rango (1 a 3)
        "0-2-05-12-001",   # estanteria fuera de rango
        "1-7-05-12-001",   # piso fuera de rango (1 a 6)
        "1-0-05-12-001",   # piso fuera de rango
        "1-2-00-12-001",   # contenedor debe ser >= 1
        "1-2-05-00-001",   # caja debe ser >= 1
        "1-2-05-12-000",   # item debe ser >= 1
    ],
)
def test_parse_code_standard_out_of_range(code):
    with pytest.raises(ValueError):
        barcode.parse_code(code)


@pytest.mark.parametrize(
    "code",
    [
        "M3-E1",       # solo se permite mesa 1 o 2
        "M0-E1",
        "m1-e2",       # case-sensitive: la nomenclatura oficial es en mayusculas
        "E3-LM0",      # modelo debe ser >= 1
        "E3LM07",      # falta el guion
        "E4-LM01",     # la exhibicion Lego vive solo en la estanteria 3
        "CAJA-001",    # nomenclatura anterior, ya no valida para items nuevos
        "1-2-3",       # formato estandar incompleto (solo 3 niveles)
        "",
        "   ",
    ],
)
def test_parse_code_rejects_invalid(code):
    with pytest.raises(ValueError):
        barcode.parse_code(code)


def test_detect_format_and_is_valid_code():
    assert barcode.detect_format("1-2-05-12-001") == barcode.FORMAT_STANDARD
    assert barcode.detect_format("M1-E2") == barcode.FORMAT_MESA
    assert barcode.detect_format("E3-LM07") == barcode.FORMAT_LEGO
    assert barcode.detect_format("no-valido") is None

    assert barcode.is_valid_code("M1-E2") is True
    assert barcode.is_valid_code("no-valido") is False


def test_validate_code_format_returns_format_name():
    assert barcode.validate_code_format("E3-LM07") == barcode.FORMAT_LEGO
    with pytest.raises(ValueError):
        barcode.validate_code_format("no-valido")


def test_describe_parsed_for_each_format():
    std = barcode.parse_code("1-2-05-12-001")
    assert "Estantería 1" in barcode.describe_parsed(std)
    assert "Ítem 001" in barcode.describe_parsed(std)

    mesa = barcode.parse_code("M1-E2")
    assert "Mesa de trabajo 1" in barcode.describe_parsed(mesa)

    lego = barcode.parse_code("E3-LM07")
    assert "Modelo 7" in barcode.describe_parsed(lego)


def test_scan_exposes_parsed_components_for_valid_format(storage):
    storage.add_item("M1-E1", name="Impresora 3D", item_type="standalone", quantity=1)
    result = barcode.scan(storage, "M1-E1")
    assert result["status"] == "found_item"
    assert result["parsed"] == {"format": "mesa_trabajo", "mesa": 1, "equipo": 1}


def test_scan_still_works_for_legacy_ids_without_parsed_info(storage):
    """Los items ya cargados con la nomenclatura anterior deben seguir
    pudiendo escanearse; solo 'parsed' queda en None."""
    storage.add_item("CAJA-001", name="Caja vieja", item_type="master")
    result = barcode.scan(storage, "CAJA-001")
    assert result["status"] == "found_master"
    assert result["parsed"] is None
