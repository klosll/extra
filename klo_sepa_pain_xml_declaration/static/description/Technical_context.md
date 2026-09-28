# Technical Context — `klo_sepa_pain_xml_declaration`

## Módulo
| Campo | Valor |
|---|---|
| **Nombre técnico** | `klo_sepa_pain_xml_declaration` |
| **Nombre legible** | `KLO - SEPA pain standalone XML declaration` |
| **Versión** | 18.0.1.0.0 |
| **Autor** | KLO Ingeniería Informática S.L.L. |
| **Licencia** | AGPL-3 |
| **Categoría** | Banking addons |
| **Ubicación** | `/opt/odoo18_desarrollo/extra-addons/klo/extra/klo_sepa_pain_xml_declaration/` |
| **Fecha creación** | 2026-09-28 |
| **Odoo versión** | 18.0 |

---

## Descripción

Los ficheros SEPA pain generados por OCA salen con cabecera `<?xml version='1.0' encoding='UTF-8'?>` sin `standalone`, porque `finalize_sepa_file_creation()` en `account_banking_pain_base` serializa con `etree.tostring(..., xml_declaration=True)` sin pasar `standalone`. El banco exige la cabecera `<?xml version="1.0" encoding="UTF-8" standalone="no"?>` y rechaza las remesas sin ella.

Este módulo extiende `account.payment.order` y normaliza solo la declaración XML (primera línea) del fichero ya generado y validado por OCA, sin tocar el contenido del documento ni modificar nada bajo `extra-addons/oca/` (solo lectura, se pierde al actualizar).

---

## Constante añadida: `_SEPA_XML_DECLARATION`

No se añade ningún campo a la base de datos. Solo una constante de clase:

| Atributo | Valor |
|---|---|
| **Modelo** | `account.payment.order` (`_inherit`) |
| **Nombre técnico** | `_SEPA_XML_DECLARATION` |
| **Tipo** | `bytes` (constante de clase, no es `fields.*`) |
| **Valor** | `b'<?xml version="1.0" encoding="UTF-8" standalone="no"?>'` |
| **Propósito** | Cabecera exigida por el banco; sustituye la declaración generada por lxml |

---

## Dependencias

| Módulo | Propósito |
|---|---|
| `account_banking_pain_base` (OCA `bank-payment`) | Provee `finalize_sepa_file_creation(xml_root, gen_args)` que este módulo extiende vía `super()` |

El módulo OCA está en:
`/opt/odoo18_desarrollo/extra-addons/oca/bank-payment/account_banking_pain_base/`

Método origen: `finalize_sepa_file_creation()` en `extra-addons/oca/bank-payment/account_banking_pain_base/models/account_payment_order.py`.

---

## Lógica

El método `finalize_sepa_file_creation(xml_root, gen_args)` de OCA genera el `xml_string` (bytes) y el `filename`, y ya ha realizado la validación XSD antes de devolverlos.

Nuestro override añade tras el `super()`:

```python
xml_string = re.sub(
    br"^<\?xml[^?\n]*\?>",
    self._SEPA_XML_DECLARATION,
    xml_string,
    count=1,
)
```

Comportamiento:

| Situación | Resultado |
|---|---|
| Fichero OCA con `<?xml version='1.0' encoding='UTF-8'?>` | Primera línea sustituida por `<?xml version="1.0" encoding="UTF-8" standalone="no"?>`; resto intacto |
| Fichero con otra declaración (p. ej. comillas dobles, otro orden) | Igualmente normalizada, el regex `^<\?xml[^?\n]*\?>` cubre cualquier variante de una línea |
| Fichero sin declaración XML | Sin cambios (el regex no encuentra coincidencia) |
| Contenido con `<?...?>` en líneas posteriores | No tocado (`count=1` y ancla `^` a la primera línea) |

La declaración XML no afecta a la validez XSD ya comprobada en `super()`.

---

## Vistas modificadas

Ninguna. Este módulo no incluye ni hereda vistas, menús ni plantillas QWeb. Solo lógica Python sobre `account.payment.order`.

---

## Estructura de archivos

```
klo_sepa_pain_xml_declaration/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── account_payment_order.py     ← Override finalize_sepa_file_creation para normalizar la declaración XML
└── static/description/
    ├── icon.png
    └── Technical_context.md        ← Este fichero
```

Sin directorio `demo/`, sin `views/`, sin `data/`, sin `security/`.

---

## Instalación / Actualización

```bash
# Instalar
python odoo-bin -c /opt/odoo18_desarrollo/config/odoo.conf \
  -d klo_dev18 -i klo_sepa_pain_xml_declaration --stop-after-init

# Actualizar
python odoo-bin -c /opt/odoo18_desarrollo/config/odoo.conf \
  -d klo_dev18 -u klo_sepa_pain_xml_declaration --stop-after-init
```

> Instalación pendiente: este módulo se crea sin instalar en ninguna BD (lo hará otro agente).

---

## Posibles adaptaciones futuras

- **Hacer configurable el `standalone`:** añadir un `ir.config_parameter` (p. ej. `klo_sepa_pain.standalone`) para conmutar entre `standalone="no"` / `standalone="yes"` / sin `standalone` según el banco de cada compañía.
- **Parametrizar por diario o compañía:** si distintos bancos exigen cabeceras distintas, mover la constante a un campo en `account.journal` o `res.company` y leerlo en el override.
- **Cubrir otros formatos pain no OCA:** si aparecen generadores SEPA fuera de `account_banking_pain_base`, aplicar la misma normalización en sus métodos de generación.
