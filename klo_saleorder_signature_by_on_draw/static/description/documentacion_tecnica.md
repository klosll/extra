# Documentación Técnica — klo_saleorder_signature_by_on_draw

## Información general

| Campo | Valor |
|---|---|
| **Nombre técnico** | `klo_saleorder_signature_by_on_draw` |
| **Versión** | 14.0.1.0.0 |
| **Módulo base** | `sale` |
| **Ubicación** | `/opt/odoo14_paasa/odoo/extra-addons/extra/klo_saleorder_signature_by_on_draw/` |
| **Autor** | KLO |
| **Fecha creación** | 2026-05-19 |

---

## Objetivo

Mostrar los campos `signed_by` y `signed_on` **encima** del widget de firma `customer_signature` dentro de la página **Customer Signature** del formulario de Pedido de venta (`sale.order`), alineados a la izquierda.

Los campos **no se eliminan** de su posición original (columna derecha del grupo). Simplemente se duplica su visualización encima del widget de firma.

---

## Estructura del módulo

```
klo_saleorder_signature_by_on_draw/
├── __init__.py
├── __manifest__.py
├── views/
│   └── sale_order_views.xml       ← herencia de vista
└── static/description/
    └── documentacion_tecnica.md   ← este fichero
```

---

## Herencia de vista

### Vista heredada
- **External ID:** `sale.view_order_form`
- **Modelo:** `sale.order`

### Cambio aplicado

Se usa un `xpath` apuntando al campo `customer_signature` dentro de la página `customer_signature` para insertar **antes** de él un bloque `div` con:

- Etiqueta + campo `signed_by` (readonly, alineado a la izquierda)
- Etiqueta + campo `signed_on` (readonly, alineado a la izquierda)

El bloque usa estilos CSS inline (`display: flex; flex-direction: column; align-items: flex-start`) para garantizar la alineación a la izquierda independientemente del tema de Odoo.

---

## Campos implicados

| Campo | Modelo | Tipo | Descripción |
|---|---|---|---|
| `signed_by` | `sale.order` | Char | Nombre de quien firmó el pedido |
| `signed_on` | `sale.order` | Datetime | Fecha y hora de la firma |
| `customer_signature` | `sale.order` | Binary | Imagen de la firma dibujada (widget `signature`) |

---

## Instalación

1. Copiar el módulo en `/opt/odoo14_paasa/odoo/extra-addons/extra/`
2. Reiniciar el servicio Odoo
3. Ir a **Aplicaciones** → Actualizar lista
4. Buscar `KLO Sale Order - Firma` e instalar

---

## Notas de mantenimiento

- Los campos `signed_by` y `signed_on` son **readonly** en el bloque añadido ya que son rellenados automáticamente por Odoo al firmar.
- Si en el futuro se cambia el external ID de la vista base (`sale.view_order_form`), actualizar el `inherit_id` en `views/sale_order_views.xml`.
- Si se desinstala el módulo base `sale`, este módulo también debe desinstalarse.

