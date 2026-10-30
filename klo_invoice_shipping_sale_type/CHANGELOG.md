# Changelog - Invoice Shipping Sale Type

## [14.0.1.0.0] - 2026-03-09

### Añadido
- Nuevo campo computed `shipping_sale_type` en el modelo `account.move`
- Nueva columna "Tipo de pedido de venta" en la vista de lista de facturas
- Campo almacenado en base de datos (store=True) para permitir filtrado y agrupación
- Dependencia automática de partner_shipping_id.sale_type para actualización en tiempo real
- Traducciones al español
- Documentación completa (README, INSTALL, index.html)
- Archivo de seguridad con permisos de acceso

### Características técnicas
- Campo calculado con @api.depends para actualización automática
- Columna opcional (optional="hide") para no saturar la vista por defecto
- Validación con hasattr para evitar errores si el campo sale_type no existe
- Compatible con Odoo 14.0
- Licencia LGPL-3

### Dependencias
- account (Contabilidad)
- sale (Ventas)
- Campo personalizado sale_type en res.partner (debe existir previamente)

