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
