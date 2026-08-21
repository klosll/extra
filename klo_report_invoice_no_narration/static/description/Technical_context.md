# KLO — Factura sin narración en el pie

## Identificación del módulo

| Campo | Valor |
|---|---|
| **Nombre técnico** | `klo_report_invoice_no_narration` |
| **Versión** | 18.0.0.1.0 |
| **Autor** | KLO Ingeniería Informática S.L.L. |
| **Licencia** | AGPL-3 |
| **Categoría** | Accounting/Accounting |
| **Dependencias** | `account` |
| **Ubicación** | `/opt/odoo18_desarrollo/odoo/extra-addons/klo/extra/klo_report_invoice_no_narration/` |

## Descripción funcional

Oculta por defecto la **narración** (`narration`) en el pie del informe de factura. La narración sí sigue visible como nota en presupuestos y pedidos de venta, pero no se imprime en la factura generada, evitando ruido en el documento fiscal.

## Campo(s) añadido(s) o lógica

No añade campos ni modelos Python (`models/__init__.py` está vacío). Toda la lógica es una herencia QWeb que reemplaza el `div` de comentario por un contenedor vacío.

## Dependencias

| Módulo | Propósito |
|---|---|
| `account` (Odoo core) | Provee la plantilla base `account.report_invoice_document` que contiene el `div[@name='comment']` con la narración. |

Sin módulos externos (OCA/terceros).

## Vistas modificadas

Plantilla heredada: `account.report_invoice_document` (id `klo_invoice_report_no_narration`).

| XPath | Posición | Cambio |
|---|---|---|
| `//div[@name='comment']` | `replace` | Sustituye el bloque de comentario por un `<div class="text-muted mb-3" t-attf-style="..." t-if="not is_html_empty(o.narration)" name="comment">` **vacío** (sin `t-field` ni contenido). El resultado es que la narración nunca se imprime, aunque el contenedor sigue existiendo para mantener la estructura. |

## Estructura de archivos

```
klo_report_invoice_no_narration/
├── __init__.py
├── __manifest__.py
├── models/
│   └── __init__.py          ← Vacío (sin modelos)
├── reports/
│   └── report_invoice.xml   ← Hereda account.report_invoice_document
└── static/description/
    ├── icon.png
    └── Technical_context.md
```

## Instalación / Actualización

```bash
# Instalar
python odoo-bin -c /opt/odoo18_desarrollo/config/odoo.conf \
  -d myv_dev -i klo_report_invoice_no_narration --stop-after-init

# Actualizar
python odoo-bin -c /opt/odoo18_desarrollo/config/odoo.conf \
  -d myv_dev -u klo_report_invoice_no_narration --stop-after-init
```

## Posibles adaptaciones futuras

- Convertir el ocultamiento en una opción configurable por compañía o por diario, en lugar de aplicarlo siempre.
- Reutilizar el patrón para ocultar otros bloques del informe (p. ej. `origin`, totales específicos) en un único módulo de personalización de factura.
- Permitir mostrar la narración solo en facturas rectificativas (`out_refund`) manteniéndola oculta en facturas normales.
