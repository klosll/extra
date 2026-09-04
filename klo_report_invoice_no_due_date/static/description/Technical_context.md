# KLO — Factura sin origen en la cabecera

## Identificación del módulo

| Campo | Valor |
|---|---|
| **Nombre técnico** | `klo_report_invoice_no_origin_source` |
| **Versión** | 18.0.0.1.0 |
| **Autor** | KLO Ingeniería Informática S.L.L. |
| **Licencia** | AGPL-3 |
| **Categoría** | Accounting/Accounting |
| **Dependencias** | `account` |
| **Ubicación** | `/opt/odoo18_desarrollo/odoo/extra-addons/klo/extra/klo_report_invoice_no_origin_source/` |

## Descripción funcional

Oculta por defecto la lista de **origen** (pedidos de venta que generaron la factura) en la cabecera del informe de factura. Así no se imprime la relación de órdenes de venta que se han facturado, manteniendo la cabecera más limpia.

## Campo(s) añadido(s) o lógica

No añade campos ni modelos Python (`models/__init__.py` está vacío). Toda la lógica es una herencia QWeb que fuerza a `False` la condición de visibilidad del `div` de origen.

## Dependencias

| Módulo | Propósito |
|---|---|
| `account` (Odoo core) | Provee la plantilla base `account.report_invoice_document` que contiene el `div[@name='origin']`. |

Sin módulos externos (OCA/terceros).

## Vistas modificadas

Plantilla heredada: `account.report_invoice_document` (id `klo_invoice_report_document_no_origin`).

| XPath | Posición | Cambio |
|---|---|---|
| `//div[@name='origin']` | `attributes` | Añade el atributo `t-if="False"`, de modo que el bloque de origen nunca se renderiza (su contenido queda siempre oculto). |

## Estructura de archivos

```
klo_report_invoice_no_origin_source/
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
  -d myv_dev -i klo_report_invoice_no_origin_source --stop-after-init

# Actualizar
python odoo-bin -c /opt/odoo18_desarrollo/config/odoo.conf \
  -d myv_dev -u klo_report_invoice_no_origin_source --stop-after-init
```

## Posibles adaptaciones futuras

- Hacer el ocultamiento configurable por compañía o por diario en lugar de aplicarlo de forma global.
- Sustituir el `t-if="False"` por una condición basada en un campo funcional (p. ej. `o.company_id.show_invoice_origin`) para permitir mostrar el origen en empresas concretas.
- Unificar este módulo con `klo_report_invoice_no_narration` en un único módulo de "limpieza de cabecera/pie" de factura.
