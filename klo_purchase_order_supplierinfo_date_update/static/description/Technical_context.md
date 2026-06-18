# Technical Context — `klo_purchase_order_supplierinfo_date_update`

## Módulo
| Campo | Valor |
|---|---|
| **Nombre técnico** | `klo_purchase_order_supplierinfo_date_update` |
| **Versión** | 18.0.1.0.0 |
| **Autor** | KLO Ingeniería Informática S.L.L. |
| **Licencia** | AGPL-3 |
| **Ubicación** | `/opt/odoo18_desarrollo/odoo/extra-addons/klo/extra/klo_purchase_order_supplierinfo_date_update/` |

---

## Descripción

Extiende la funcionalidad del módulo OCA `purchase_order_supplierinfo_update` añadiendo el campo **`purchase_date`** ("F. última compra") en el modelo `product.supplierinfo`.

Este campo almacena la **fecha de la última compra confirmada** del producto al proveedor, y se actualiza automáticamente cada vez que el módulo OCA actualiza el precio del proveedor (al confirmar un pedido de compra cuya línea es la más reciente para ese par producto/proveedor).

---

## Campo añadido: `purchase_date`

| Atributo | Valor |
|---|---|
| **Modelo** | `product.supplierinfo` |
| **Nombre técnico** | `purchase_date` |
| **Tipo** | `Date` |
| **String (etiqueta)** | `F. última compra` |
| **readonly** | `True` |
| **copy** | `False` |
| **Se actualiza** | Al confirmar un pedido de compra, cuando la línea es la más reciente para ese producto/proveedor |
| **Valor** | `purchase.order.date_order.date()` (fecha del pedido de compra confirmado) |

---

## Dependencias

| Módulo | Propósito |
|---|---|
| `purchase_order_supplierinfo_update` (OCA) | Provee el método `_update_supplierinfo(seller)` que este módulo extiende via `super()` |

El módulo OCA está en:
`/opt/odoo18_desarrollo/extra-addons/oca/purchase-workflow/purchase_order_supplierinfo_update/`

---

## Lógica de actualización

El método `_update_supplierinfo` del módulo OCA en `purchase.order.line` se ejecuta cuando:
1. Un pedido de compra pasa a estado `purchase` o `done`
2. Se crea o modifica una línea de pedido de compra con cambios en precio/descuento
3. La línea es la **más reciente** para ese par `(partner_id, product_id)` — verificado mediante:
   ```python
   domain = [
       ("partner_id", "=", line.partner_id.id),
       ("product_id", "=", line.product_id.id),
       ("date_order", ">", line.date_order),
   ]
   # Solo actualiza si no existe ningún pedido posterior
   ```

Nuestro override añade tras el `super()`:
```python
order_date = self.order_id.date_order
new_date = order_date.date() if order_date else fields.Date.today()
if seller.purchase_date != new_date:
    seller.sudo().purchase_date = new_date
```

---

## Vistas modificadas

### Lista de tarifas de proveedor (2 contextos con 1 sola herencia)

La columna `purchase_date` se añade **tras el campo `price`** con `optional="show"` (visible por defecto).

| Vista base heredada | Dónde se ve |
|---|---|
| `product.product_supplierinfo_tree_view` | Menú Compra › Config › Tarifas de proveedor **y** pestaña Compra del formulario de producto (la vista `purchase.product_supplierinfo_tree_view2` es `mode="primary"` y hereda los cambios del padre) |

> **Nota importante**: NO se hereda `purchase.product_supplierinfo_tree_view2` por separado porque, aunque tiene `mode="primary"`, Odoo propaga sobre ella los cambios aplicados a su vista padre. Heredarla también causaría que la columna apareciera duplicada.

### Formulario de tarifa de proveedor

El campo `purchase_date` ("Fecha última compra") se añade en el grupo **Pricelist**, antes del campo `date_start`, como campo `readonly`.

---

## Estructura de archivos

```
klo_purchase_order_supplierinfo_date_update/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── product_supplierinfo.py     ← Añade purchase_date a product.supplierinfo
│   └── purchase_order_line.py      ← Override _update_supplierinfo para escribir la fecha
├── views/
│   └── product_supplierinfo_views.xml
└── static/description/
    ├── icon.png
    └── Technical_context.md        ← Este fichero
```

---

## Instalación / Actualización

```bash
# Instalar
python odoo-bin -c /opt/odoo18_desarrollo/config/odoo.conf \
  -d ryp_dev -i klo_purchase_order_supplierinfo_date_update --stop-after-init

# Actualizar
python odoo-bin -c /opt/odoo18_desarrollo/config/odoo.conf \
  -d ryp_dev -u klo_purchase_order_supplierinfo_date_update --stop-after-init
```

---

## Posibles adaptaciones futuras

- **Rellenar datos históricos:** Para poblar `purchase_date` en registros existentes de `product.supplierinfo`, ejecutar un script que busque el pedido de compra más reciente confirmado por producto/proveedor y escriba la fecha.
- **Campo calculado vs almacenado:** Si se prefiere un enfoque siempre actualizado, `purchase_date` podría convertirse en un campo `compute` que busque en tiempo real la fecha del último pedido de compra confirmado para ese proveedor/producto. Sería más lento pero no dependería del módulo OCA para actualizarse.
- **Mostrar en líneas de pedido de compra:** Añadir la fecha de la tarifa vigente como columna informativa en `purchase.order.line` para que el comprador vea cuándo fue la última compra al confirmar un nuevo pedido.

