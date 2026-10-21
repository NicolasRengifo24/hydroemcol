from __future__ import annotations

import re


def normalizar_correo(correo: str) -> str:
    if not correo:
        return ""
    return correo.strip().lower()


_TELEFONO_CLEAN = re.compile(r"[^\d+]")


def normalizar_telefono(telefono: str) -> str:
    if not telefono:
        return ""
    t = telefono.strip()
    # Elimina espacios, guiones, paréntesis y otros símbolos; conserva +
    t = _TELEFONO_CLEAN.sub("", t)
    # Trata +57 o 57 opcionales (colombia)
    if t.startswith("+57"):
        t = t[3:]
    elif t.startswith("57") and len(t) > 2:
        t = t[2:]
    return t


_CELULAR_SEPARADORES = re.compile(r"[\s\-()]")


def validar_celular_colombiano(valor: str) -> str | None:
    """Valida un celular colombiano de WhatsApp (RF-WA-02, spec 012).

    Quita espacios, guiones y paréntesis; después quita el prefijo `+57` o
    `57` (solo cuando quedan 12 dígitos). Devuelve los 10 dígitos limpios
    si empiezan por 3; `None` en cualquier otro caso.
    """
    if not valor:
        return None
    t = _CELULAR_SEPARADORES.sub("", valor)
    # Prefijo país: +57 siempre; 57 solo si tras quitarlo quedan 10 dígitos
    if t.startswith("+57"):
        t = t[3:]
    elif t.startswith("57") and len(t) == 12:
        t = t[2:]
    if len(t) != 10 or not t.isdigit() or not t.startswith("3"):
        return None
    return t
