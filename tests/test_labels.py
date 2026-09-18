# -*- coding: utf-8 -*-
"""Pruebas de core/labels.py: generacion de la imagen de etiqueta (codigo de
barras Code128 + texto legible) para impresion en una termica SAT TT 460."""

import pytest
from PIL import Image

from core import labels


@pytest.mark.parametrize("code", ["1-2-05-12-001", "M1-E2", "E3-LM07", "3-6-999-999-9999"])
def test_generate_label_image_has_fixed_canvas_size(code):
    img = labels.generate_label_image(code)
    assert img.size == labels.LABEL_CANVAS_SIZE
    assert img.mode == "1"  # blanco y negro puro, ideal para termica


def test_generate_label_image_custom_canvas_size():
    img = labels.generate_label_image("M1-E2", canvas_size=(300, 150))
    assert img.size == (300, 150)


def test_generate_label_image_rejects_invalid_code():
    with pytest.raises(ValueError):
        labels.generate_label_image("CAJA-001")


def test_generate_label_png_bytes_returns_valid_png():
    data = labels.generate_label_png_bytes("1-2-05-12-001")
    assert data[:8] == b"\x89PNG\r\n\x1a\n"

    import io
    img = Image.open(io.BytesIO(data))
    assert img.size == labels.LABEL_CANVAS_SIZE


def test_label_canvas_matches_sat_tt460_spec():
    # 50x25mm @ 203dpi (aprox, redondeado a multiplos de 32px)
    assert labels.LABEL_DPI == 203
    assert labels.LABEL_WIDTH_MM == 50
    assert labels.LABEL_HEIGHT_MM == 25
    assert labels.LABEL_CANVAS_SIZE == (384, 192)
