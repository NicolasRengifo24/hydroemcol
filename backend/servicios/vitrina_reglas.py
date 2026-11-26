"""Clave opaca de la vitrina (spec 013).

Única función pura que queda en este módulo: deriva la clave pública de un
producto a partir de su identificador interno y del secreto, sin leer base de
datos, reloj ni configuración. La API pública nunca expone el identificador.
"""

import hashlib


def clave_publica_producto(pk, secreto):
    """Clave pública opaca y estable de un producto (plan §4.1).

    Primeros 16 hex de ``SHA-256("vitrina:" + secreto + ":" + pk)``. No es
    reversible y no coincide con el pk, de modo que la API pública nunca
    expone identificadores internos (RF-VIT-03/05).
    """
    material = f'vitrina:{secreto}:{pk}'.encode('utf-8')
    return hashlib.sha256(material).hexdigest()[:16]
