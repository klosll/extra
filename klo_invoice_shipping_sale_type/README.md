# Invoice Shipping Sale Type

## Descripción

Este módulo agrega una nueva columna en la vista de lista de Facturas de Venta que muestra el tipo de pedido de venta de la dirección de entrega del cliente.

## Características

- **Nueva columna**: "Tipo de pedido de venta" en la vista de árbol de facturas
- **Campo computed**: `shipping_sale_type` que obtiene el valor desde `partner_shipping_id.sale_type`
- **Campo almacenado**: Permite agrupar y filtrar por este campo
- **Columna opcional**: La columna está oculta por defecto pero puede activarse desde la vista

## Instalación

1. Copiar el módulo en la carpeta de addons
2. Actualizar la lista de aplicaciones
3. Instalar el módulo "Invoice Shipping Sale Type"

## Uso

Una vez instalado el módulo:
1. Ir a Contabilidad > Clientes > Facturas
2. En la vista de lista, haga clic en el icono de columnas opcionales
3. Active la columna "Tipo de pedido de venta"
4. La columna mostrará el tipo de pedido de venta asociado a la dirección de entrega de cada factura

## Funcionalidades

- **Filtrar**: Puede filtrar las facturas por el tipo de pedido de venta
- **Agrupar**: Puede agrupar las facturas por el tipo de pedido de venta
- **Buscar**: El campo está almacenado en la base de datos para búsquedas eficientes

## Dependencias

- account
- sale

## Versión

14.0.1.0.0

## Autor

Manuel Calomarde Gómez - KLO Ingeniería Informática S.L.L.

## Licencia

LGPL-3

