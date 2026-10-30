# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "KLO - Custom Sale Order Report Columns RYP",
    "version": "18.0.3.0.0",
    "summary": (
        "Columnas personalizadas de los informes de pedido, factura y albarán de "
        "entrega para RYP: cabeceras Precio U y columna Neto con los mismos "
        "decimales que el formulario (precisión Product Price) e Importe = subtotal "
        "del documento (price_subtotal), que cuadra exactamente con base/IVA/total. "
        "En el albarán se oculta la columna Taxes, se renombra Subtotal a Importe y "
        "se separan 1 mm las columnas numéricas (padding-left)"
    ),
    "description": """
Personalización de las columnas de la tabla de líneas de los informes PDF de pedido de
venta (sale.report_saleorder_document), factura (account.report_invoice_document) y
albarán de entrega (stock.report_delivery_document) para el cliente RYP:

* Cambia la cabecera de la columna de precio unitario a "Precio U" en pedido,
  factura y albarán de entrega.
* Añade una nueva columna "Neto" (precio unitario sin impuestos con el descuento
  aplicado) antes de "Importe" en los tres documentos. "Precio U" y "Neto" se
  renderizan con t-field usando los mismos decimales que el campo "Precio unitario"
  del formulario (precisión decimal "Product Price", sin redondeo del valor).
* Sustituye el valor de la columna "Importe": muestra siempre el subtotal del
  documento (price_subtotal), que cuadra exactamente con base/IVA/total (la
  multiplicación manual Cantidad × Neto puede diferir ±0,01 € en líneas con
  impuestos precio incluido). Precio U y Neto no cambian: Neto mantiene la
  fórmula Precio × (1 − Dto/100) y ambos se muestran con los decimales del
  formulario.
* En el albarán de entrega valora las columnas aportadas por
  stock_picking_report_valued: la cabecera "Subtotal" pasa a llamarse "Importe",
  la columna "Taxes" se oculta y se añade una columna "Neto" entre "Discount" e
  "Importe". El Importe del albarán conserva el subtotal de Odoo
  (sale_price_subtotal), que cuadra con el "Untaxed Amount" del pie.
* Separa 1 mm las columnas numéricas del cuerpo (padding-left en th/td de la
  tabla de líneas, pedido, factura y albarán) para que los datos no se mezclen
  visualmente.

Añade el campo computado price_unit_net en sale.order.line, account.move.line y
stock.move.line: Neto = price_unit_untaxed x (1 - descuento/100), definido con
min_display_digits 'Product Price' (sin digits) para mimetizar el campo price_unit del
core. Reutiliza price_unit_untaxed en sale.order.line (aportado por
klo_sale_order_price_unit_untaxed), en account.move.line (aportado por
klo_invoice_report_price_unit_untaxed) y en stock.move.line (aportado por
klo_stock_picking_report_price_unit_untaxed). La dependencia
klo_report_saleorder_no_taxes_column aporta el ocultado de la columna "Impuestos"
(th_taxes/td_taxes) del pedido; sus xpaths no interfieren con los de este módulo. En
la factura, el span original del subtotal no se elimina (es ancla de herencias de
terceros): se oculta con style y se añade el nuevo importe, respetando la agrupación
por albarán de account_invoice_report_grouped_by_picking.
""",
    "license": "AGPL-3",
    "author": "KLO Ingenieria Informatica S.L.L.",
    "website": "https://www.klo.es",
    "category": "Sales/Sales",
    "depends": [
        "sale",
        "klo_sale_order_price_unit_untaxed",
        "klo_report_saleorder_no_taxes_column",
        "klo_invoice_report_price_unit_untaxed",
        "stock_picking_report_valued",
        "klo_stock_picking_report_price_unit_untaxed",
    ],
    "data": [
        "report/sale_order_report_templates.xml",
        "report/account_report_templates.xml",
        "report/stock_picking_report_templates.xml",
    ],
    "installable": True,
    "auto_install": False,
}
