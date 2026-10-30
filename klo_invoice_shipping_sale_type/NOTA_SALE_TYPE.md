# NOTA IMPORTANTE - Campo sale_type en res.partner

## ⚠️ REQUISITO PREVIO

Este módulo requiere que el modelo `res.partner` tenga un campo llamado `sale_type`.

## Verificar si el campo existe

Para verificar si el campo `sale_type` existe en tu instalación de Odoo:

1. Ir a **Ajustes > Técnico > Modelos**
2. Buscar el modelo: `res.partner`
3. Ir a la pestaña **Campos**
4. Buscar el campo: `sale_type`

## Si el campo NO existe

Si el campo `sale_type` no existe, tienes dos opciones:

### Opción 1: Crear el campo manualmente (Recomendado)

Crear un módulo que agregue el campo `sale_type` a `res.partner`:

```python
# models/res_partner.py
from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    sale_type = fields.Char(
        string='Sale Type',
        help='Type of sale for this partner'
    )
```

O si prefieres un campo de selección:

```python
sale_type = fields.Selection([
        ('retail', 'Retail'),
        ('wholesale', 'Wholesale'),
        ('online', 'Online'),
        ('distributor', 'Distributor'),
    ],
    string='Sale Type',
    help='Type of sale for this partner'
)
```

### Opción 2: El módulo funcionará sin errores

El módulo está diseñado con `hasattr()` para verificar si el campo existe.
Si no existe, simplemente el campo `shipping_sale_type` quedará vacío (False).

## Comportamiento del módulo

### Si sale_type EXISTE:
- ✅ El campo `shipping_sale_type` se actualizará con el valor de `partner_shipping_id.sale_type`
- ✅ Podrás filtrar y agrupar por tipo de pedido de venta
- ✅ Verás los valores en la lista de facturas

### Si sale_type NO EXISTE:
- ⚠️ El campo `shipping_sale_type` estará siempre vacío
- ⚠️ No habrá errores, pero no verás ningún valor
- ⚠️ El filtrado y agrupación mostrarán valores vacíos

## Recomendación

Se recomienda crear el campo `sale_type` en `res.partner` antes de instalar
este módulo para aprovechar toda su funcionalidad.

## Ejemplo de módulo para crear sale_type

Si necesitas crear el campo, aquí tienes un ejemplo de módulo básico:

### Estructura:
```
klo_partner_sale_type/
├── __init__.py
├── __manifest__.py
└── models/
    ├── __init__.py
    └── res_partner.py
```

### __manifest__.py:
```python
{
    'name': 'Partner Sale Type',
    'version': '14.0.1.0.0',
    'depends': ['base', 'sale'],
    'data': [],
    'installable': True,
}
```

### models/res_partner.py:
```python
from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    sale_type = fields.Selection([
        ('retail', 'Minorista'),
        ('wholesale', 'Mayorista'),
        ('online', 'Online'),
        ('distributor', 'Distribuidor'),
    ], string='Tipo de Venta')
```

Instala este módulo ANTES de instalar klo_invoice_shipping_category.

