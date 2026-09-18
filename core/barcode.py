# -*- coding: utf-8 -*-
"""
core/barcode.py - Validacion, interpretacion y resolucion de codigos de
inventario (ver core/labels.py para la generacion visual de etiquetas y los
nombres de tipo de item que ve el usuario).

Nomenclatura de codigos del laboratorio (Canvas de Estructura y Codificacion
GLIOPS V3), soporta exactamente 3 formatos, cada uno resuelto por regex:

1. Estandar de 5 niveles, 100% numerico:
   [ESTANTERIA]-[PISO]-[CONTENEDOR]-[CAJA]-[ITEM]
   Solo digitos separados por guion. Estanteria: 1 a 3. Piso: 1 a 6.
   Contenedor/Caja/Item: enteros positivos, con o sin ceros a la izquierda.
   Ejemplo: 1-2-05-12-001

2. Mesas de trabajo (equipos de alto valor), alfanumerico:
   M[1|2]-E[n]
   Ejemplo: M1-E2

3. Exhibicion Lego, alfanumerico:
   E3-LM[n]
   Ejemplo: E3-LM07

Los 3 formatos son mutuamente excluyentes por construccion (empiezan con
digito, con "M" o con "E3-LM" respectivamente), asi que un codigo nunca
coincide con mas de uno.
"""

import logging
import re

logger = logging.getLogger(__name__)

FORMAT_STANDARD = "estandar_numerico"
FORMAT_MESA = "mesa_trabajo"
FORMAT_LEGO = "exhibicion_lego"

ESTANTERIA_MIN, ESTANTERIA_MAX = 1, 3
PISO_MIN, PISO_MAX = 1, 6

_STANDARD_RE = re.compile(r"^(\d+)-(\d+)-(\d+)-(\d+)-(\d+)$")
_MESA_RE = re.compile(r"^M([12])-E(\d+)$")
_LEGO_RE = re.compile(r"^E3-LM(\d+)$")

FORMAT_HELP = (
    "Formatos aceptados: "
    "[ESTANTERIA]-[PISO]-[CONTENEDOR]-[CAJA]-[ITEM] 100% numerico "
    "(ej. 1-2-05-12-001) · "
    "M1-E[n] o M2-E[n] para mesas de trabajo (ej. M1-E2) · "
    "E3-LM[n] para exhibicion Lego (ej. E3-LM07)."
)


def parse_code(code: str) -> dict:
    """Identifica a cual de los 3 formatos pertenece `code` y lo descompone
    en sus componentes. Lanza ValueError con un mensaje explicativo (incluye
    los 3 formatos validos) si no coincide con ninguno o si algun componente
    esta fuera de rango."""
    code = (code or "").strip()

    m = _STANDARD_RE.match(code)
    if m:
        estanteria, piso, contenedor, caja, item = (int(g) for g in m.groups())
        if not (ESTANTERIA_MIN <= estanteria <= ESTANTERIA_MAX):
            raise ValueError(
                f"Estanteria invalida en '{code}': debe estar entre "
                f"{ESTANTERIA_MIN} y {ESTANTERIA_MAX}."
            )
        if not (PISO_MIN <= piso <= PISO_MAX):
            raise ValueError(
                f"Piso invalido en '{code}': debe estar entre {PISO_MIN} y {PISO_MAX}."
            )
        if contenedor < 1 or caja < 1 or item < 1:
            raise ValueError(f"Contenedor, caja e item deben ser numeros positivos en '{code}'.")
        return {
            "format": FORMAT_STANDARD,
            "estanteria": estanteria,
            "piso": piso,
            "contenedor": contenedor,
            "caja": caja,
            "item": item,
        }

    m = _MESA_RE.match(code)
    if m:
        mesa, equipo = int(m.group(1)), int(m.group(2))
        if equipo < 1:
            raise ValueError(f"Numero de equipo invalido en '{code}'.")
        return {"format": FORMAT_MESA, "mesa": mesa, "equipo": equipo}

    m = _LEGO_RE.match(code)
    if m:
        modelo = int(m.group(1))
        if modelo < 1:
            raise ValueError(f"Numero de modelo invalido en '{code}'.")
        return {"format": FORMAT_LEGO, "estanteria": 3, "modelo": modelo}

    raise ValueError(f"'{code}' no coincide con ningun formato de codigo valido. {FORMAT_HELP}")


def detect_format(code: str):
    """Version silenciosa de parse_code: devuelve el nombre del formato o
    None si `code` no es valido, sin lanzar excepcion."""
    try:
        return parse_code(code)["format"]
    except ValueError:
        return None


def is_valid_code(code: str) -> bool:
    return detect_format(code) is not None


def validate_code_format(code: str) -> str:
    """Valida `code` contra los 3 formatos y devuelve el nombre del formato
    detectado. Lanza ValueError (con los 3 formatos validos en el mensaje)
    si no coincide con ninguno. Usado por core/storage.py al dar de alta
    items nuevos y por core/labels.py antes de generar una etiqueta."""
    return parse_code(code)["format"]


def describe_parsed(parsed: dict) -> str:
    """Texto legible en español de los componentes ya interpretados de un
    codigo (ver parse_code), para mostrar en la UI de escaneo."""
    if not parsed:
        return ""
    fmt = parsed.get("format")
    if fmt == FORMAT_STANDARD:
        return (
            f"Estantería {parsed['estanteria']} · Piso {parsed['piso']} · "
            f"Contenedor {parsed['contenedor']:02d} · Caja {parsed['caja']:02d} · "
            f"Ítem {parsed['item']:03d}"
        )
    if fmt == FORMAT_MESA:
        return f"Mesa de trabajo {parsed['mesa']} · Equipo {parsed['equipo']}"
    if fmt == FORMAT_LEGO:
        return f"Estantería 3 (Exhibición Lego) · Modelo {parsed['modelo']}"
    return ""


def scan(storage, code: str) -> dict:
    code = (code or "").strip()
    if not code:
        return {"status": "error", "message": "El codigo de barras no puede estar vacio."}

    parsed = None
    try:
        parsed = parse_code(code)
    except ValueError:
        parsed = None  # codigo con nomenclatura anterior/libre: se sigue permitiendo buscar por id

    try:
        item = storage.get_item(code)
        if not item:
            return {"status": "not_found", "barcode": code, "parsed": parsed}

        if item.get("status") == "retired":
            return {"status": "error", "message": f"El item '{item.get('name')}' fue dado de baja."}

        if item.get("item_type") == "master":
            children = storage.get_children(code)
            for child in children:
                child["available"] = storage.get_available_quantity(child["id"])
            return {"status": "found_master", "item": item, "children": children, "parsed": parsed}

        item["available"] = storage.get_available_quantity(code)
        parent = None
        if item.get("parent_id"):
            parent = storage.get_item(item["parent_id"])
        return {"status": "found_item", "item": item, "parent": parent, "parsed": parsed}

    except Exception as e:
        logger.error(f"Error al escanear el codigo '{code}': {e}")
        return {"status": "error", "message": str(e)}
