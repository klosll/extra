# Technical Context — klo_purchase_order_confirmed_supplierinfo

## Módulo

| Campo      | Valor                                                                                  |
|------------|----------------------------------------------------------------------------------------|
| Nombre     | KLO - Actualizar proveedores al añadir líneas en pedido confirmado                     |
| Versión    | 18.0.1.0.0                                                                             |
| Autor      | KLO Ingeniería Informática S.L.L.                                                      |
| Licencia   | AGPL-3.0 or later                                                                      |
| Ruta       | extra-addons/klo/extra/klo_purchase_order_confirmed_supplierinfo/                      |

## Descripción

Cuando se añade una línea de producto nueva a un pedido de compra ya **confirmado**
(estado `purchase` o `done`), Odoo nativo no actualiza la ficha del producto con los
datos del proveedor porque `_add_supplier_to_product()` sólo se llama durante
`button_confirm`, que únicamente procesa pedidos en estado `draft`/`sent`.

Este módulo extiende `purchase.order.line` para que, al crear una nueva línea sobre un
pedido confirmado, se ejecute la misma lógica de registro del proveedor en la ficha del
producto (`seller_ids`) que ocurre durante la confirmación de un pedido en borrador.

## Campo(s) añadido(s)

No añade campos nuevos. Actúa exclusivamente sobre `product.supplierinfo` (`seller_ids`
de `product.template`) a través de la lógica ya existente en `purchase.order`.

## Dependencias

- `purchase` (Odoo core)

Compatible y complementario con `purchase_order_supplierinfo_update` (OCA):
- OCA actualiza precios/descuentos de **sellers existentes** al crear/editar líneas.
- Este módulo **crea** el seller si el proveedor todavía no estaba registrado en el producto.

## Lógica

### `PurchaseOrderLine.create()` (override)

Después de llamar a `super().create()`, filtra las líneas recién creadas cuyo pedido
esté en estado `purchase` o `done` y que tengan producto asignado, y llama a
`_add_supplier_to_product()` para cada una.

### `PurchaseOrderLine._add_supplier_to_product()`

Método nuevo a nivel de línea. Replica la lógica de
`purchase.order._add_supplier_to_product()` (Odoo core) pero acotada a `self`:

1. Determina el partner proveedor (usa empresa padre si el partner es una dirección de contacto).
2. Comprueba si el proveedor ya está en `seller_ids` del producto (`already_seller`).
3. Si no está y el producto tiene ≤ 10 proveedores:
   - Calcula el precio convertido a la UoM de compra del producto.
   - Llama a `order._prepare_supplier_info()` para construir el dict de datos.
   - Si existe un seller coincidente, copia `product_name` y `product_code`.
   - Escribe el nuevo `supplierinfo` en la plantilla del producto con `sudo()`.

## Vistas modificadas

Ninguna.

## Estructura de archivos

```
klo_purchase_order_confirmed_supplierinfo/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── purchase_order_line.py
└── static/
    └── description/
        ├── icon.png
        └── Technical_context.md
```

## Instalación / Actualización

```bash
# Instalación inicial
python odoo-bin -c /opt/odoo18_desarrollo/config/odoo.conf \
    -d ryp_dev -i klo_purchase_order_confirmed_supplierinfo --stop-after-init

# Actualización
python odoo-bin -c /opt/odoo18_desarrollo/config/odoo.conf \
    -d ryp_dev -u klo_purchase_order_confirmed_supplierinfo --stop-after-init
```

## Posibles adaptaciones futuras

- **Actualización en `write`**: Si se cambia el `product_id` de una línea existente en
  un pedido confirmado, también podría ejecutarse `_add_supplier_to_product()`. Actualmente
  sólo se dispara en `create`.
- **Integración con OCA discount**: Si se usa `purchase_triple_discount`, ampliar
  `_prepare_supplier_info` para incluir `discount1`, `discount2`, `discount3`.
- **Control por configuración**: Añadir un checkbox en `res.config.settings` para
  activar/desactivar este comportamiento sin desinstalar el módulo.
