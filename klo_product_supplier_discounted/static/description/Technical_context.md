# Technical Document — klo_product_supplier_discounted

## Información general

| Campo | Valor |
|---|---|
| **Nombre técnico** | `klo_product_supplier_discounted` |
| **Versión** | 18.0.1.0.0 |
| **Autor** | KLO Ingeniería Informática S.L.L. |
| **Licencia** | AGPL-3 |
| **Categoría** | Purchase |
| **Dependencias** | `purchase_triple_discount` (OCA purchase-workflow) |

## Descripción

Añade el campo calculado **`discounted_price`** ("Precio con dto.") al modelo `product.supplierinfo`.

El campo muestra el precio de compra (`price`) tras aplicar los tres descuentos encadenados (`discount1`, `discount2`, `discount3`) definidos por el módulo OCA `purchase_triple_discount`.

## Lógica de cálculo

Se replica exactamente el método `_get_aggregated_multiple_discounts` del mixin OCA:

```
discounted_price = price × (1 - discount1/100) × (1 - discount2/100) × (1 - discount3/100)
```

Ejemplo: precio=100, discount1=10, discount2=5, discount3=2  
→ 100 × 0.90 × 0.95 × 0.98 = **83,79**

## Ficheros

```
klo_product_supplier_discounted/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── product_supplierinfo.py      ← campo discounted_price
├── views/
│   └── product_supplierinfo_view.xml ← columna en pestaña Compra del producto
└── static/description/
    ├── icon.png
    └── Tecnical_document.md
```

## Modelo afectado

**`product.supplierinfo`**

| Campo nuevo | Tipo | Almacenado | Descripción |
|---|---|---|---|
| `discounted_price` | Float (`Product Price`) | Sí (store=True) | Precio tras aplicar discount1, discount2, discount3 |

### Dependencias del campo computed
`price`, `discount1`, `discount2`, `discount3`

## Vista modificada

- `product.product_supplierinfo_tree_view` (ref: `product.product_supplierinfo_tree_view`)
- Se añade la columna **"Precio con dto."** con `optional="show"` (visible por defecto) **a la izquierda** de `currency_id`.

## Notas para futuros ajustes

- Si se añaden más descuentos al mixin OCA, hay que actualizar el `@api.depends` y la lista `discounts` en `_compute_discounted_price`.
- El campo es `store=True`, por lo que se puede usar en filtros, vistas pivot, etc.
- Si se necesita mostrar también en el formulario de `product.supplierinfo` (vista `product.product_supplierinfo_form_view`), añadir un nuevo `<record>` en `views/product_supplierinfo_view.xml` heredando esa vista.
- La vista tree de supplierinfo se usa embebida en la pestaña **Compra** del formulario de producto (`product.template`).

