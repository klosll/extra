# Tecnical_document.md — klo_po_supplierinfo_triple_discount

## Descripción general

Módulo de extensión que integra `purchase_order_supplierinfo_update` (OCA) con `purchase_triple_discount` (OCA) para que al confirmar un pedido de compra se actualicen **todos** los campos de descuento del proveedor (`discount1`, `discount2`, `discount3`) en `product.supplierinfo`, además del precio unitario.

---

## Datos técnicos

| Campo | Valor |
|---|---|
| **Nombre técnico** | `klo_po_supplierinfo_triple_discount` |
| **Versión** | 18.0.1.0.0 |
| **Autor** | KLO |
| **Licencia** | LGPL-3 |
| **Ubicación** | `/opt/odoo18_desarrollo/odoo/extra-addons/klo/extra/klo_po_supplierinfo_triple_discount/` |
| **Categoría** | Purchase |

---

## Dependencias

| Módulo | Tipo | Descripción |
|---|---|---|
| `purchase_order_supplierinfo_update` | OCA (purchase-workflow) | Actualiza precio y descuento final al confirmar PO |
| `purchase_triple_discount` | OCA (purchase-workflow) | Añade `discount1`, `discount2`, `discount3` a `purchase.order.line` y `product.supplierinfo` |

---

## Problema que resuelve

### Comportamiento estándar de Odoo 18
`button_confirm()` → `_add_supplier_to_product()` **solo crea** un nuevo `product.supplierinfo` si el proveedor no existe en la lista del producto. **No actualiza** registros existentes.

### Comportamiento de `purchase_order_supplierinfo_update`
Al confirmar el PO, llama a `update_supplierinfo_price()` → `_update_supplierinfo(seller)` que actualiza **únicamente**:
- `price` (precio unitario, con conversión de divisa y UoM)
- `discount` (descuento final calculado, campo único)

**NO actualiza** `discount1`, `discount2`, `discount3`.

### Lo que añade este módulo
Extiende `_update_supplierinfo` para que **también actualice** `discount1`, `discount2` y `discount3` del registro `product.supplierinfo` encontrado.

---

## Lógica de funcionamiento

### Disparadores de actualización
La actualización se produce en los siguientes casos:

1. **Al confirmar el PO** (heredado del módulo base OCA):
   - `PurchaseOrder.write({'state': 'purchase'/'done'})` → `update_supplierinfo_price()`

2. **Al modificar descuentos en una línea de PO confirmado** (añadido por este módulo):
   - `PurchaseOrderLine.write({'discount1': ..., 'discount2': ..., 'discount3': ...})` → `update_supplierinfo_price()`

3. **Al crear líneas en un PO ya confirmado** (heredado del módulo base OCA):
   - `PurchaseOrderLine.create(...)` → `update_supplierinfo_price()`

### Condición de seguridad (heredada del módulo base OCA)
Solo se actualiza el `product.supplierinfo` si **no existe un pedido de compra más reciente** para el mismo proveedor+producto. Esto evita sobreescribir datos con precios/descuentos de un PO más antiguo.

```python
domain = [
    ("partner_id", "=", line.partner_id.id),
    ("product_id", "=", line.product_id.id),
    ("date_order", ">", line.date_order),
]
if not self.env["purchase.order.line"].search_count(domain, limit=1):
    # → Actualiza
```

---

## Archivos del módulo

```
klo_po_supplierinfo_triple_discount/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── purchase_order_line.py      ← Lógica principal
└── static/
    └── description/
        ├── icon.png                ← Logo KLO
        └── Tecnical_document.md   ← Este documento
```

---

## Modelo afectado: `purchase.order.line`

### Método `write` extendido
```python
def write(self, vals):
    res = super().write(vals)
    triple_discount_fields = {"discount1", "discount2", "discount3"}
    if triple_discount_fields & set(vals.keys()):
        self.update_supplierinfo_price()
    return res
```
Añade el trigger para cambios en `discount1/2/3` en líneas de PO ya confirmados.

### Método `_update_supplierinfo` extendido
```python
def _update_supplierinfo(self, seller):
    super()._update_supplierinfo(seller)   # Actualiza price y discount
    updates = {}
    if self.discount1 != seller.discount1:
        updates["discount1"] = self.discount1
    if self.discount2 != seller.discount2:
        updates["discount2"] = self.discount2
    if self.discount3 != seller.discount3:
        updates["discount3"] = self.discount3
    if updates:
        seller.sudo().write(updates)       # Actualiza discount1/2/3
```

---

## Campos actualizados en `product.supplierinfo` al confirmar PO

| Campo | Módulo responsable | Descripción |
|---|---|---|
| `price` | `purchase_order_supplierinfo_update` | Precio unitario (con conv. divisa/UoM) |
| `discount` | `purchase_order_supplierinfo_update` | Descuento final calculado |
| `discount1` | **este módulo** | Descuento 1 (%) |
| `discount2` | **este módulo** | Descuento 2 (%) |
| `discount3` | **este módulo** | Descuento 3 (%) |

---

## Notas para futuros ajustes

- Si se añaden más campos de descuento al mixin `purchase.triple.discount.mixin`, se deberá actualizar el método `_update_supplierinfo` de este módulo.
- Alternativa más dinámica: usar `self._get_multiple_discount_field_names()` en lugar de hardcodear los tres campos, lo que permitiría escalabilidad automática.
- El campo `min_qty` **no se actualiza** (ni por el módulo base ni por este). Si se necesita, habría que extender `_update_supplierinfo` y `_prepare_supplier_info`.

