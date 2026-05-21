# Tecnical_document.md — klo_account_move_facturae_status (Odoo 15)

## Descripción general

Módulo de adaptación KLO para **Odoo 15 Community** que añade un indicador visual en la lista de facturas mostrando si se ha generado el archivo Facturae XML mediante la acción **"Crear archivo de Facturae"** del módulo OCA `l10n_es_facturae`.

Es el **downgrade a Odoo 15** del módulo `klo_account_move_facturae_status` originalmente desarrollado para Odoo 18. La diferencia técnica principal es que en Odoo 15 el archivo Facturae se almacena en un One2many (`l10n_es_facturae_attachment_ids`) mientras que en Odoo 18 existe un campo binario directo (`l10n_es_edi_facturae_xml_file`).

---

## Ubicación

```
/opt/odoo15_klo/odoo/extra-addons/klo/extra/klo_account_move_facturae_status/
```

---

## Estructura del módulo

```
klo_account_move_facturae_status/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── account_move.py
├── views/
│   └── account_move_view.xml
└── static/
    └── description/
        ├── icon.png
        └── Tecnical_document.md
```

---

## Dependencias

| Módulo | Razón |
|--------|-------|
| `account` | Modelo base `account.move` |
| `l10n_es_facturae` | OCA — proporciona `l10n_es_facturae_attachment_ids` y la pestaña Facturae en el formulario |

> **Nota**: En Odoo 15 el módulo oficial de Odoo 18 `l10n_es_edi_facturae` no existe. El equivalente funcional es el módulo OCA `l10n_es_facturae` ubicado en `/opt/odoo15_klo/extra-addons/oca/l10n-spain/l10n_es_facturae/`.

---

## Modelo: `account.move` (account_move.py)

### Campo añadido

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `is_facturae_generated` | `Boolean` | `True` si existe al menos un adjunto Facturae generado |

### Lógica de cálculo

```python
@api.depends("l10n_es_facturae_attachment_ids")
def _compute_is_facturae_generated(self):
    for move in self:
        move.is_facturae_generated = bool(move.l10n_es_facturae_attachment_ids)
```

- **`store=True`**: El valor se almacena en base de datos para permitir filtrado y búsqueda eficiente.
- **`copy=False`**: No se copia al duplicar la factura.
- Se recomputa automáticamente cuando cambia `l10n_es_facturae_attachment_ids`.
- Al instalar el módulo, Odoo recalcula el valor para todos los `account.move` existentes en la BD.

---

## Campo fuente en `l10n_es_facturae` (OCA v15)

En `/opt/odoo15_klo/extra-addons/oca/l10n-spain/l10n_es_facturae/models/account_move.py`:

```python
l10n_es_facturae_attachment_ids = fields.One2many(
    comodel_name="account.move.facturae",
    inverse_name="move_id",
    string="Facturae Attachments",
)
```

El modelo `account.move.facturae` tiene:
- `move_id` — Many2one a `account.move`
- `file` — Binary (el XML generado)
- `filename` — Char (nombre del fichero)

El archivo Facturae se genera mediante la acción **"Crear archivo de Facturae"** en el formulario de factura.

---

## Vista: `account_move_view.xml`

### 1. Vista lista — columna opcional

Hereda de `account.view_invoice_tree` (vista de lista de facturas de Odoo 15).

- **Posición**: Después del campo `state` (último campo del tree en Odoo 15; `move_sent_values` de Odoo 18 no existe en v15)
- **Widget**: `boolean_toggle` (interruptor visual, solo lectura)
- **Opcional**: `optional="show"` → visible por defecto, el usuario puede ocultarla
- **Etiqueta**: "Facturae"

### 2. Vista formulario — campo en pestaña Facturae

Hereda de `l10n_es_facturae.view_move_form` (que a su vez hereda de `l10n_es_aeat.view_move_form`).

- **Posición**: Después del campo `facturae_file_reference`, dentro de la pestaña "Facturae"
- El campo es editable (`readonly="0"`) para permitir correcciones manuales si fuera necesario
- La pestaña "Facturae" sólo es visible cuando `facturae = True` (campo calculado del módulo OCA)

---

## Diferencias entre versión Odoo 15 y Odoo 18

| Aspecto | Odoo 18 | Odoo 15 |
|---------|---------|---------|
| Módulo proveedor | `l10n_es_edi_facturae` (oficial Odoo) | `l10n_es_facturae` (OCA) |
| Campo fuente | `l10n_es_edi_facturae_xml_file` (Binary) | `l10n_es_facturae_attachment_ids` (One2many) |
| Detección de generación | `bool(move.l10n_es_edi_facturae_xml_file)` | `bool(move.l10n_es_facturae_attachment_ids)` |
| Ancla en vista lista | `move_sent_values` | `state` |
| Ancla en vista formulario | `l10n_es_payment_means` | `facturae_file_reference` |
| Vista formulario hereda de | `l10n_es_edi_facturae.view_move_form` | `l10n_es_facturae.view_move_form` |
| Licencia | `LGPL-3` | `AGPL-3` (convenio KLO) |

---

## Comando de instalación/actualización

```bash
# Instalar por primera vez
python /opt/odoo15_klo/odoo/odoo-bin \
  -c /opt/odoo15_klo/odoo/config/odoo15.conf \
  -i klo_account_move_facturae_status \
  --stop-after-init

# Actualizar tras cambios
python /opt/odoo15_klo/odoo/odoo-bin \
  -c /opt/odoo15_klo/odoo/config/odoo15.conf \
  -u klo_account_move_facturae_status \
  --stop-after-init
```

---

## Notas para futuras adaptaciones

- Si se necesita mostrar la fecha de generación, se puede acceder al adjunto vía `l10n_es_facturae_attachment_ids[0].create_date` (el campo `file` es binario sin fecha propia, pero el registro `account.move.facturae` tiene `create_date` de ORM).
- Si se quiere permitir descarga directa en lista, añadir un campo `related` que apunte al primer `file` del One2many.
- El campo `is_facturae_generated` puede usarse en filtros y agrupaciones de la vista lista.
- Si en el futuro se migra a Odoo 16/17/18, revisar si OCA mantiene `l10n_es_facturae` o si el módulo oficial `l10n_es_edi_facturae` ya está disponible, y adaptar el campo fuente del `@api.depends`.
- Para mostrar el estado también en facturas de proveedor, verificar que el contexto incluye `in_invoice`.

---

## Historial de versiones

| Versión | Fecha | Descripción |
|---------|-------|-------------|
| 15.0.1.0.0 | 2026-05-21 | Creación inicial — downgrade desde módulo Odoo 18 |

---

*Documento generado por IA — KLO Development Team*

