# Tecnical_document.md — klo_account_move_facturae_status

## Descripción general

Módulo de adaptación KLO para **Odoo 18 Community** que añade un indicador visual en la lista de facturas mostrando si se ha generado el archivo Facturae XML mediante la acción **"Crear archivo de Facturae"** del módulo oficial `l10n_es_edi_facturae`.

---

## Ubicación

```
/opt/odoo18_desarrollo/odoo/extra-addons/klo/extra/klo_account_move_facturae_status/
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
| `l10n_es_edi_facturae` | Proporciona el campo `l10n_es_edi_facturae_xml_file` |

---

## Modelo: `account.move` (account_move.py)

### Campo añadido

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `is_facturae_generated` | `Boolean` | `True` si existe archivo Facturae generado |

### Lógica de cálculo

```python
@api.depends('l10n_es_edi_facturae_xml_file')
def _compute_is_facturae_generated(self):
    for move in self:
        move.is_facturae_generated = bool(move.l10n_es_edi_facturae_xml_file)
```

- **`store=True`**: El valor se almacena en base de datos para permitir filtrado y búsqueda eficiente.
- **`copy=False`**: No se copia al duplicar la factura.
- Se recomputa automáticamente cuando cambia `l10n_es_edi_facturae_xml_file`.

---

## Vista: `account_move_view.xml`

Hereda de `account.view_invoice_tree` (vista de lista de facturas).

### Columna añadida

- **Posición**: Después del campo `move_sent_values` (columna "Enviado")
- **Widget**: `boolean_toggle` (interruptor visual, solo lectura)
- **Opcional**: `optional="show"` → visible por defecto, el usuario puede ocultarla
- **Etiqueta**: "Facturae"

---

## Campo fuente en `l10n_es_edi_facturae`

En `/opt/odoo18_desarrollo/odoo/addons/l10n_es_edi_facturae/models/account_move.py`:

```python
l10n_es_edi_facturae_xml_file = fields.Binary(
    attachment=True, string="Facturae File", copy=False,
)
l10n_es_edi_facturae_xml_id = fields.Many2one(
    comodel_name='ir.attachment',
    string="Facturae Attachment",
    compute=lambda self: self._compute_linked_attachment_id(
        'l10n_es_edi_facturae_xml_id', 'l10n_es_edi_facturae_xml_file'),
    depends=['l10n_es_edi_facturae_xml_file']
)
```

El archivo Facturae se genera mediante la acción **"Crear archivo de Facturae"** en el formulario de factura.

---

## Comando de instalación/actualización

```bash
/home/manolo/.local/bin/uv run /opt/odoo18_desarrollo/uv/.venv/bin/python3 \
  /opt/odoo18_desarrollo/odoo/odoo-bin \
  -c /opt/odoo18_desarrollo/config/odoo.conf \
  -d ryp_dev \
  -i klo_account_move_facturae_status \
  --stop-after-init --no-http
```

---

## Notas para futuras adaptaciones

- Si se necesita mostrar la fecha de generación, se puede acceder al adjunto via `l10n_es_edi_facturae_xml_id.create_date`.
- Si se quiere añadir un botón de descarga directo en la lista, usar el widget `binary` apuntando a `l10n_es_edi_facturae_xml_file`.
- El campo `is_facturae_generated` puede usarse en filtros y agrupaciones de la vista lista.
- Para mostrar el estado también en facturas de proveedor, verificar que `context.get('default_move_type')` incluye `in_invoice`.

---

## Historial de versiones

| Versión | Fecha | Descripción |
|---------|-------|-------------|
| 18.0.1.0.0 | 2026-05-18 | Creación inicial del módulo |

---

*Documento generado por IA — KLO Development Team*

