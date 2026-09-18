# -*- coding: utf-8 -*-
"""
core/labels.py - Nomenclatura unica para los tipos de item, usada por todas
las vistas para que el lenguaje sea consistente en toda la aplicacion.

Los valores internos ("master", "child", "standalone") se mantienen tal cual
en core/storage.py y en los CSV de importacion (son claves tecnicas, no
texto para el usuario). Este modulo es la UNICA fuente de los nombres que
ve el usuario, para poder evolucionarlos sin tocar la logica de negocio.

- Contenedor Principal ("master"): la caja, kit o gabinete fisico que agrupa
  productos relacionados.
- Contenedor de Caracteristica ("child"): una subdivision con nombre propio
  DENTRO de un Contenedor Principal, que agrupa unidades que comparten una
  caracteristica (ej. "Resistencias 220 ohm", "Tornillos M4 x 20mm").
- Item Individual ("standalone"): un producto con codigo propio que no
  pertenece a ningun Contenedor Principal.
"""

ITEM_TYPE_ICONS = {
    "master": "🗄️",
    "child": "🧩",
    "standalone": "🔹",
}

ITEM_TYPE_NAMES = {
    "master": "Contenedor Principal",
    "child": "Contenedor de Característica",
    "standalone": "Ítem Individual",
}

ITEM_TYPE_LABELS = {k: f"{ITEM_TYPE_ICONS[k]} {v}" for k, v in ITEM_TYPE_NAMES.items()}

# Opciones en el orden en que se muestran en los formularios de creacion.
ITEM_TYPE_CHOICES = [
    ITEM_TYPE_NAMES["standalone"],
    ITEM_TYPE_NAMES["master"],
    ITEM_TYPE_NAMES["child"],
]

ITEM_TYPE_BY_CHOICE = {
    ITEM_TYPE_NAMES["standalone"]: "standalone",
    ITEM_TYPE_NAMES["master"]: "master",
    ITEM_TYPE_NAMES["child"]: "child",
}

ITEM_TYPE_HELP = {
    "standalone": "Un producto con su propio codigo, sin contenedor (ej. un multimetro).",
    "master": "La caja, kit o gabinete fisico que va a agrupar productos (ej. 'Caja de Electronica').",
    "child": "Una subdivision DENTRO de un Contenedor Principal ya creado, para una caracteristica "
             "especifica (ej. 'Resistencias 220 ohm', 'Tornillos M4').",
}


def type_label(item_type: str) -> str:
    return ITEM_TYPE_LABELS.get(item_type, item_type)


def type_name(item_type: str) -> str:
    return ITEM_TYPE_NAMES.get(item_type, item_type)


# ---------------------------------------------------------------------------
# Generacion visual de etiquetas imprimibles (codigo de barras + texto)
# ---------------------------------------------------------------------------
# Genera una etiqueta Code128 (legible por cualquier lector USB ya usado en
# la app) centrada sobre un lienzo Pillow de tamano fijo, con el codigo en
# texto plano debajo. Pensada para imprimirse tal cual en una termica
# SAT TT 460 (u otra compatible) a 203 dpi.

import io

import barcode as code128_lib
from barcode.writer import ImageWriter
from PIL import Image, ImageDraw, ImageFont

from core.barcode import validate_code_format

LABEL_DPI = 203  # resolucion nativa de la SAT TT 460
LABEL_WIDTH_MM = 50
LABEL_HEIGHT_MM = 25
# Aproximacion en pixeles de 50x25mm a 203dpi (399x200 exacto), redondeada a
# multiplos de 32px como espera el firmware de impresoras termicas tipo SAT.
LABEL_CANVAS_SIZE = (384, 192)

_QUIET_ZONE_MM = 1.5
_MODULE_HEIGHT_MM = 9.0
_MARGIN_PX = 10
_TEXT_AREA_PX = 34
_MIN_MODULE_WIDTH_MM = 0.22
_MAX_MODULE_WIDTH_MM = 0.55

_FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]


def _load_font(size: int):
    for path in _FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def _raw_barcode_image(code: str, module_width_mm: float):
    writer = ImageWriter()
    options = {
        "module_width": module_width_mm,
        "module_height": _MODULE_HEIGHT_MM,
        "quiet_zone": _QUIET_ZONE_MM,
        "write_text": False,
        "dpi": LABEL_DPI,
    }
    obj = code128_lib.get("code128", code, writer=writer)
    buf = io.BytesIO()
    obj.write(buf, options=options)
    buf.seek(0)
    return Image.open(buf).convert("L")


def _fit_module_width(code: str, target_width_px: int) -> float:
    """El ancho renderizado de un Code128 es una funcion afin del
    module_width (para un `code` fijo), asi que 2 muestras bastan para
    despejar por interpolacion lineal el module_width exacto que llena
    `target_width_px` sin tener que reescalar la imagen despues (reescalar
    un codigo de barras puede romper su legibilidad)."""
    lo, hi = _MIN_MODULE_WIDTH_MM, _MAX_MODULE_WIDTH_MM
    w_lo = _raw_barcode_image(code, lo).width
    w_hi = _raw_barcode_image(code, hi).width
    if w_hi == w_lo:
        return lo
    slope = (w_hi - w_lo) / (hi - lo)
    intercept = w_lo - slope * lo
    mw = (target_width_px - intercept) / slope
    return max(lo, min(hi, mw))


def generate_label_image(code: str, canvas_size: tuple = LABEL_CANVAS_SIZE) -> Image.Image:
    """Genera la etiqueta imprimible completa: codigo de barras Code128
    centrado horizontalmente + el codigo en texto legible por humanos
    (5 niveles numerico o alfanumerico) centrado abajo, sobre un lienzo en
    blanco y negro de `canvas_size` px (por defecto 50x25mm @ 203dpi).

    Lanza ValueError si `code` no cumple ninguno de los 3 formatos validos
    (ver core/barcode.validate_code_format)."""
    validate_code_format(code)

    width, height = canvas_size
    target_bar_w = max(1, width - 2 * _MARGIN_PX)

    module_width = _fit_module_width(code, target_bar_w)
    bar_img = _raw_barcode_image(code, module_width)
    for _ in range(3):
        if bar_img.width <= target_bar_w:
            break
        module_width *= 0.97
        bar_img = _raw_barcode_image(code, module_width)

    canvas = Image.new("L", (width, height), color=255)
    draw = ImageDraw.Draw(canvas)

    bar_area_h = max(1, height - _TEXT_AREA_PX - _MARGIN_PX)
    if bar_img.height > bar_area_h:
        ratio = bar_area_h / bar_img.height
        bar_img = bar_img.resize((max(1, int(bar_img.width * ratio)), bar_area_h), Image.LANCZOS)

    bar_x = (width - bar_img.width) // 2
    bar_y = _MARGIN_PX // 2 + (bar_area_h - bar_img.height) // 2
    canvas.paste(bar_img, (bar_x, bar_y))

    font_size = 26
    font = _load_font(font_size)
    while font_size > 8:
        bbox = draw.textbbox((0, 0), code, font=font)
        if bbox[2] - bbox[0] <= width - 2 * _MARGIN_PX:
            break
        font_size -= 1
        font = _load_font(font_size)

    bbox = draw.textbbox((0, 0), code, font=font)
    text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    text_x = (width - text_w) // 2 - bbox[0]
    text_y = height - _TEXT_AREA_PX + (_TEXT_AREA_PX - text_h) // 2 - bbox[1]
    draw.text((text_x, text_y), code, font=font, fill=0)

    return canvas.convert("1", dither=Image.Dither.NONE)


def generate_label_png_bytes(code: str, canvas_size: tuple = LABEL_CANVAS_SIZE) -> bytes:
    """Como generate_label_image pero devuelve bytes PNG listos para
    st.download_button o para enviar directo a la impresora."""
    img = generate_label_image(code, canvas_size=canvas_size)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
